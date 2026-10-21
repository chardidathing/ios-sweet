/* redmi note 10 pro (sweet, sm7150), every address from the live fdt */
#pragma once

#define BOARD_NAME		"sweet"

#define FB_BASE			0x9c000000UL	/* reserved-memory cont_splash_region */
#define FB_W			1080
#define FB_H			2400
#define FB_STRIDE		(FB_W * 4)	/* a8r8g8b8, matches mainline simplefb */
/* video mode panel: it scans the splash buffer out by itself, no DISP_PP */

#define GICD_BASE		0x17a00000UL
#define GICR_BASE		0x17a60000UL
#define VTIMER_INTID		19	/* DT: <GIC_PPI 3 ...>, not the usual 27 */
#define PTIMER_INTID		18	/* DT: <GIC_PPI 2 ...> */

#define UFS_BASE		0x01d84000UL	/* ufshc@1d84000 */

#define IMEM_RESTART_REASON	0x146aa65cUL	/* qcom,msm-imem restart_reason@65c */
#define PSHOLD			0x0c264000UL
