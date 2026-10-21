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

# Goodix GT9896 on GENI SE7 (qupv3 wrapper 1, local SE1) for bsd/dev/sweet_touch.c:
# GCC vote register and bits for the wrapper AHB/core clocks and the SE, the
# SE's RCG, the branch halt registers to check, the TLMM NORTH tile, pins,
# the board power enable and the L11C rail voted through RPMh.
TOUCH = dict(
    protocol='goodix', se=0x00a84000, gcc_vote=0x5200c, gcc_vote_mask=(0x0f << 18) | (1 << 23),
    gcc_rcg=0x18148, gcc_halt=[0x18004, 0x18008, 0x1800c, 0x18010, 0x18144],
    tlmm=0x03900000, sda=6, scl=7, mux=1, reset=8, irq=9, power_gpio=90,
    rails=[('ldoc11', 3200)], max_x=1080, max_y=2400)
# DWC3 USB live log (bsd/dev/sweet_usb.c): the USB30_PRIM GDSC and clock branch
# registers in GCC, the controller, its QSCRATCH wrapper and the QUSB2 PHY.
USB = dict(
    gdscr=0x0f004, cbcr_master=0x0f010, cbcr_sleep=0x0f014, cbcr_utmi=0x0f018,
    cbcr_cfg_noc=0x0502c, cbcr_aggre=0x8201c, cbcr_ahb2phy=0x6a004, cbcr_clkref=0x8c010,
    dwc3=0x0a600000, qscratch=0x0a6f8800, qusb2=0x088e2000)

ECID = 0x5357454554000001  # 'SWEET' + 1, synthetic
