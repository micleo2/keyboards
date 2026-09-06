#!/usr/bin/env bash
# Build one board and flash it over the RP2040 UF2 bootloader.
#   tools/flash.sh <keyboard>        e.g. svalboard/trackball/pmw3389/right, boardsource/unicorne
# Run via make (flash-*), which sets QMK="uv run qmk", KEYMAP and QMK_HOME.
#
# Put the board in bootloader mode when asked: Svalboard, the half on the U
# port: sys_ctrl + left pinky centre (QK_BOOT) or double-tap RESET underneath;
# unicorne / lulu: the BOOT key in the layout or the button on the controller.
set -euo pipefail
kb=${1:?keyboard, e.g. boardsource/unicorne}
keymap=${KEYMAP:-micleo2}
label=RPI-RP2
uf2="$(echo "$kb" | tr / _)_${keymap}.uf2"

echo "== building $kb:$keymap"
${QMK:-qmk} compile -kb "$kb" -km "$keymap" -j"$(nproc)" >"/tmp/qmk-flash-$$.log" 2>&1 \
  || { tail -40 "/tmp/qmk-flash-$$.log"; echo "build failed, see /tmp/qmk-flash-$$.log"; exit 1; }
[ -f "$uf2" ] || { echo "expected $uf2 not found"; exit 1; }
echo "== built $uf2"

echo "== put the board in bootloader mode; waiting for the $label drive (ctrl-c to abort)..."
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
echo "== done: board rebooting with new firmware"
