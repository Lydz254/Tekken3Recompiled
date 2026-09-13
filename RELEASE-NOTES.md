# v0.1.0-jun-preview

First public preview of the Jun Kazama showcase version, including all ten mod
packages and their supporting runtime changes. Custom HD textures and outfit
gallery artwork are included. Jun's original assets are imported locally.

Download the **Windows x64 Setup ZIP**, extract it, and run
**Tekken_3_Recompiled.exe**. Supply a supported USA Tekken 3 disc image and use
**Generate & rebuild**. Python 3.12+ is required; the wizard obtains the build
toolchain. See the README for the additional arcade ROMs and MAME version
required by **Import-Jun.cmd**.

Release preparation verified:

- A clean setup host build with debug tools, TCP debug server and netplay disabled.
- No game or retail BIOS code linked into the distributed setup host.
- A complete game build from the packaged source using a locally supplied disc.
- A fresh, muted MAME capture and conversion reproducing all nine Jun runtime
  files byte-for-byte against the showcase version.
- Import tests rejecting mismatched chip contents and changed consumed RAM bytes.
- Explicit file allowlisting and credential/private-key/personal-path checks.
- Windows Defender scan: no threats found with the installed definitions.

Disc images, retail BIOS dumps, generated retail code, donor payloads, memory
cards, personal settings, debug captures and showcase music/video are excluded.
The ZIP includes a per-file SHA-256 manifest and a separate archive checksum.

This is an unsigned Windows preview. Steam Deck/Proton and Linux are unverified.
Jun's scope is solo combat; tag mechanics and secondary hair physics are not
included. See the README for current limitations and upstream credits.
