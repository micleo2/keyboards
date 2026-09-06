# QMK userspace shared by every keymap named micleo2 (build_keyboard.mk pulls in
# users/<keymap name>/ automatically).  Board-specific settings stay in each
# keymap's rules.mk.

# Raw HID link to the desktop shell: host_link.c owns raw_hid_receive() and
# pushes layer / RGB / key events to quickshell's qmk-bridge.py.
RAW_ENABLE = yes
SRC += host_link.c
