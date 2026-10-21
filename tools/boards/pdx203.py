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
# phone has 8 GB, so the bank above 4 GB is at least 4 GiB. Boots, not yet
# checked against a live FDT.
PHYS_BASE = 0x100000000
MEM_SIZE = 0xfcc00000
HIGH_PHYS_BASE = PHYS_BASE
HIGH_MEM_SIZE = MEM_SIZE

GICD, GICD_SIZE = 0x17a00000, 0x10000
GICR, GICR_SIZE = 0x17a60000, 0x100000
# cont_splash_region@9c000000. The panel's default timing is 1096x2560 (the
# 4K mode is a second timing), a8r8g8b8, stride width x 4 (verified). It is a
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

# Samsung sec_ts at I2C 0x48 on qupv3_se13 (0xa94000, wrapper 1 local SE5):
# GCC vote 0x52008 bits 18-21 (wrapper core 2x/core, m/s ahb) and 27 (s5),
# RCG 0x18600, halt registers of those branches; pins 36/37 (qup13) 38 reset
# 39 irq in the TLMM SOUTH tile (0xf000000 + 0x500000). The IC is in-cell on
# the panel's rails ts_io (pm8150a_l1 = ldoc1, 1.8 V) and ts_vddh (pm8150a_l10
# = ldoc10, 3.296 V), which ABL powers for the splash, so the votes are
# optional. Coordinates come in the 4K space (sec,max_coords).
TOUCH = dict(
    protocol='sects', se=0x00a94000, gcc_vote=0x52008, gcc_vote_mask=(0x0f << 18) | (1 << 27),
    gcc_rcg=0x18600, gcc_halt=[0x18004, 0x18008, 0x23138, 0x23140, 0x185fc],
    tlmm=0x0f500000, sda=36, scl=37, mux=1, reset=38, irq=39,
    rails=[('ldoc1', 1800), ('ldoc10', 3296)], rails_optional=True, max_x=1644, max_y=3840)
# qcom,qmp-phy-init-seq of ssphy@88e8000 from the stock kona dtb, without the
# terminator: register offset, value, delay in microseconds
USB_SSPHY_SEQ = [
    0x1010, 0x01, 0, 0x101c, 0x31, 0, 0x1020, 0x01, 0, 0x1024, 0xde, 0,
    0x1028, 0x07, 0, 0x1030, 0xde, 0, 0x1034, 0x07, 0, 0x1050, 0x0a, 0,
    0x1060, 0x20, 0, 0x1074, 0x06, 0, 0x1078, 0x06, 0, 0x107c, 0x16, 0,
    0x1080, 0x16, 0, 0x1084, 0x36, 0, 0x1088, 0x36, 0, 0x1094, 0x1a, 0,
    0x10a4, 0x04, 0, 0x10ac, 0x14, 0, 0x10b0, 0x34, 0, 0x10b4, 0x34, 0,
    0x10b8, 0x82, 0, 0x10bc, 0x82, 0, 0x10c4, 0x82, 0, 0x10cc, 0xab, 0,
    0x10d0, 0xea, 0, 0x10d4, 0x02, 0, 0x10d8, 0xab, 0, 0x10dc, 0xea, 0,
    0x10e0, 0x02, 0, 0x110c, 0x02, 0, 0x1110, 0x24, 0, 0x1118, 0x24, 0,
    0x111c, 0x02, 0, 0x1158, 0x01, 0, 0x116c, 0x08, 0, 0x11ac, 0xca, 0,
    0x11b0, 0x1e, 0, 0x11b4, 0xca, 0, 0x11b8, 0x1e, 0, 0x11bc, 0x11, 0,
    0x1234, 0x60, 0, 0x1238, 0x60, 0, 0x123c, 0x11, 0, 0x1240, 0x02, 0,
    0x1284, 0xd5, 0, 0x1288, 0x00, 0, 0x129c, 0x12, 0, 0x1304, 0x40, 0,
    0x1408, 0x09, 0, 0x1414, 0x05, 0, 0x1430, 0x2f, 0, 0x1434, 0x7f, 0,
    0x143c, 0xff, 0, 0x1440, 0x0f, 0, 0x1444, 0x99, 0, 0x144c, 0x08, 0,
    0x1450, 0x08, 0, 0x1454, 0x00, 0, 0x1458, 0x04, 0, 0x14d4, 0x54, 0,
    0x14d8, 0x0c, 0, 0x14ec, 0x0f, 0, 0x14f0, 0x4a, 0, 0x14f4, 0x0a, 0,
    0x14f8, 0xc0, 0, 0x14fc, 0x00, 0, 0x1510, 0x77, 0, 0x151c, 0x04, 0,
    0x1524, 0x0e, 0, 0x1570, 0xff, 0, 0x1574, 0x7f, 0, 0x1578, 0x7f, 0,
    0x157c, 0x7f, 0, 0x1580, 0x97, 0, 0x1584, 0xdc, 0, 0x1588, 0xdc, 0,
    0x158c, 0x5c, 0, 0x1590, 0x7b, 0, 0x1594, 0xb4, 0, 0x15b4, 0x04, 0,
    0x15b8, 0x38, 0, 0x1460, 0xa0, 0, 0x15bc, 0x0c, 0, 0x14dc, 0x1f, 0,
    0x15c4, 0x10, 0, 0x1634, 0x60, 0, 0x1638, 0x60, 0, 0x163c, 0x11, 0,
    0x1640, 0x02, 0, 0x1684, 0xd5, 0, 0x1688, 0x00, 0, 0x169c, 0x12, 0,
    0x1704, 0x54, 0, 0x1808, 0x09, 0, 0x1814, 0x05, 0, 0x1830, 0x2f, 0,
    0x1834, 0x7f, 0, 0x183c, 0xff, 0, 0x1840, 0x0f, 0, 0x1844, 0x99, 0,
    0x184c, 0x08, 0, 0x1850, 0x08, 0, 0x1854, 0x00, 0, 0x1858, 0x04, 0,
    0x18d4, 0x54, 0, 0x18d8, 0x0c, 0, 0x18ec, 0x0f, 0, 0x18f0, 0x4a, 0,
    0x18f4, 0x0a, 0, 0x18f8, 0xc0, 0, 0x18fc, 0x00, 0, 0x1910, 0x77, 0,
    0x191c, 0x04, 0, 0x1924, 0x0e, 0, 0x1970, 0x7f, 0, 0x1974, 0xff, 0,
    0x1978, 0x3f, 0, 0x197c, 0x7f, 0, 0x1980, 0xa6, 0, 0x1984, 0xdc, 0,
    0x1988, 0xdc, 0, 0x198c, 0x5c, 0, 0x1990, 0x7b, 0, 0x1994, 0xb4, 0,
    0x19b4, 0x04, 0, 0x19b8, 0x38, 0, 0x1860, 0xa0, 0, 0x19bc, 0x0c, 0,
    0x18dc, 0x1f, 0, 0x19c4, 0x10, 0, 0x1cc4, 0xd0, 0, 0x1cc8, 0x07, 0,
    0x1ccc, 0x20, 0, 0x1cd8, 0x13, 0, 0x1cdc, 0x21, 0, 0x1d88, 0xa9, 0,
    0x1db0, 0x0a, 0, 0x1dc0, 0x88, 0, 0x1dc4, 0x13, 0, 0x1dd0, 0x0c, 0,
    0x1ddc, 0x4b, 0, 0x1dec, 0x10, 0, 0x1f18, 0xf8, 0, 0x1f38, 0x07, 0,
]

# USB30_PRIM on kona (gcc-kona.c): same GDSC and DWC3/QSCRATCH addresses, the
# clock branches at their kona offsets, no cfg_ahb2phy or clkref branch here,
# and a SNPS femto HS PHY (0x88e3000) the driver does not read.
USB = dict(
    gdscr=0x0f004, cbcr_master=0x0f010, cbcr_sleep=0x0f018, cbcr_utmi=0x0f01c,
    cbcr_cfg_noc=0x0f07c, cbcr_aggre=0x0f080,
    cbcr_aux=0x0f054, cbcr_com_aux=0x0f058, cbcr_pipe=0x0f05c,
    dwc3=0x0a600000, qscratch=0x0a6f8800,
    # the femto HS PHY (hsphy@88e3000), its EUD enable register, its GCC BCR
    # (GCC_QUSB2PHY_PRIM_BCR) and the DT qcom,param-override-seq (value, offset)
    hsphy=0x088e3000, eud=0x088e2000, hsphy_reset=0x12000, hsphy_override=[0x43, 0x70],
    # the USB3/DP combo QMP PHY (ssphy@88e8000): the pipe clock the DWC3 core
    # needs comes from its PLL, and ABL powers it down after fastboot. The GCC
    # resets are GCC_USB3_DP_PHY_PRIM_BCR (global) and GCC_USB3_PHY_PRIM_BCR,
    # ssphy_reg is the DT qcom,qmp-phy-reg-offset list (phy-msm-ssusb-qmp.c
    # enum order) and ssphy_seq the qcom,qmp-phy-init-seq (offset, value, delay us)
    # the apps SMMU (qsmmu-v500) that usb0 (stream id 0, anoc_1_tbu) sits
    # behind: the driver switches that stream to bypass before its first dma
    smmu=0x15000000, smmu_sid=0,
    ssphy=0x088e8000, ssphy_reset=[0x50008, 0x50000],
    ssphy_reg=[0x1c14, 0x1f08, 0x1f14, 0x1c40, 0x1c00, 0x1c44, 0xffff, 0x2a18,
               0x08, 0x04, 0x1c, 0x00, 0x10, 0x0c, 0x1c8c],
    ssphy_seq=USB_SSPHY_SEQ)

# The display processor (mdss_mdp@ae00000, offsets from the sde catalog in
# the stock dtb): ctl_0, lm_0, the qseed3lite scaler inside a vig pipe, the
# eight source pipes (four vig then four dma, so the pipes ABL staged for the
# splash can be found: vig_0 and vig_1, one per 548-pixel half) and the mdp's
# unsecure stream behind the apps SMMU (its address registers are 32 bits,
# the kernel's RAM is above 4 GB, so the stream gets a window). The kernel
# presents through it (bsd/dev/sweet_mdp.c), sweetfb_mdp=0 goes back to the
# cpu copy.
MDP = dict(base=0x0ae00000, ctl=0x2000, lm=0x45000, qseed=0xa00,
           sspp=[0x5000, 0x7000, 0x9000, 0xb000, 0x25000, 0x27000, 0x29000, 0x2b000],
           smmu=0x15000000, smmu_sid=0x820)

ECID = 0x5044583230330001  # 'PDX203' + 1, synthetic
