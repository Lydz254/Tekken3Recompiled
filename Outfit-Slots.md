# Skin gallery

Launch `Play-Tekken3-Recompiled.cmd`, highlight Nina, Anna, Xiaoyu or Kuma, and press
**L1** to open the skin gallery. The selection timer pauses while browsing.

| Control | Action |
| --- | --- |
| L1 (keyboard default Q) | Open the highlighted fighter's gallery; close it to cancel |
| Left / Right arrows or controller D-pad | Browse; wrap at either end |
| Cross / Square / Start or Enter | Select the displayed outfit and confirm the fighter |
| Circle or Escape | Cancel and return to character select |
| `[` / `]` | Open player 1's gallery |
| `;` / `'` | Open player 2's gallery after joining |

Nina has three entries: **Purple Assassin**, **Crimson Leather**, and **White
Satin**. Anna has four: **Scarlet Silk**, **Midnight Silk**, **White Tiger**, and
**Jessica Rabbit**. Xiaoyu has four: **Red & Gold**, **Blue Ribbon**, **School
Uniform**, and **Cherry Blossom**. Kuma has three: **Brown Bear**, **Panda**,
and **Polar Bear**. Polar Bear adds white fur to Kuma's existing model while
retaining his red bandana and wristband. The gallery opens for one player at a time;
each player's browsing choice is remembered independently for each fighter.

Selecting directly from the ordinary roster retains the original punch/kick/
Start costume controls. L1 does not affect combat inputs. Missing or disabled
HD packs remove their custom entries. Original costumes remain available.

The menu is for local OpenGL play. Its host choices are not stored inside old
PS1 save-state files: loading a match uses the host cosmetic choice currently
confirmed in this process. New launches start with the original costumes.

## Artwork

All fourteen portrait illustrations (Nina's three, Anna's four, Xiaoyu's
four and Kuma's three) are 1024x1536, with distinct poses, camera angles and color palettes.
Base Kuma uses an exact copy of the user's Project Fighter Raids
`Loading Screen/Kuma.png`. The other portraits were generated with the built-in
image_gen tool using the Raids loading art as style references. The reference folder is read-only; originals are preserved there.
Nina's revised prompts are in `workspace/outfit-menu/raids-prompts.json`.
Anna and Xiaoyu's prompts, web costume references, original generated paths
and final image hashes are in
`workspace/outfit-menu/anna-xiaoyu-splash-prompts.json`. Their previous
gameplay crops are preserved in `workspace/outfit-menu/gameplay-art-references`.
The blue and school-uniform Xiaoyu cards now have complete splash art.
Menu artwork and its runtime RGBA copies are in `mods/assets/outfit-menu`.
Kuma, Panda and Polar Bear use a forest fight, bamboo garden and Arctic ice
scene respectively. Their prompts and generated originals are recorded in
`workspace/kuma-skin/prompts.json`.

## Extending the menu

`mods/assets/outfit-menu/catalog.txt` supplies the rows; the renderer always
shows a scrolling three-card view and computes the total from the catalog.
No menu layout code needs to change to add more entries. Each row is:

```
id|character ID|display name|stock confirmation mask in hex|skin ID|art basename
```

Stock confirmation masks: `8000` = punch outfit, `4000` = kick outfit,
`0008` = third outfit. Skin ID `-1` uses original textures; the registered HD
packs currently use `0` = Nina, `1` = Xiaoyu, `2` = Anna, `3` = Kuma. A new HD atlas needs
its own renderer pack registration in addition to a catalog row. IDs and art
basenames use letters, digits, hyphens or underscores. Duplicate IDs and
malformed rows are ignored. Missing art keeps a usable labelled card; a
missing/empty catalog falls back to the built-in entries.

Put a 2:3 PNG under the matching art basename and run:

```
python tools/outfit_menu_pack.py
```

Build the runtime to stage the catalog and artwork beside the executable.
Restart the game to reload them.

## Implementation and verification

`tekken3_outfits.c` owns selection, cancellation, player isolation and finite
confirmation pulses. Guest VBlank ticks, rather than controller poll count,
time those pulses. The main runtime parks the guest at a safe VBlank while
the menu polls host input and redraws the last frame. Match simulation and
the selection timer remain frozen until the menu closes.

The SLUS-00402 character bytes are `0x80098106/7`. The original third-costume
selection handler at `0x8010DAE0` tests bit(character) of `0x80097EF4`.
The gallery temporarily supplies only a missing bit needed for a selected
third costume, then restores it after selection; it preserves the other
unlock/progress bits. Original texture and palette guards remain active.

`tools/tests/outfit_slots_test.c` covers navigation edges, cancel, multiple
players, missing packs, 19 dynamically loaded entries, third-costume flags,
and unchanged combat input for all 65,536 button words on both players.
`tools/verify_outfit_gallery.py --matches` checks the real L1 input path,
frozen selector state, all 11 confirmations, and captures each match.
`out/outfit-slots/gallery-validation.json` records the live results.
The debug-only `outfit_screenshot` command captures the actual host gallery,
which is outside the guest framebuffer used by ordinary screenshots.
Kuma's three live selections and match captures are recorded separately in
`out/kuma-skin/gallery-validation.json`. The focused Kuma tests cover stock
punch/kick selection, both player choices, custom-pack availability, exact
4bpp pixel/palette matching, Panda rejection and preserved accessories.
