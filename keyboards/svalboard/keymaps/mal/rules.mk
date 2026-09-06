# Pure QMK.  No VIA/Vial: the keymap in this directory is the whole truth,
# nothing is read from EEPROM, and Keybard/Vial cannot talk to the board.
VIA_ENABLE  = no
VIAL_ENABLE = no

TAP_DANCE_ENABLE = yes    # tap_dance_actions[] in keymap.c
CAPS_WORD_ENABLE = yes    # keymap_support.c's SV_CAPS_WORD calls caps_word_toggle()
RAW_ENABLE       = yes    # host_link.c owns raw HID (desktop link)
# COMBO_ENABLE = yes      # add key_combos[] to keymap.c first
# KEY_OVERRIDE_ENABLE = yes

# The Svalboard's keycode handlers (SV_*, auto mouse layer, scrolling, DPI).
VPATH        += keyboards/svalboard/keymaps
EXTRAINCDIRS += keyboards/svalboard/keymaps
SRC += keymap_support.c

# Raw HID link to the desktop shell (symlinked from creative-synced/programming/qs-qmk).
SRC += host_link.c

# Per the Svalboard docs: LTO breaks the build, leave it off.
LTO_ENABLE = no
