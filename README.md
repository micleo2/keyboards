# Svalboard

My Svalboard layout as plain QMK C, plus the tooling to build and flash it.
This repo is a QMK *userspace overlay*: it holds only my keymap, and the
vendor firmware tree is the `firmware/` submodule.  No VIA, no Vial: the
keymap is compiled in, nothing is read from EEPROM, and Keybard/Vial cannot
talk to the board any more.

```
svalboard/
  Makefile                        make flash-left / flash-right / left / right / import / update
  qmk.json                        overlay marker + default build targets
  pyproject.toml, uv.lock         pins the qmk CLI (Python 3.12) for `uv run qmk`
  keyboards/svalboard/keymaps/mal/
    keymap.c                      THE LAYOUT.  Edit this.
    config.h                      tapping term and friends
    rules.mk                      features on/off, pulls in keymap_support.c and host_link.c
    vial.json                     key geometry only, read by the desktop layout viewer
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
  `keymap.c`.  Only the USB-connected half reboots.
* **Hardware:** double-tap the `RESET` button on the underside of that half.

Either way an `RPI-RP2` drive appears and the script takes it from there.  A
half stuck in bootloader mode (drive showing, nothing copied) gets out by
being flashed or by unplugging it.

Keymap-only changes take effect on the half that is USB master, because the
master looks up keycodes for both halves and pushes LED state to the other
side.  So for a quick iteration, flashing just the half you keep plugged in is
enough; flash both when you change `config.h`/`rules.mk` or update `firmware/`.

## Writing the keymap

Everything is standard QMK, so the [QMK docs](https://docs.qmk.fm) apply
directly:

* Layers are `LAYOUT(...)` blocks in `keymaps[]`; unused layer slots are
  filled with `LAYER_TRNS`.  Add a name to `enum layer` and shrink the
  `[3 ... 13]` range when you add one.
* [Tap dances](https://docs.qmk.fm/features/tap_dance): `enum` +
  `tap_dance_actions[]`, placed as `TD(name)`.  `keymap.c` carries the docs'
  tap-hold helper (`ACTION_TAP_DANCE_TAP_HOLD`) for "any keycode on tap,
  another on hold".
* Custom keycodes: start your enum at `SV_SAFE_RANGE`, not `SAFE_RANGE`, so
  they don't collide with the Svalboard's `SV_*` codes, and handle them in
  `process_record_user`.
* Combos, key overrides and the like: turn the feature on in `rules.mk` and
  define the table in `keymap.c`.
* Svalboard specifics (DPI keys, scroll toggles, auto mouse layer, `SV_*`):
  `firmware/keyboards/svalboard/keymaps/keymap_support.c` and
  `firmware/keyboards/svalboard/docs/custom_firmware.md`.  Trackball scroll
  and DPI settings still live in the Svalboard's own EEPROM block and survive
  flashes; layer colours come from `keymap.c` at every boot.

## Re-importing from Keybard

```sh
cp ~/Downloads/whatever.kbi layouts/keybard/
make import KBI=layouts/keybard/whatever.kbi     # overwrites keymap.c
```

The converter handles keycodes, layer colours and tap dances (emitted as
standard QMK `tap_dance_actions`), and refuses to run if the export contains
macros, combos or key overrides, so those are never silently dropped.

## The firmware submodule

`firmware/` is my fork of [svalboard/vial-qmk](https://github.com/svalboard/vial-qmk)
on branch `mal`: upstream's `vial` branch plus two small patches to
`svalboard.c`: the board's init/split-sync code runs without Vial, and a
`raw_hid_receive_user()` hook for Vial builds.
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
