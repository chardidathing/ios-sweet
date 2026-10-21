"""Redmi Note 10 Pro (sweet, Qualcomm SM7150 / Snapdragon 732G).

Every MMIO address comes from the sweet live FDT (see NOTES.md).
"""
NAME = 'sweet'
COMPATIBLE = ['xiaomi,sweet', 'qcom,sm7150']

# Kernel-managed RAM: above every Qualcomm XPU carve-out (see NOTES.md)
PHYS_BASE = 0xb0000000
MEM_SIZE = 0x4d000000
# --highmem (phone only): the whole upper DDR bank. The live FDT memory node is
# <0x80000000 2G>, <0x1_00000000 0xfcc00000>; every fixed reserved-memory
# carve-out is in the low bank and the dynamic pools are limited below 4G.
HIGH_PHYS_BASE = 0x100000000
HIGH_MEM_SIZE = 0xfcc00000

GICD, GICD_SIZE = 0x17a00000, 0x10000
GICR, GICR_SIZE = 0x17a60000, 0x100000
# ABL's continuous-splash framebuffer (cont_splash_region), a8r8g8b8, video
# mode panel that scans it out by itself
FB, FB_SIZE = 0x9c000000, 0x1700000
FB_W, FB_H, FB_STRIDE = 1080, 2400, 1080 * 4
# Internal UFS host (ufshc@1d84000 "ufs_mem")
UFS, UFS_SIZE = 0x01d84000, 0x3000
TIMEBASE = 19200000
# Qualcomm numbers the timer PPIs 1/2/3/0: the virtual timer is INTID 16 + 3
VTIMER_INTID = 19

# All eight cores in physical-core order (MPIDR Aff1 = core): 0-5 Cortex-A55,
# 6-7 Cortex-A76. The kernel's SweetCPU matches CPU_COMPATIBLE.
CPU_COMPATIBLE = 'qcom,kryo470'
CPU_HZ = [1804800000] * 6 + [2304000000] * 2

# PMIC key wiring for bsd/dev/sweet_keys.c: power and volume-down (RESIN) on
# the PM6150 PON block, volume-up on PM6150L GPIO2 (SPMI SID 4).
KEYS = dict(pon_ppid=0x008, gpio_ppid=0x4c1, gpio_base=0xc100, gpio_key=1, resin_key=2)
# Goodix GT9896 on GENI SE7 (bsd/dev/sweet_touch.c) and the DWC3 USB live log
# (bsd/dev/sweet_usb.c) are wired for this board only.
TOUCH = True
USB = True

ECID = 0x5357454554000001  # 'SWEET' + 1, synthetic
