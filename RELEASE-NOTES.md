# v0.1.1 — Easy setup

**Open Play Tekken 3.exe, choose your game files, and click Set up & play.**

The launcher downloads its tools, prepares the game and all selected mods,
imports Jun, builds locally, and opens the game. On later launches the same icon
starts the game directly. Use Configure Tekken 3.cmd for graphics, controls and mods.

- No manual Python, Pillow, MAME or compiler installation.
- One setup screen for the disc and optional Jun donor ZIPs.
- Progress messages, Cancel, and Retry after an interrupted setup.
- Pinned tool downloads checked with SHA-256 before use.
- Portable tools stay in the application folder; no system PATH changes.
- Smaller ZIP: duplicate textures are rebuilt from the included PNGs and checked
  byte-for-byte against all 20 existing runtime textures.
- Gameplay and mod behavior are unchanged from the Jun showcase preview.

First setup requires internet access, your supported game files, at least 4 GB
of working space, and several minutes. For Jun, provide the supported TTT1 and
Tekken 3 arcade ZIPs as well as the USA PS1 disc. No ROMs or retail BIOS are included.

Windows x64 preview. Steam Deck/Proton and native Linux remain unverified.
