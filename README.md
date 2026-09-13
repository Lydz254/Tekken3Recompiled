# Tekken 3 Recompiled Jun showcase build

A Windows PC project built on **psxrecomp**, with Jun Kazama added as a separate
fighter. This preview includes the version used in the Jun showcase and an automatic first-run setup.

Jun has her own roster entry in both character selectors, imported TTT1 solo
moves and animations, paired throws and reversals, voices, victory poses, and
restored Tekken 3 arcade selector/loading artwork. Her slot does not replace Jin.

This is a **hybrid recompilation**: translated game routines run alongside PS1
hardware models and interpreter fallback. It is not a completed source decompilation.
Development was assisted by AI, with local compilation and gameplay testing.

## Download and play

Download **[Tekken3Recompiled-v0.1.1-Easy-Setup.zip](https://github.com/FishB0nes98/Tekken3Recompiled/releases/tag/v0.1.1-easy-setup)**.

1. Extract the whole ZIP and open **Play Tekken 3.exe**.
2. Choose your Tekken 3 USA PS1 disc image. For Jun, also choose your TTT1
   and Tekken 3 arcade ZIPs.
3. Click **Set up & play**. The launcher handles everything and opens the game.

**No manual Python, MAME, compiler or command-line setup.** The smaller download
includes its own Python and image tools; the remaining tools download
from pinned upstream releases on first setup. Allow several minutes and at
least 4 GB of free working space. Nothing is installed into your system PATH.

After setup, opening **Play Tekken 3.exe** starts the game directly.
Use **Configure Tekken 3.cmd** to open the graphics, controller and mod settings.
If a download is interrupted, click **Try again**. **Cancel** stops the setup
processes and keeps completed downloads for another attempt.

### Your game files

- **Tekken 3 PS1:** USA, **SLUS-00402**, with its CUE/BIN tracks.
- **TTT1 arcade for Jun:** non-merged `tektagt.zip`, World TEG2/VER.C1, set 1.
- **Tekken 3 arcade portraits:** non-merged `tekken3.zip`, World TET2/VER.E1.

Keep **Include Jun Kazama** checked to add her automatically. Turn it off if
setting up only the base game and the other mods. The importer verifies the
arcade chips and all nine converted Jun files against the tested showcase build.

The launcher requires your game files. **No ROMs, retail BIOS, extracted Jun
payloads or generated retail game code are included.** Game data is processed
locally and is never uploaded. OpenBIOS is included under its own license.

## Included mods and improvements

| Feature | Included |
| --- | --- |
| Jun Kazama | Separate character, both selectors, solo TTT1 combat/throws/reversals, voices and victory poses; local donor import required |
| True widescreen | Native 16:9 stage rendering, adjusted menus/selectors/loading screens, optional wider fight camera |
| Roster unlock | Access to the existing hidden fighters |
| Forest HD | Custom Yoshimitsu stage background and ground textures |
| Nina White Satin | Custom texture pack and outfit gallery card |
| Xiaoyu Cherry Blossom | Custom texture pack and outfit gallery card |
| Anna Jessica Rabbit | Custom texture pack and outfit gallery card |
| Kuma Polar Bear | Custom texture pack and outfit gallery card |
| Outfit gallery | Custom illustrations, original costume choices retained; press L1 on a supported fighter |
| Audio options | Separate music and sound-effect volume controls |
| Framework enhancements | Fast loading and configurable CD speed |

OpenGL, 16:9, perspective-correct textures and 3Ă— supersampling are the project
defaults. Adjust these in the launcher for your hardware. Custom texture and
gallery artwork includes AI-generated illustrations.

## Preview limits

Windows x64 has been tested. Steam Deck/Proton and native Linux are **unverified**.
Jun's conversion targets **solo combat**; tag mechanics are excluded. Her hair
and bow use rigid attachments. Live checks cover representative moves, throws,
reactions and wins, rather than exhaustive timing parity with the arcade game.
Netplay is not part of this preview. The separate `native/` target is an early
experimental port and is disabled by default.

## Source builds

The modified framework and UI source are vendored so downloading the repository
preserves all local changes. Exact upstream revisions are in [UPSTREAM.json](UPSTREAM.json).
No submodule checkout is required for this release.

```powershell
python psxrecomp/psxrecomp_cli.py ensure-emitters --project-root .
python psxrecomp/psxrecomp_cli.py generate --project-root . --config game.toml --disc "PATH-TO-YOUR-DISC.cue"
python psxrecomp/psxrecomp_cli.py rebuild --project-root . --config game.toml --build-dir build-release --target psx-runtime --no-pgo
```

To build only the distributable setup host, configure CMake with
`PSXRECOMP_FORCE_SETUP_HOST=ON`, `PSXRECOMP_ALLOW_NO_BIOS=ON`,
`PSXRECOMP_BIOS_STEMS=OpenBIOS`, `PSX_STATIC_RUNTIME=ON`, and both
`PSX_DEBUG_TOOLS=OFF` and `PSX_DEBUG_SERVER_LITE=OFF`. Generated retail code and
imported assets must never be copied into a public setup archive.

## Credits and notices

Project and mods: **FishB0nes98**. Built on Matthew Stan's
[psxrecomp](https://github.com/RetroPortingToolKit/psxrecomp) and
[recomp-ui](https://github.com/RetroPortingToolKit/recomp-ui), with project-specific
runtime and recompiler changes included here. MAME provides the arcade reference
and verified ROM metadata. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
and the licenses retained in each dependency.

This is an unofficial fan project. Tekken and its original characters, game data,
music and artwork belong to their respective rights holders. The source is not
an offer of rights to the original game assets. psxrecomp uses the **PolyForm
Noncommercial 1.0.0** license; see [LICENSE](LICENSE). Third-party components retain
their own licenses.
