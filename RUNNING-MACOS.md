# Running Tekken 3 Recompiled on macOS

This is the short path from a clean clone to the game running on a Mac. It
covers the **base game only**, with no Jun and no other guest character. The
Easy Setup launcher and the `.cmd` files in this repository are Windows-only
and are not used here.

Tested on macOS 15.7.9, Intel Mac, Apple clang 17. Apple Silicon is untested.

Every step below was run from a fresh clone. `PORTING.md` explains *why* each
workaround is needed; this file only tells you what to type.

---

## 1. Prerequisites

```bash
xcode-select --install
brew install cmake ninja sdl3
```

The README's build commands say `python`. macOS has no `python`, only
`python3`, so use `python3` everywhere below.

You also need a working network connection for the first build, as CMake
fetches `libchdr` while configuring.

Versions used for the tested run: cmake 4.4.3, ninja 1.13.2, SDL3 3.4.16,
Python 3.14.2.

## 2. Your disc

You need your own dump of **Tekken 3, USA, SLUS-00402**. Nothing is supplied
here.

The pipeline expects a **Redump-style track set**: one `.bin` file per track,
plus a `.cue` that references all three of them. To see which sort of dump you
have, count the `FILE` lines in your `.cue`:

```bash
grep -c '^FILE' "your-dump.cue"
```

**If the answer is 3, your dump is already in the right shape. There is nothing
to do in this section, so carry on to section 3.**

If the answer is 1, your dump is a single `.bin` holding all three tracks. That
form is rejected, with:

```
disc digests not in prepare_disc.known_*
```

This is not a macOS problem, and no flag works around it. In particular,
`--skip-hash-check` makes matters worse: the single-file case takes a code path
that would collapse your two CDDA tracks. Split the dump first.

### Splitting a single-file three-track dump

Your `.cue` gives the track boundaries in its `INDEX` lines, so check it against
the table below before you start. For the standard SLUS-00402 dump of
687,924,720 bytes the boundaries are:

| Track | Type | Start sector | Sectors |
|---|---|---:|---:|
| 1 | MODE2/2352 | 0 | 268,934 |
| 2 | AUDIO | 268,934 | 11,628 |
| 3 | AUDIO | 280,562 | 11,923 |

From the directory holding your dump:

```bash
mkdir -p disc
dd if="Tekken 3.bin" bs=2352 skip=0      count=268934 of="disc/Tekken 3 (USA) (Track 1).bin"
dd if="Tekken 3.bin" bs=2352 skip=268934 count=11628  of="disc/Tekken 3 (USA) (Track 2).bin"
dd if="Tekken 3.bin" bs=2352 skip=280562 count=11923  of="disc/Tekken 3 (USA) (Track 3).bin"
```

Then write `disc/Tekken 3 (USA).cue`:

```
FILE "Tekken 3 (USA) (Track 1).bin" BINARY
  TRACK 01 MODE2/2352
    INDEX 01 00:00:00
FILE "Tekken 3 (USA) (Track 2).bin" BINARY
  TRACK 02 AUDIO
    PREGAP 00:02:00
    INDEX 01 00:00:00
FILE "Tekken 3 (USA) (Track 3).bin" BINARY
  TRACK 03 AUDIO
    INDEX 00 00:00:00
    INDEX 01 00:02:00
```

Afterwards, check track 1 against the digest this project already recognises:

```bash
shasum -a 1 "disc/Tekken 3 (USA) (Track 1).bin"
# expected: 68f32a8657376cb4d4504c160fd5e8ae4a4f18d6
```

If that matches, the split is correct. If it does not, stop here, because
everything downstream assumes it.

The file names above are the ones `[prepare_disc]` in `game.toml` expects.
Putting the track set in this repository's own `disc/` directory also saves a
687 MB copy that the pipeline would otherwise make. `disc/` is gitignored.

## 3. Build

Three commands, from the repository root:

```bash
python3 psxrecomp/psxrecomp_cli.py ensure-emitters --project-root .
```

```bash
python3 psxrecomp/psxrecomp_cli.py generate --project-root . --config game.toml --disc "disc/Tekken 3 (USA).cue"
```

```bash
python3 psxrecomp/psxrecomp_cli.py rebuild --project-root . --config game.toml --build-dir build-release --target psx-runtime --no-pgo --exe-basename Tekken_3_Recompiled
```

Two differences from the README's version of these commands:

- `python3`, as above;
- **`--exe-basename Tekken_3_Recompiled` is required.** Without it, the link
  succeeds and the command then fails with `build succeeded but binary
  missing: build-release/psx-runtime.exe`. The executable's name is derived
  from the window title rather than from the target name. This is not specific
  to macOS.

`ensure-emitters` first tries to download a prebuilt cmake and clang pack. If
that fails, it falls back to the cmake and ninja on your `PATH`, and the build
is none the worse for it. To skip the attempt altogether, add `--no-download`
and `--no-toolchain-download` to `ensure-emitters` and `rebuild`.

`generate` recompiles roughly 1.7 million lines of C into 45 shards, and
`rebuild` then compiles them. Allow several minutes for each, and a few GB of
disk.

## 4. Run

```bash
cd build-release
./Tekken_3_Recompiled
```

**Run it from inside `build-release/`.** The binary resolves `settings.toml`,
`bios/`, `assets/` and `mods/` relative to the current directory, so started
from anywhere else it opens the launcher instead of the game.

## 5. Behaviour worth knowing about

- **`settings.toml` overrides `game.toml`.** It is written into the build
  directory and remembers your choice of renderer, amongst other things. The
  order of precedence is the command line, then `settings.toml`, then
  `game.toml`. Delete it to return to the project defaults.
- **The refresh rate is read once, at start-up.** Moving the window to a
  different monitor does not cause it to be read again. On a 30 Hz panel the
  game runs at 0.50x, so restart it on the display you mean to use.
- **`self-comparison always evaluates to true` warnings** during the build are
  expected. They come from recompiled unconditional MIPS branches.

## 6. What this covers

The base game, built from source and running natively on macOS.

That includes the mods this project bundles, which need nothing done to them:
true widescreen, the roster unlock, Forest HD, the four texture packs, the
outfit gallery and the audio options are all built and work as they do on
Windows. None of their sources were changed for macOS.

Jun and other guest characters are a separate matter and are not part of this
branch.
