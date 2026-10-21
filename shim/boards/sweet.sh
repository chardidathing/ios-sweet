# boot.img v2 header of the stock pixelos image (tools/unpack_bootv2.py on the backup)
DTB=../dtb/boot_unpacked/dtb
MKBOOTIMG_ARGS="--header_version 2 --base 0 --kernel_offset 0x8000 --ramdisk_offset 0x1000000 --tags_offset 0x100 --dtb_offset 0x1f00000 --pagesize 4096 --os_version 17.0.0 --os_patch_level 2035-06"
CMDLINE="console=null"
