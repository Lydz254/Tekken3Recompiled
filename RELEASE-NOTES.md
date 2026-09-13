# v0.1.2 - Easy Setup build fix

Fixes the setup loop that repeatedly runs CMake and eventually reports
`manifest 'build.ninja' still dirty after 100 tries`.

## Already stuck on v0.1.1?

Download **Tekken3Recompiled-v0.1.2-Setup-Fix.zip**, the small patch.

1. Close the launcher.
2. Extract the patch and copy its contents into your **existing** Easy Setup
   folder, beside **Play Tekken 3.exe**. Choose **Replace** when asked.
3. Open **Play Tekken 3.exe** again and retry setup.

Keep the existing game folder in place. Downloads, imported Jun files,
completed build work, settings and saves are retained. No terminal commands
are needed. This patch requires the v0.1.1 Easy Setup package.

## New installation

Download **Tekken3Recompiled-v0.1.2-Easy-Setup.zip**, extract the entire archive,
and open **Play Tekken 3.exe**. Choose your game files and click **Set up & play**.
The launcher downloads the remaining tools automatically.

## Changes

- Easy Setup explicitly configures on every attempt, then builds without
  Ninja's automatic CMake regeneration checks. This avoids the loop reproduced
  with future-dated input files. Normal developer builds keep their defaults.
- Build errors now direct you to the setup log instead of suggesting that every
  failure is caused by heavy apps or insufficient memory.
- Gameplay and all included mods are unchanged, including Jun Kazama.

First setup requires internet access, your supported Tekken 3 USA PS1 disc,
and at least 4 GB of working space. Jun also requires the supported TTT1 and
Tekken 3 arcade ZIPs. No ROMs, retail BIOS, extracted donor assets, or generated
retail game code are included. Windows x64 preview; Steam Deck/Proton and native
Linux remain unverified.
