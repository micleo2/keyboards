# Keep Vial on: the Svalboard's own init code (EEPROM settings, DPI, layer
# colours, split sync) is only compiled in Vial builds.  Because every build
# gets a fresh random BUILD_ID, flashing a new build invalidates the keymap
# stored in EEPROM and the compiled keymap below takes over.
VIA_ENABLE = yes
VIAL_ENABLE = yes
VIAL_INSECURE ?= yes

# Pull in the Svalboard keycode handlers (SV_*, auto mouse layer, scrolling).
VPATH += keyboards/svalboard/keymaps
EXTRAINCDIRS += keyboards/svalboard/keymaps
SRC += keymap_support.c

# Per the Svalboard docs: LTO breaks the build, leave it off.
LTO_ENABLE = no
