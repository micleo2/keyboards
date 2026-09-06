# Svalboard QMK userspace

My Svalboard layout as plain QMK C, built against the Svalboard fork of
vial-qmk.  This repo is a QMK *userspace overlay*: it holds only my keymap
and tooling, and the vendor firmware tree lives next door in
`../svalboard-vial-qmk` (branch `mal`, which is upstream `vial` plus one
Python 3.14 compatibility fix).

```
qmk/                                   <- this repo (overlay)
  qmk.json                             overlay marker + default build targets
  Makefile                             make left / right / flash-* / import
  keyboards/svalboard/keymaps/mal/
    keymap.c                           THE LAYOUT.  Edit this.
    config.h                           Vial UID, unlock combo, tapping term
    rules.mk                           Vial on, pulls in keymap_support.c
    vial.json                          layout definition Vial/Keybard need
  tools/kbi2keymap.py                  Keybard .kbi  ->  keymap.c
  layouts-kbi/                         archived Keybard exports
../svalboard-vial-qmk/                 <- vendor tree, don't edit keymaps here
```

The qmk CLI is wired up via `~/.config/qmk/qmk.ini`
(`user.qmk_home`, `user.overlay_dir`, `user.keyboard`, `user.keymap`), so
`qmk compile` works from anywhere.

## Daily use

```sh
make flash-left          # build, wait for the left half in bootloader, copy the .uf2
make flash-right
make flash               # both, one after the other
make left right          # build only -> svalboard_{left,right}_mal.uf2 here
```

`make flash-*` builds first, then waits for the `RPI-RP2` drive, mounts it
with udisks (no desktop automount needed), copies the firmware, and unmounts.

### Getting a half into flashing mode

The half you flash must be the one plugged into the computer, via its port
labelled `U` (not `S`).  Then either:

* **From the keyboard:** hold the sys_ctrl layer key (right ring finger, east)
  and press left pinky west.  That is `QK_BOOT` in `keymap.c`.  Only the
  USB-connected half reboots.
* **Hardware:** double-tap the `RESET` button on the underside of that half.

Either way an `RPI-RP2` drive appears and the script takes it from there.  A
half stuck in bootloader mode (drive showing, nothing copied) gets out by
being flashed or by unplugging it.

Keymap-only changes take effect on the half that is USB master, because the
master looks up keycodes for both halves and pushes LED state to the other
side.  So for a quick iteration, flashing just the half you keep plugged in is
enough; flash both when you change anything else, or to keep them in sync.

Vial/Keybard cannot load firmware, only edit the keymap in EEPROM, so C
changes always go through a `.uf2` flash.

If a half has a pointing device, build the matching variant:

```sh
make right POINTER=trackpoint
make left  POINTER=trackball/pmw3389    # pmw3360 only on very early boards
```

(`azoteq` and `pimoroni` also exist.)  Flashing the wrong variant is harmless;
the pointer just won't work until the right one is flashed.

## How the C keymap wins over Vial

Vial stays enabled because the Svalboard's own init code (EEPROM settings,
DPI, layer colours, split sync) is only compiled in Vial builds.  Every build
gets a random `BUILD_ID`, and Vial stamps that into EEPROM as the keymap
validity magic.  Flashing a *new build* therefore invalidates whatever Vial or
Keybard stored and the compiled `keymaps[]` is loaded instead.  Layer colours
are copied from `keymap.c` on every boot.  Net effect: `keymap.c` is the
source of truth; anything changed in Keybard survives only until the next
flash.

## Re-importing from Keybard

If you ever tweak things in Keybard and want to pull them back into C:

```sh
cp ~/Downloads/whatever.kbi layouts-kbi/
make import KBI=layouts-kbi/whatever.kbi     # overwrites keymap.c
```

The converter handles keycodes and layer colours only, and refuses to run if
the export contains macros, combos, tap dances or key overrides, so those are
never silently dropped.  Add them by hand in `keymap.c` instead.

## Updating the vendor tree

```sh
cd ../svalboard-vial-qmk
git fetch origin && git rebase origin/vial       # keeps the py3.14 fix on top
git submodule update --init --recursive
```

Then rebuild.  The Svalboard docs on custom firmware are at
`keyboards/svalboard/docs/custom_firmware.md` in the vendor tree.
