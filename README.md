# keyboards

My QMK keymaps, as a QMK *userspace overlay*: this repo holds only my keymaps,
shared code and tooling, and builds against pristine firmware trees checked
out as submodules.  Plain QMK everywhere, no VIA/Vial.

| board | keymap | firmware tree | build | flash |
|---|---|---|---|---|
| Svalboard (both halves pmw3389 trackballs) | `keyboards/svalboard/keymaps/micleo2/` | `firmware/svalboard` (fork of svalboard/vial-qmk, branch `mal`) | `make svalboard-left svalboard-right` | `make flash-svalboard-left` / `-right` |
| Boardsource unicorne | `keyboards/boardsource/unicorne/keymaps/micleo2/` | `firmware/qmk` (upstream qmk_firmware) | `make unicorne` | `make flash-unicorne` |
| Boardsource lulu (rp2040) | `keyboards/boardsource/lulu/keymaps/micleo2/` | `firmware/qmk` | `make lulu` | `make flash-lulu` |

```
Makefile                build / flash / export / import / update-* / setup
setup.sh                fresh machine (toolchain, submodules, uv env, qmk config, udev, export)
qmk.json                overlay marker + default build targets
pyproject.toml uv.lock  pins the qmk CLI (Python 3.12); everything runs it as `uv run qmk`
keyboards/<board>/keymaps/micleo2/   one keymap per board (keymap.c, config.h, rules.mk)
users/micleo2/          shared by every board (QMK auto-includes users/<keymap name>/):
  host_link.c/.h          raw HID link to the desktop shell (protocol documented at the top)
  gw_oled.h               Game & Watch OLED art used by the boardsource keymaps
  rules.mk                RAW_ENABLE + host_link.c
host/                   the computer side of that link (host_link.c is the board side)
  keymap-export.py        keymap.c -> $XDG_STATE_HOME/quickshell/retro/keymap/<board>.json (viewer data)
  boards/<board>.json     per-board export config: firmware tree, keyboard, geometry, USB ids, legends
  udev/70-<board>-bridge.rules   hidraw access for each board (installed by setup.sh)
docs/host-link.md       how the boards talk to the quickshell desktop
tools/kbi2keymap.py     Keybard .kbi export -> Svalboard keymap.c
tools/flash.sh          build, wait for the RPI-RP2 drive, copy the .uf2
keybard-exports/        old Keybard .kbi exports, input to `make import`
firmware/svalboard      submodule
firmware/qmk            submodule
```

The desktop half (bar chip, layout viewer, the bridge that owns the hidraw
nodes) lives in the quickshell config in `~/dotfiles`; the only contract
between the two is the HID protocol in `users/micleo2/host_link.c` and the
JSON files `make export` writes.

**Raw HID access.**  The bridge opens each board's hidraw node, which is
root-only by default.  `host/udev/70-<board>-bridge.rules` tags the node
`uaccess` by USB vendor/product id, and logind then grants the active seat's
user access.  The `70-` prefix matters: the system rule that acts on the tag is
`73-seat-late.rules`, and udev runs rule files in name order.  Only the bridge
needs this; building and flashing do not.  `setup.sh` installs the rules and
reloads udev.

## Daily use

```sh
make flash-svalboard-right     # build, wait for the half in bootloader, copy the .uf2
make flash-unicorne            # same for the unicorne (make flash-lulu for the lulu)
make export                    # refresh what the desktop viewer draws
make                           # build every board -> *.uf2 here
```

`tools/flash.sh` builds first, then waits for the `RPI-RP2` drive, mounts it
with udisks (no desktop automount needed), copies the firmware, and unmounts.

**Bootloader mode.**  Svalboard: the half to flash must be the one plugged
in, through its port labelled `U`.  Tap the sys_ctrl layer key (right ring
finger, east, a one-shot layer) then press left pinky centre (`QK_BOOT`), or
double-tap the `RESET` button on its underside.  Unicorne / lulu: `QK_BOOT`
in the layout, or the button on the controller.  A board stuck in bootloader
mode (drive showing, nothing copied) gets out by being flashed or unplugged.

Svalboard keymap-only changes take effect on the half that is USB master (it
looks up keycodes for both halves and pushes LED state to the other side), so
one flash is enough for a quick iteration; flash both when `config.h`,
`rules.mk` or `firmware/svalboard` change.  Trackball DPI and scroll settings
live in the Svalboard's own EEPROM block and survive flashes; layer colours
come from `keymap.c` at every boot.

Svalboard pointing-device variants, if a half ever changes:
`make svalboard-right POINTER=` (none), `POINTER=trackpoint`,
`POINTER=trackball/pmw3360` (very early boards), `azoteq`, `pimoroni`.

## Writing a keymap

Everything is standard QMK, so the [QMK docs](https://docs.qmk.fm) apply:

* Layers are `LAYOUT(...)` blocks in `keymaps[]`.  The Svalboard file fills
  unused layer slots with `LAYER_TRNS`; shrink the `[3 ... 13]` range when
  adding a layer.
* [Tap dances](https://docs.qmk.fm/features/tap_dance): `enum` +
  `tap_dance_actions[]`, placed as `TD(name)`.  The Svalboard keymap carries
  the docs' tap-hold helper (`ACTION_TAP_DANCE_TAP_HOLD`).
* Custom keycodes on the Svalboard start at `SV_SAFE_RANGE`, not
  `SAFE_RANGE`, so they don't collide with its `SV_*` codes (DPI, scroll,
  sniper, ...), which come from
  `firmware/svalboard/keyboards/svalboard/keymaps/keymap_support.c`; see
  `firmware/svalboard/keyboards/svalboard/docs/custom_firmware.md`.
* Code every board should get goes in `users/micleo2/`.

### Importing a Keybard export (Svalboard)

```sh
cp ~/Downloads/whatever.kbi keybard-exports/
make import KBI=keybard-exports/whatever.kbi     # overwrites keymap.c
```

Keycodes, layer colours and tap dances (as `tap_dance_actions`) are
converted; the script refuses exports with macros, combos or key overrides
rather than dropping them.  Keybard cannot talk to the board any more (no
Vial), so this is a one-way import.  `geometry.json` next to the keymap is
Keybard's key layout in Vial's KLE format, kept only for the viewer.

## Firmware trees

* `firmware/qmk`: pristine [qmk/qmk_firmware](https://github.com/qmk/qmk_firmware)
  `master`, pinned at a commit.  Everything the boardsource boards need is in
  their keymaps' `config.h`/`rules.mk` (a keymap `config.h` is included after
  the keyboard's and the generated `info_config.h`, so `#undef` + `#define`
  overrides anything).  `make update-qmk` moves the pin to current master.
* `firmware/svalboard`: fork of [svalboard/vial-qmk](https://github.com/svalboard/vial-qmk),
  branch `mal` = upstream `vial` + two small patches to `svalboard.c` (the
  board's init/split-sync code runs without Vial; a `raw_hid_receive_user`
  hook for Vial builds).  Inside it `origin` is the fork, `upstream` the original.

### Working on the Svalboard fork

Edit directly in `firmware/svalboard`; it is a normal clone on branch `mal`.
The one rule of submodules: the parent repo records a commit hash, so after
committing inside the submodule, push it *and* commit the new pointer here,
otherwise a fresh clone checks out the old commit.

```sh
cd firmware/svalboard
git commit -am "svalboard: ..." && git push origin mal
cd ../.. && git add firmware/svalboard && git commit -m "firmware/svalboard: <what changed>"
```

`setup.sh` clones the submodules shallow (`--depth 1`); before rebasing on
upstream from a fresh machine run `git -C firmware/svalboard fetch --unshallow upstream`.

```sh
make update-svalboard          # fetch upstream, rebase mal, sync submodules
git -C firmware/svalboard push --force-with-lease origin mal
git add firmware/svalboard && git commit -m "firmware/svalboard: rebase on upstream"
```

## Fresh machine

```sh
gh repo clone micleo2/keyboards ~/oss/keyboards
~/oss/keyboards/setup.sh      # pacman deps, submodules (shallow), uv env, qmk config, udev, export
```

`setup.sh` is idempotent: rerun it after pulling to pick up new submodule
pins, udev rules or Python deps (`NO_SUDO=1` skips the pacman and udev steps).
`~/dotfiles/install/arch-hyprland.sh` does exactly that.  The qmk CLI is
configured with `user.overlay_dir` only; the Makefile passes `QMK_HOME` per
board (the CLI would prefer a configured `qmk_home` over the environment).
For ad hoc CLI use: `QMK_HOME=$PWD/firmware/qmk uv run qmk info -kb boardsource/unicorne`.
