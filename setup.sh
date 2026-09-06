#!/usr/bin/env bash
# Fresh machine: everything needed to build, flash and feed the desktop viewer.
# Re-runnable.  NO_SUDO=1 skips the pacman and udev steps.
set -euo pipefail
cd "$(dirname "$0")"

if [ -z "${NO_SUDO:-}" ]; then
  sudo pacman -S --needed git uv arm-none-eabi-gcc arm-none-eabi-newlib udisks2 python-hid
fi

# firmware trees (svalboard fork on branch mal, upstream qmk_firmware pinned)
git submodule update --init --recursive --depth 1

# the qmk CLI, pinned (the Svalboard tree's Python helpers need 3.12).  No
# user.qmk_home on purpose: the Makefile passes QMK_HOME per board, and the CLI
# would prefer a configured value over the environment.
uv sync
uv run qmk config user.overlay_dir="$PWD" \
  user.keymap=micleo2 user.keyboard=svalboard/trackball/pmw3389/left >/dev/null

if [ -z "${NO_SUDO:-}" ]; then
  # let the logged-in user open the boards' raw HID nodes (quickshell's qmk-bridge.py)
  sudo install -m 644 desktop/udev/70-qmk.rules /etc/udev/rules.d/
  sudo udevadm control --reload && sudo udevadm trigger --subsystem-match=hidraw
fi

# what the desktop layout viewer draws
make export
echo "setup done: try  make unicorne  or  make svalboard-right"
