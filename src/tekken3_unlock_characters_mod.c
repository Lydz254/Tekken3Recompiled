/* Default roster unlock for the exact SLUS-00402 executable in the manifest.
 * The game reads its character availability mask from 0x80097EF0 and the
 * Doctor's Tekken Force progress byte from +6. The adjacent costume/movie
 * flags are separate and are deliberately not part of this feature.
 * See the package README for the original address research.
 */
#include "mod_plugins.h"

static void tekken3_unlock_characters(void)
{
    const uint32_t roster_address = 0x80097EF0u;
    const uint32_t roster_mask = 0x001FFFFFu;
    const uint32_t doctor_progress_address = 0x80097EF6u;
    if (!psx_mod_game_started()) return;

    uint32_t roster = psx_mod_read_word(roster_address);
    if ((roster & roster_mask) != roster_mask)
        psx_mod_write_word(roster_address, roster | roster_mask);
    if (psx_mod_read_byte(doctor_progress_address) < 5u)
        psx_mod_write_byte(doctor_progress_address, 5u);
}

PSX_MOD_CONSTRUCTOR(tekken3_register_unlock_characters)
{
    (void)psx_mod_register_vblank_plugin(
        "tekken3.unlock-all-characters", tekken3_unlock_characters);
}
