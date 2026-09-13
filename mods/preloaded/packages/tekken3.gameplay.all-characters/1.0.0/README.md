# All Characters Unlocked

Enabled by default for the verified Tekken 3 USA executable (SLUS-00402).
The complete playable roster is available without completing Arcade or Tekken
Force. The game's normal alternate-character selection controls still apply.

A trusted VBlank plugin adds the 21 character-availability bits at `0x80097EF0`
and raises the Doctor's progress byte at `0x80097EF6` to at least five. It runs
only after the game starts and writes only when a value needs changing, so old
saves also gain the roster. Costume, movie and other progress flags remain
under the game's control. There is no executable or disc patch.

If an old savestate was made while already on character select, leave and
re-enter that screen to refresh the game's cached roster.

Disable **Unlock All Characters** in Mods to stop applying the unlocks. Any
unlocks subsequently saved by the game remain earned in that save.

Address reference: [Thunder2's SLUS-00402 research on GameHacking.org](https://gamehacking.org/game/89985?hacker=Thunder2).
This feature uses only the character mask and Doctor progress from those codes.
