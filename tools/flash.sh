#!/usr/bin/env bash
# Build one half and flash it.  Usage: tools/flash.sh left|right [pointer]
# Run via make (flash-left / flash-right) so QMK="uv run qmk" is set.
#   pointer: "" (none), trackpoint, trackball/pmw3389, trackball/pmw3360, azoteq, pimoroni
#
# Flashing steps: the half to flash must be the one plugged into the computer
# (its port labelled U).  Put it in bootloader mode either with the BOOT key in
# the layout (hold the sys_ctrl layer key, right ring finger east, and press
# left pinky west) or by double-tapping the RESET button on its underside.
set -euo pipefail
half=${1:?left|right}
pointer=${2:-}
keymap=${KEYMAP:-mal}
kb="svalboard/${pointer:+$pointer/}$half"
label=RPI-RP2
uf2="svalboard_$(echo "$kb" | tr / _ | sed 's/^svalboard_//')_${keymap}.uf2"

echo "== building $kb:$keymap"
${QMK:-qmk} compile -kb "$kb" -km "$keymap" -j"$(nproc)" >/tmp/qmk-flash-$half.log 2>&1 \
  || { tail -40 /tmp/qmk-flash-$half.log; echo "build failed, see /tmp/qmk-flash-$half.log"; exit 1; }
[ -f "$uf2" ] || { echo "expected $uf2 not found"; exit 1; }
echo "== built $uf2"

echo "== plug in the $half half and put it in bootloader mode (BOOT key, or double-tap RESET)"
echo "   waiting for the $label drive (ctrl-c to abort)..."
until [ -e /dev/disk/by-label/$label ]; do sleep 0.3; done
dev=$(readlink -f /dev/disk/by-label/$label)
sleep 0.5
mnt=$(findmnt -no TARGET "$dev" || true)
if [ -z "$mnt" ]; then
  udisksctl mount -b "$dev" >/dev/null
  mnt=$(findmnt -no TARGET "$dev")
fi
echo "== copying $uf2 to $mnt"
cp "$uf2" "$mnt/"
sync
udisksctl unmount -b "$dev" >/dev/null 2>&1 || true
echo "== done: $half half rebooting with new firmware"
