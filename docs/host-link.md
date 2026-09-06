# The boards and the quickshell desktop

How the keyboards talk to my quickshell config (`~/dotfiles/.config/quickshell/retro`)
and what shows up on the desktop because of it.  The firmware and keymaps are
covered in the [README](../README.md); the shell side lives in dotfiles.

## What you get

- **Layout viewer.** `SUPER+U k` (or `qs -c retro ipc call keymap toggle`)
  opens a Game & Watch style LCD drawing of the board: the Svalboard's finger
  clusters as interlocking plus shapes with the thumb pads below (the geometry
  Keybard draws), or the split 3x6 of the boardsource boards, with each key's
  tap legend on top and what it does when held underneath.  Transparent keys
  show what they fall through to, ghosted.  Tab / Space / arrows / wheel cycle
  layers, 1-9 jump, B switches boards, Escape closes.
- **Live follow.** While a board is plugged in, the viewer shows the layer it
  is on: hold a layer key and it flips, let go and it flips back.  Keys you
  hold light up in the urgent colour.  Type on another board and the viewer
  switches to it.
- **Bar chip.** A keyboard glyph with the active layer's name, in the urgent
  colour off the base layer.  Click for the backlight slider, the RGB toggle,
  the effect stepper, one row per layer to toggle it from the mouse, and a
  board switch when several boards are in.  Right-click opens the viewer; the
  wheel changes the backlight and flashes the LCD OSD.
- **IPC** for keybinds: `qs -c retro ipc call qmk up | down | set 50 |
  toggle | mode next | layer 2 | board svalboard | status`, and
  `keymap toggle | layer nav | board next | status`.

## How it is wired

```
keymap.c ──make export──▶ $XDG_STATE_HOME/quickshell/retro/keymap/<board>.json ──▶ viewer, chip labels
users/micleo2/host_link.c ◀──raw HID──▶ retro/services/qmk/qmk-bridge.py ◀──JSON lines──▶ retro/services/Qmk.qml
```

**Layout.** `host/keymap-export.py` (`make export`) reads each board's
`keymap.c` with `qmk c2json`, the layer enum and designators for names and
numbers, the layer colour table, and the key geometry (qmk `info` for the
boardsource boards, the keymap's `geometry.json` KLE for the Svalboard).  It
writes one JSON per board plus `index.json` into the shell's state dir
(`Settings.stateDir + "/keymap"`); the shell watches the files, so the viewer
updates in place.  `host/boards/<board>.json` drives it: firmware tree,
keyboard, geometry source, USB ids, layer short names and titles, legends for
custom keycodes.  Layers that are transparent everywhere and keys that do
nothing on any layer are left out.

**Link.** `users/micleo2/host_link.c` is built into every board
(`users/micleo2/rules.mk`: `RAW_ENABLE = yes`, `SRC += host_link.c`) and owns
`raw_hid_receive`.  The board pushes a STATE packet whenever layers, RGB or
caps word change and a KEY packet for every press and release, but only while
the desktop has said HELLO in the last five seconds, so a board whose bridge
has gone never stalls its matrix scan.  RGB is whichever of RGB matrix or
rgblight the board has, driven through the no-EEPROM setters and committed
once a moment after the last change.  Packets are 32 bytes, command ids in
0x40-0x6F (clear of VIA, Vial and the Svalboard's own); the full protocol is
the comment at the top of `host_link.c`.

**Host.** `qmk-bridge.py` finds the boards by USB id (its `BOARDS` table
matches `host/boards/*.json` and `host/udev/70-qmk.rules`) on their raw
HID interface, keeps the HELLO going, and turns packets into JSON lines for
`Qmk.qml`, which mirrors whichever board was typed on last.  Access to the
hidraw nodes comes from the udev rule, installed by `setup.sh`.

## After changing a keymap

```sh
make flash-svalboard-right      # or flash-unicorne / flash-lulu
make export
```

The first puts the new keymap (and the link) on the board, the second
refreshes what the desktop draws.  Check the link with
`qs -c retro ipc call qmk status`, or straight from the board with
`~/dotfiles/.config/quickshell/retro/services/qmk/qmk-bridge.py state svalboard`.
