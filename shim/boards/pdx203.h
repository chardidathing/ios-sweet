/*
 * sony xperia 1 ii (pdx203, sm8250 "kona"), addresses from the stock boot.img
 * dtb and sony's kernel source, see docs/PDX203.md for what is verified
 */
#pragma once

#define BOARD_NAME		"pdx203"

/* cont_splash_region@9c000000, 0x2300000 long. the panel's default timing is
 * 1096x2560 (4k is a second timing), stride assumed width x 4 */
#define FB_BASE			0x9c000000UL
#define FB_W			1096
#define FB_H			2560
#define FB_STRIDE		(FB_W * 4)

/* command mode panel, so the mdp only sends a frame when started. display.c
 * turns on pingpong autorefresh, offsets from kona-sde.dtsi and the sde driver
 * (mdp_phys 0xae00000, ctl_0 +0x2000, pingpong_0 +0x71000) */
#define DISP_CTL		0x0ae02000UL
#define DISP_PP			0x0ae71000UL
/* vsync counter for the te config if abl left tearcheck off:
 * 19.2 MHz / (vtotal 2584 lines * 60 fps) */
#define DISP_VSYNC_COUNT	123

#define GICD_BASE		0x17a00000UL
#define GICR_BASE		0x17a60000UL
#define VTIMER_INTID		27	/* DT: <GIC_PPI 11 ...>, the usual numbering */
#define PTIMER_INTID		30	/* DT: <GIC_PPI 14 ...> */

#define UFS_BASE		0x01d84000UL	/* ufshc@1d84000, userdata is on lun 0 (sda) */

#define IMEM_RESTART_REASON	0x146bf65cUL	/* qcom,msm-imem@146bf000 restart_reason@65c */
#define PSHOLD			0x0c264000UL
