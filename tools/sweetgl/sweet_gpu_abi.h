/*
 * sweetgl <-> kernel contract: the SweetGPU iokit user client (selectors 10
 * to 16) as ios-sailfish defined it (joranv1, xnu patches 0138, 0150, 0151,
 * 0155, 0156). the kernel's bsd/dev/sweet_gpu.h and
 * iokit/Kernel/arm/SweetGPU.cpp must match this file exactly, the two
 * halves are built and shipped separately (the dylib through sweetgl.yml,
 * the kernel through xnu.yml) and only this header ties them together.
 *
 * all calls go through IOConnectCallScalarMethod / IOConnectCallMethod on a
 * connection to the service named SWEET_GPU_SERVICE (type 0). every
 * selector but SWEET_GPU_WAIT answers kIOReturnNotReady until the gpu is up
 * (it comes up a while after boot, callers retry).
 *
 *   10 bo new      in: size                 out: handle, gpu va, user address
 *                  zeroed wired memory, page rounded (16 KiB), cached in
 *                  the caller and uncached for the gpu, max 256 MiB per bo
 *                  and 768 MiB per client
 *   11 bo free     in: handle               waits for the last submit listing it
 *   12 bo import   in: iosurface id         out: handle, gpu va, size
 *                  the surface's own pages, mapped as they are
 *   13 submit      struct in: struct sweet_gpu_submit, then
 *                  struct sweet_gpu_ib[nr_ibs], then uint32_t handles[nr_bos]
 *                  (every bo the ibs touch)   out: sequence number
 *                  the cpu cache is cleaned and invalidated over every listed
 *                  bo before the ring runs, so cpu writes reach memory and
 *                  no stale lines sit over what the gpu writes
 *   14 wait        in: sequence number, timeout ms (0 polls, capped at
 *                  60000)   kIOReturnSuccess once completed, kIOReturnTimeout,
 *                  kIOReturnNotReady when the gpu is off or declared hung
 *   15 info        out: chip id, gmem size, gmem base, max freq hz, 0
 *                  (the fifth value carried the fence page once, it is
 *                  0 now and waits poll through 14)
 *   16 bo cpu prep in: handle               kIOReturnBusy while its last
 *                  submit runs, else the cpu's cached lines over the bo are
 *                  dropped so it sees the gpu's writes
 *
 * the gpu runs the submitted streams as they are, in one address space
 * shared by every client. fine for a single user bring-up device, nothing
 * else.
 */
#ifndef SWEET_GPU_ABI_H
#define SWEET_GPU_ABI_H

#include <stdint.h>

#define SWEET_GPU_SERVICE       "SweetGPU"

#define SWEET_GPU_BO_NEW        10
#define SWEET_GPU_BO_FREE       11
#define SWEET_GPU_BO_IMPORT     12
#define SWEET_GPU_SUBMIT        13
#define SWEET_GPU_WAIT          14
#define SWEET_GPU_INFO          15
#define SWEET_GPU_BO_CPU_PREP   16

/* selector 13: the header of the structure input, followed by the ibs and the handles */
struct sweet_gpu_submit {
	uint32_t nr_ibs, nr_bos;
};

/* one CP_INDIRECT_BUFFER: dwords at a gpu va inside a listed bo */
struct sweet_gpu_ib {
	uint64_t iova;
	uint32_t dwords;
	uint32_t pad;
};

#define SWEET_GPU_MAX_IBS       256u
#define SWEET_GPU_MAX_BOS       16384u
#define SWEET_GPU_MAX_SUBMIT    (1u << 20)      /* bytes of structure input */
#define SWEET_GPU_WAIT_MAX_MS   60000u

/* selector 15 scalar outputs */
#define SWEET_GPU_INFO_CHIP_ID  0       /* core << 24 | major << 16 | minor << 8 | patch, 0x0605xxxx on the adreno 650 */
#define SWEET_GPU_INFO_GMEM     1       /* bytes, 1 MiB on the adreno 650 */
#define SWEET_GPU_INFO_GMEM_BASE 2      /* 0 on the a650 family (a6xx before it: 0x100000) */
#define SWEET_GPU_INFO_MAX_FREQ 3       /* hz, what the kernel votes the gpu to */
#define SWEET_GPU_INFO_RESERVED 4
#define SWEET_GPU_INFO_COUNT    5

#endif
