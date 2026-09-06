# Svalboard and the quickshell desktop

How the Svalboard talks to my quickshell config (`~/dotfiles/.config/quickshell/retro`)
and what shows up on the desktop because of it. The firmware and layout
themselves are covered in `README.md`; the host side and the protocol
live in `~/creative-synced/programming/qs-qmk`.

## What you get

- **Layout viewer.** `SUPER+U k` (or `qs -c retro ipc call keymap toggle`)
  opens a Game & Watch style LCD drawing of the board: the finger clusters
  as interlocking plus shapes and the thumb pads below, the same geometry
  Keybard draws, with each key's tap legend on top and what it does when
  held underneath. Transparent keys show what they fall through to,
  ghosted. Tab / Space / arrows / wheel cycle layers, 1-9 jump, B switches
  to the unicorne and back, Escape closes.
- **Live follow.** While the board is plugged in, the viewer shows the
  layer the board is on: hold the nav/symbols thumb key and it flips to
  NAV, let go and it flips back. Keys you hold light up in the urgent
  colour. Type on the unicorne instead and the viewer switches boards.
- **Bar chip.** A keyboard glyph with the active layer's name, in the
  urgent colour off the base layer. Click for the backlight slider, the
  RGB toggle, the effect stepper, one row per layer to toggle it from the
  mouse, and a board switch when two boards are in. Right-click opens the
  viewer; the wheel changes the backlight and flashes the LCD OSD.
- **IPC** for keybinds: `qs -c retro ipc call qmk up | down | set 50 |
  toggle | mode next | layer 2 | status`, and `keymap layer nav`,
  `keymap board svalboard`.

## How it is wired

```
keymap.c ──keymap-export.py──▶ retro/keymap/svalboard.json ──▶ viewer, chip labels
host_link.c (in the keymap) ◀──raw HID──▶ qmk-bridge.py ◀──JSON lines──▶ services/Qmk.qml
```

**Layout.** `~/creative-synced/programming/qs-qmk/keymap-export.py --board svalboard`
reads `keyboards/svalboard/keymaps/mal/keymap.c` with `qmk c2json`, the
layer enum and designators for names and numbers, the HSV layer colour table,
and `geometry.json`'s KLE for where every key sits. It writes
`retro/keymap/svalboard.json`; the shell watches the file, so the viewer
updates in place. The board config that drives it is
`qs-qmk/boards/svalboard.json`: layer short names and titles, legends for the
`SV_*` keycodes, and the trees to read from. Layers that are transparent
everywhere (3 to 13) and keys that do nothing on any layer (the double-south
positions) are left out.

**Link.** `host_link.c` is symlinked into the keymap from
`qs-qmk/firmware/` and built by `SRC += host_link.c` plus `RAW_ENABLE = yes`
in the keymap's rules.mk. The build has no VIA/Vial, so the file owns
`raw_hid_receive` outright (its non-VIA path). The fork
`micleo2/svalboard-vial-qmk`, branch `mal`, the `firmware/` submodule, is
patched so the Svalboard's boot and split-sync code runs without Vial. The board pushes a STATE packet
whenever layers, rgblight or caps word change and a KEY packet for every
press and release, but only while the desktop has said HELLO in the last
five seconds. Backlight brightness is the rgblight value the Svalboard keeps
across its per-layer colours, set through the no-EEPROM path and committed
once a moment later.

**Host.** `retro/services/qmk/qmk-bridge.py` finds the board by USB id
(303a:4044) on its raw HID interface, keeps the HELLO going, and turns
packets into JSON lines for `services/Qmk.qml`, which mirrors whichever
board was typed on last. Without Vial the board no longer carries the Vial
serial the stock vial udev rule matches, so the rule in `qs-qmk/udev/`
(matching by USB id, installed as `70-qmk-unicorne.rules`) is what grants
access to its hidraw node.

## After changing the keymap

```sh
make flash-left                    # or flash-right; the half on the U port
~/creative-synced/programming/qs-qmk/keymap-export.py --board svalboard
```

The first puts the new keymap (and the link) on the board, the second
refreshes what the desktop draws. Check the link with
`qs -c retro ipc call qmk status`, or straight from the board with
`~/dotfiles/.config/quickshell/retro/services/qmk/qmk-bridge.py state svalboard`.
