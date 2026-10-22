#!/bin/sh
# after ios-sailfish by joranv1, ported to the xperia 1 ii (pdx203)
# write out/sweetgl.dylib over /usr/lib/sweetgl.dylib on the phone from the
# lineage recovery (adb root): the recovery cannot mount hfs+, so only the
# file's own blocks on userdata are rewritten, at the offsets install.sh (or
# mkiosroot.sh with SWEETGL_DYLIB) recorded for this image. refuses unless
# the first run starts with a mach-o header, reads everything back after
# dropping the caches and compares.
#   tools/sweetgl/push.sh [-s SERIAL] EXTENTS [DYLIB]
set -e
H=$(cd "$(dirname "$0")" && pwd)
ADB=adb
if [ "${1:-}" = "-s" ]; then
	ADB="adb -s $2"
	shift 2
fi
E=${1:?usage: push.sh [-s SERIAL] IMG.sweetgl-extents.txt [DYLIB]}
O=${2:-$H/out/sweetgl.dylib}
PAD=67108864
[ "$(stat -c %s "$O")" = $PAD ] || { echo "$O is not 64 MiB"; exit 1; }
[ "$(awk '{n += $2} END {print n}' "$E")" = $PAD ] || { echo "$E does not cover 64 MiB"; exit 1; }
$ADB root >/dev/null 2>&1 || true
$ADB wait-for-device
dev=$($ADB shell 'for d in /dev/block/by-name/userdata /dev/block/bootdevice/by-name/userdata; do [ -e $d ] && readlink -f $d && break; done' | tr -d '\r')
[ -n "$dev" ] || { echo "userdata block device not found"; exit 1; }
first=$(head -1 "$E" | cut -d' ' -f1)
magic=$($ADB exec-out "dd if=$dev bs=4096 skip=$((first / 4096)) count=1 2>/dev/null | head -c 4 | od -An -tx1" | tr -d ' \r\n')
[ "$magic" = cffaedfe ] || { echo "$dev at $first does not start with a mach-o header ($magic), wrong image or extents"; exit 1; }
$ADB push "$O" /tmp/sweetgl.dylib >/dev/null
# one dd per run: the file's offset moves along with the volume offset
src=0
while read -r off len; do
	$ADB shell "dd if=/tmp/sweetgl.dylib of=$dev bs=4096 skip=$((src / 4096)) seek=$((off / 4096)) count=$((len / 4096)) conv=notrunc 2>/dev/null"
	src=$((src + len))
done < "$E"
$ADB shell 'sync; echo 3 > /proc/sys/vm/drop_caches; rm -f /tmp/back'
while read -r off len; do
	$ADB shell "dd if=$dev bs=4096 skip=$((off / 4096)) count=$((len / 4096)) 2>/dev/null >> /tmp/back"
done < "$E"
want=$(sha256sum "$O" | cut -d' ' -f1)
got=$($ADB shell 'sha256sum /tmp/back' | cut -d' ' -f1 | tr -d '\r')
$ADB shell 'rm -f /tmp/back /tmp/sweetgl.dylib'
[ "$want" = "$got" ] || { echo "readback differs: $got"; exit 1; }
echo "VERIFY OK: $(echo "$want" | cut -c1-16)"
