# boot.img v2 header of the stock sony image (tools/unpack_bootv2.py), the dtb
# section is its kona dtb set (abl picks the soc revision out of it)
DTB=../dtb/pdx203/dtb
MKBOOTIMG_ARGS="--header_version 2 --base 0 --kernel_offset 0x8000 --ramdisk_offset 0x2000000 --tags_offset 0x1e00000 --dtb_offset 0x1f00000 --pagesize 4096 --os_version 11.0.0 --os_patch_level 2021-06"
CMDLINE="androidboot.hardware=pdx203"
