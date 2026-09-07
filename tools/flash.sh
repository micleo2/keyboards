#!/usr/bin/env bash
# Flash one built firmware over the RP2040 UF2 bootloader.
#   tools/flash.sh <file.uf2>        e.g. build/boardsource_unicorne_micleo2.uf2
# Run via make (flash-*), which builds the board first and passes its .uf2.
#
# Put the board in bootloader mode when asked: Svalboard, the half on the U
# port: sys_ctrl + left pinky centre (QK_BOOT) or double-tap RESET underneath;
# unicorne / lulu: the BOOT key in the layout or the button on the controller.
set -euo pipefail
uf2=${1:?path to a .uf2, e.g. build/boardsource_unicorne_micleo2.uf2}
label=RPI-RP2
[ -f "$uf2" ] || { echo "no such firmware: $uf2"; exit 1; }

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
