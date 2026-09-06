# Svalboard

My Svalboard layout as plain QMK C, plus the tooling to build and flash it.
This repo is a QMK *userspace overlay*: it holds only my keymap, and the
vendor firmware tree is the `firmware/` submodule.

```
svalboard/
  Makefile                        make flash-left / flash-right / left / right / import / update
  qmk.json                        overlay marker + default build targets
  pyproject.toml, uv.lock         pins the qmk CLI (Python 3.12) for `uv run qmk`
  keyboards/svalboard/keymaps/mal/
    keymap.c                      THE LAYOUT.  Edit this.
    config.h                      Vial UID, unlock combo, tapping term
    rules.mk                      Vial on, pulls in keymap_support.c and host_link.c
    vial.json                     layout definition Vial/Keybard need
    host_link.c/.h -> ../../../../../qs-qmk/firmware/   raw HID link to the desktop
  tools/kbi2keymap.py             Keybard .kbi  ->  keymap.c
  tools/flash.sh                  build, wait for the RPI-RP2 drive, copy
  layouts/keybard/*.kbi           archived Keybard exports
  layouts/vial/*.vil              archived Vial exports
  firmware/                       submodule: micleo2/svalboard-vial-qmk, branch mal
  QUICKSHELL.md                   how the board talks to the quickshell desktop
```

The qmk CLI is wired up via `~/.config/qmk/qmk.ini` (`user.qmk_home`,
`user.overlay_dir`, `user.keyboard`, `user.keymap`).  It runs from the uv
environment, so use `make`, or `uv run qmk ...` from this directory; the
system `qmk` on Python 3.14 cannot drive this firmware tree.

## Daily use

```sh
make flash-left          # build, wait for the left half in bootloader, copy the .uf2
make flash-right
make flash               # both, one after the other
make left right          # build only -> svalboard_trackball_pmw3389_{left,right}_mal.uf2 here
```

`make flash-*` builds first, then waits for the `RPI-RP2` drive, mounts it
with udisks (no desktop automount needed), copies the firmware, and unmounts.

Both halves have a pmw3389 trackball, so that variant is the default
(`POINTER ?= trackball/pmw3389` in the Makefile).  Other variants:

```sh
make right POINTER=                     # plain, no pointing device
make right POINTER=trackpoint
make left  POINTER=trackball/pmw3360    # only on very early boards
```

(`azoteq` and `pimoroni` also exist.)  Flashing the wrong variant is harmless;
the pointer just won't work until the right one is flashed.

### Getting a half into flashing mode

The half you flash must be the one plugged into the computer, via its port
labelled `U` (not `S`).  Then either:

* **From the keyboard:** tap the sys_ctrl layer key (right ring finger, east,
  a one-shot layer) then press left pinky centre.  That is `QK_BOOT` in
  `keymap.c`, "Reset" in Keybard.  Only the USB-connected half reboots.
* **Hardware:** double-tap the `RESET` button on the underside of that half.

Either way an `RPI-RP2` drive appears and the script takes it from there.  A
half stuck in bootloader mode (drive showing, nothing copied) gets out by
being flashed or by unplugging it.

Keymap-only changes take effect on the half that is USB master, because the
master looks up keycodes for both halves and pushes LED state to the other
side.  So for a quick iteration, flashing just the half you keep plugged in is
enough; flash both when you change `config.h`/`rules.mk` or update `firmware/`.

Vial/Keybard cannot load firmware, only edit the keymap in EEPROM, so C
changes always go through a `.uf2` flash.

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

```sh
cp ~/Downloads/whatever.kbi layouts/keybard/
make import KBI=layouts/keybard/whatever.kbi     # overwrites keymap.c
```

The converter handles keycodes, layer colours and Vial tap dances (seeded
into EEPROM on a fresh flash), and refuses to run if the export contains
macros, combos or key overrides, so those are never silently dropped.

## The firmware submodule

`firmware/` is my fork of [svalboard/vial-qmk](https://github.com/svalboard/vial-qmk)
on branch `mal`: upstream's `vial` branch plus one patch, a
`raw_hid_receive_user()` hook in `svalboard.c` that `host_link.c` needs.
Remotes inside it: `origin` = the fork, `upstream` = Svalboard.

```sh
make update        # fetch upstream, rebase mal on upstream/vial, sync submodules
git -C firmware push --force-with-lease origin mal
git add firmware && git commit -m "firmware: rebase on upstream"
```

Fresh clone of this repo:

```sh
git clone --recurse-submodules --shallow-submodules <this repo>
uv run qmk config user.qmk_home=$PWD/firmware user.overlay_dir=$PWD \
    user.keyboard=svalboard/trackball/pmw3389/left user.keymap=mal
make left
```

Svalboard's own docs on custom firmware:
`firmware/keyboards/svalboard/docs/custom_firmware.md`.
