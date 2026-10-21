"""Sony Xperia 1 II (pdx203, Qualcomm SM8250 / Snapdragon 865).

Addresses come from the stock boot.img DTB (kona) and Sony's kernel source
(arch/arm64/boot/dts/somc/kona-edo-*). See docs/PDX203.md for what has been
verified on the phone and what has not.
"""
NAME = 'pdx203'
COMPATIBLE = ['sony,pdx203', 'qcom,sm8250']

# Kernel-managed RAM: the upper DDR bank, as on sweet. The boot.img DTB has no
# memory node (ABL fills it in), so this is the sweet layout carried over:
# every fixed kona carve-out is in the low bank (0x80000000-0xffd01000) and the
# phone has 8 GB, so the bank above 4 GB is at least 4 GiB. Unverified.
PHYS_BASE = 0x100000000
MEM_SIZE = 0xfcc00000
HIGH_PHYS_BASE = PHYS_BASE
HIGH_MEM_SIZE = MEM_SIZE

GICD, GICD_SIZE = 0x17a00000, 0x10000
GICR, GICR_SIZE = 0x17a60000, 0x100000
# cont_splash_region@9c000000. The panel's default timing is 1096x2560 (the
# 4K mode is a second timing), a8r8g8b8, stride assumed width x 4. It is a
# command mode panel: the shim turns on MDP autorefresh so the panel keeps
# fetching the buffer (shim/display.c).
FB, FB_SIZE = 0x9c000000, 0x2300000
FB_W, FB_H, FB_STRIDE = 1096, 2560, 1096 * 4
UFS, UFS_SIZE = 0x01d84000, 0x3000
TIMEBASE = 19200000
# kona uses the usual timer PPI numbers 13/14/11/10: virtual timer INTID 16 + 11
VTIMER_INTID = 27

# 0-3 Cortex-A55, 4-6 Cortex-A77, 7 the A77 prime core (MPIDR Aff1 = core)
CPU_COMPATIBLE = 'qcom,kryo585'
CPU_HZ = [1804800000] * 4 + [2419200000] * 3 + [2841600000]

# Power on the PM8150 PON block (SID 0), volume-up on its RESIN input,
# volume-down on PM8150 GPIO1 (active low), from Sony's gpio_keys and pon nodes.
KEYS = dict(pon_ppid=0x008, gpio_ppid=0x0c0, gpio_base=0xc000, gpio_key=2, resin_key=1)
# Touch is a Samsung sec_ts at I2C 0x48 on qupv3_se13 (0xa94000): not ported
# yet, so the sweet Goodix driver stays off. Same for the sweet USB driver
# (different HS PHY).
TOUCH = False
USB = False

ECID = 0x5044583230330001  # 'PDX203' + 1, synthetic
