#!/bin/bash
# put sweetgl.dylib into a root image made by tools/mkiosroot.sh and record
# where its blocks are, so push.sh can rewrite it in place later without
# reflashing the whole root.
#   sudo tools/sweetgl/install.sh IMG [DYLIB]      (DYLIB default out/sweetgl.dylib)
# writes IMG.sweetgl-extents.txt next to the image. the dylib must be the
# 64 MiB padded one from build.sh (the size is what keeps the extents fixed).
set -euo pipefail
H=$(cd "$(dirname "$0")" && pwd)
[[ $# -ge 1 ]] || { sed -n '2,7p' "$0"; exit 2; }
img=$1 dylib=${2:-$H/out/sweetgl.dylib}
[[ $(stat -c %s "$dylib") == 67108864 ]] || { echo "$dylib is not 64 MiB, build it with build.sh" >&2; exit 1; }
[[ $(id -u) == 0 ]] || { echo "run as root (mount, FIBMAP)" >&2; exit 1; }
work=$(mktemp -d)
trap 'mountpoint -q "$work" && umount "$work"; rmdir "$work"' EXIT
# linux only mounts a journaled hfs+ volume read-write after fsck, like the readme
fsck.hfsplus -f -y "$img" | grep -v 'Illegal name' || true
mount -t hfsplus -o loop,force "$img" "$work"
install -m 0755 -o 0 -g 0 "$dylib" "$work/usr/lib/sweetgl.dylib"
sync
python3 -I "$H/extents.py" "$work/usr/lib/sweetgl.dylib" > "$img.sweetgl-extents.txt"
umount "$work"
fsck.hfsplus -f -n "$img"
echo "installed /usr/lib/sweetgl.dylib, extents in $img.sweetgl-extents.txt"
