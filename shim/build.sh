#!/bin/bash
# Build the shim for one board (BOARD=sweet|pdx203, default sweet) and wrap it
# in a boot.img v2 that mirrors that phone's stock header (boards/$BOARD.sh).
set -euo pipefail
cd "$(dirname "$0")"
BOARD=${BOARD:-sweet}
. "boards/$BOARD.sh"
OUT=out/$BOARD
mkdir -p "$OUT"
# gnu cross toolchain if installed, otherwise clang + lld with the llvm binutils
if command -v aarch64-linux-gnu-gcc >/dev/null; then
	CC=aarch64-linux-gnu-gcc
	OBJCOPY=aarch64-linux-gnu-objcopy
	NM=aarch64-linux-gnu-nm
	READELF=aarch64-linux-gnu-readelf
	LDFLAGS="-Wl,--no-warn-rwx-segments"
else
	CC="clang --target=aarch64-linux-gnu"
	OBJCOPY=llvm-objcopy
	NM=llvm-nm
	READELF=llvm-readelf
	LDFLAGS="-fuse-ld=lld"
fi
CFLAGS="-O2 -ffreestanding -fno-builtin -nostdlib -fno-pic -mgeneral-regs-only -mstrict-align -fno-stack-protector -Wall -Wextra -DBOARD_${BOARD^^}"
SRCS="shim.c console.c mmu.c fdt.c loader.c ufs.c display.c"
for f in start.S $SRCS; do
	$CC $CFLAGS -c $f -o "$OUT/${f%.*}.o"
done
OBJS=$(for f in $SRCS; do printf '%s ' "$OUT/${f%.*}.o"; done)
# The image runs wherever ABL puts it with no relocation pass: only the
# header's image_size (start.o, linked at 0) may be an absolute address.
abs=$($READELF -r $OBJS | grep -c ABS64 || true)
[ "$abs" = 0 ] || { echo "error: $abs absolute relocations in C objects" >&2; exit 1; }
$CC $CFLAGS -static -T shim.ld -Wl,--build-id=none $LDFLAGS -Wl,-N \
	"$OUT/start.o" $OBJS -o "$OUT/shim.elf"
$OBJCOPY -O binary "$OUT/shim.elf" "$OUT/Image"
# ABL copies the file; pad to image_size so .bss/stacks exist as zeroed bytes.
size=$($NM "$OUT/shim.elf" | awk '$3=="_end"{print strtonum("0x"$1)}')
truncate -s "$size" "$OUT/Image"
# Ramdisk: an xnu payload (tools/mkpayload.py) if given as $1, else an empty
# newc cpio (ABL dislikes a zero-size ramdisk on some builds) -> diagnostics.
if [ -n "${1:-}" ]; then
	cp "$1" "$OUT/ramdisk.bin"
else
	(cd "$OUT" && rm -rf rd && mkdir rd && cd rd && find . | cpio -o -H newc --quiet | gzip -9 > ../ramdisk.bin)
fi
mkbootimg --kernel "$OUT/Image" --ramdisk "$OUT/ramdisk.bin" --dtb "$DTB" \
	$MKBOOTIMG_ARGS --cmdline "$CMDLINE" -o "$OUT/shim-boot.img"
# Host render of the console layout.
gcc -O1 -Wall -DBOARD_${BOARD^^} -o "$OUT/host_test" console.c host_test.c && "./$OUT/host_test"
ls -l "$OUT/Image" "$OUT/shim-boot.img"
