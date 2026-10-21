/*
 * Command mode panels (pdx203) show the splash only because ABL pushed one
 * frame. With pingpong autorefresh on, the MDP resends the framebuffer on
 * every panel TE pulse, so the shim and xnu can draw into it as if it were a
 * video mode panel. Video mode boards define no DISP_PP and get the stubs.
 * Register offsets: techpack/display/msm/sde/sde_hw_{pingpong,ctl}.c.
 */
#include <stdint.h>
#include "board.h"
#include "console.h"
#include "display.h"

#ifdef DISP_PP
#define PP_TEAR_CHECK_EN	0x00
#define PP_SYNC_CONFIG_VSYNC	0x04
#define PP_SYNC_CONFIG_HEIGHT	0x08
#define PP_SYNC_WRCOUNT		0x0c
#define PP_VSYNC_INIT_VAL	0x10
#define PP_SYNC_THRESH		0x18
#define PP_START_POS		0x1c
#define PP_RD_PTR_IRQ		0x20
#define PP_LINE_COUNT		0x2c
#define PP_AUTOREFRESH_CONFIG	0x30
#define CTL_TOP			0x14
#define CTL_FLUSH		0x18

#define AUTOREFRESH_EN		(1u << 31)	/* low bits: refresh every n TE pulses */
#define VSYNC_COUNTER_EN	(1u << 19)
#define SYNC_THRESH		4		/* start and continue, the driver's defaults */

static uint32_t pp_before, pp_after, te_before, ctl_top, ctl_flush;

static uint32_t rd(uintptr_t a)
{
	return *(volatile uint32_t *)a;
}

static void wr(uintptr_t a, uint32_t v)
{
	*(volatile uint32_t *)a = v;
	__asm__ volatile("dsb sy" ::: "memory");
}

void display_setup(void)
{
	pp_before = rd(DISP_PP + PP_AUTOREFRESH_CONFIG);
	te_before = rd(DISP_PP + PP_TEAR_CHECK_EN);
	ctl_top = rd(DISP_CTL + CTL_TOP);
	ctl_flush = rd(DISP_CTL + CTL_FLUSH);
	if (!(te_before & 1)) {
		/* autorefresh counts TE pulses, so tearcheck must run. same values the
		 * linux cmd encoder programs, external TE, hw vsync effectively off */
		wr(DISP_PP + PP_SYNC_CONFIG_VSYNC, VSYNC_COUNTER_EN | DISP_VSYNC_COUNT);
		wr(DISP_PP + PP_SYNC_CONFIG_HEIGHT, 0xfff0);
		wr(DISP_PP + PP_VSYNC_INIT_VAL, FB_H);
		wr(DISP_PP + PP_RD_PTR_IRQ, FB_H + 1);
		wr(DISP_PP + PP_START_POS, FB_H);
		wr(DISP_PP + PP_SYNC_THRESH, (SYNC_THRESH << 16) | SYNC_THRESH);
		wr(DISP_PP + PP_SYNC_WRCOUNT, FB_H + SYNC_THRESH + 1);
		wr(DISP_PP + PP_TEAR_CHECK_EN, 1);
	}
	wr(DISP_PP + PP_AUTOREFRESH_CONFIG, AUTOREFRESH_EN | 1);
	pp_after = rd(DISP_PP + PP_AUTOREFRESH_CONFIG);
}

void display_report(void)
{
	con_hex2("DISP", "pp=", pp_before, "now=", pp_after);
	con_hex2("DISP", "te=", te_before, "top=", ctl_top);
	con_hex2("DISP", "flush=", ctl_flush, "line=", rd(DISP_PP + PP_LINE_COUNT));
}
#else
void display_setup(void)
{
}

void display_report(void)
{
}
#endif
