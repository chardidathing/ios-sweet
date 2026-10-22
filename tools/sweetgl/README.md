# sweetgl

`sweetgl.dylib` puts CoreAnimation's own OpenGL ES renderer on the Adreno
650 through Mesa's freedreno driver. After
[ios-sailfish](https://github.com/joranv1/ios-sailfish) by joranv1 (Pixel 1,
Adreno 530), ported to the Xperia 1 II. iOS has no Metal here, so CA falls
back to its GLES renderer (`CA::OGL::GLESContext`), which only ever talks to
EAGL through seven `EAGLContext` methods and a 1036 slot GLI dispatch table
it gets from `getMacroContextPrivate`. The dylib, inserted into backboardd,
replaces those methods for the contexts it makes and fills the table with
Mesa's `gl*` entry points, so the whole UI renders on the GPU.

| File | What |
| --- | --- |
| `eagl.c`, `eagl.h` | the EAGL shim: the swapped methods, IOSurfaces as texture storage (GEM import, `get_egl_image`), the hand written dispatch slots, GL_TEXTURE_RECTANGLE and framebuffer fetch emulation, QuartzCore in-memory fixes |
| `sweetgl.c`, `sweetgl.h` | a minimal gallium frontend: one `pipe_screen` over `sweet_drm.c`, surfaceless GLES contexts, the load time self test |
| `sweet_drm.c`, `sweet_drm.h`, `include/xf86drm.h` | libdrm and the msm DRM ioctls emulated in user space over the SweetGPU IOKit user client |
| `sweet_gpu_abi.h` | the kernel contract: selectors 10 to 16 and `struct sweet_gpu_submit`. The kernel's `bsd/dev/sweet_gpu.h` and `iokit/Kernel/arm/SweetGPU.cpp` must match it |
| `gen-dispatch.py`, `ios-dispatch.txt` | the GLI dispatch layout of GLEngine 20H392 and the generator of `out/dispatch.c` |
| `layerdump.c` | SpringBoard side research aid and the vibrant fill workaround |
| `mesa.patch`, `mesa-setup.sh`, `ios-cross.txt`, `build.sh` | the Mesa build for iOS and the dylib link |
| `install.sh`, `extents.py`, `push.sh` | getting the dylib into the root image and onto the phone |

## What changed from ios-sailfish

- Adreno 650 (a6xx) instead of the 530. `sweet_drm.c` answers
  `MSM_PARAM_GPU_ID` from the chip id the kernel reports (0x0605xxxx becomes
  650, which is what Mesa's device table matches first), GMEM size and base
  come from the kernel too (1 MiB, base 0 on the a650 family). Mesa reads
  nothing else from the kernel at the DRM version we claim (1.7, softpin):
  `VA_SIZE`, `UCHE_TRAP_BASE` and the UBWC parameters are only queried past
  that or by turnip, and Mesa's defaults for the a650 apply.
- `mesa.patch` is cut against Mesa main `45a949a91f098b80b999636008e9facbd5633408`
  (2026-10-03), the exact commit ios-sailfish's patch index lines point at.
  Its a5xx hunk (64 byte pitches for imported linear surfaces in
  `fd_layout_resource_for_handle`) does not run on a6xx, where
  `fd6_layout_resource_for_handle` goes through `fdl6_layout_image`
  instead. That path already takes 64 byte pitches for 1, 2 and 4 byte
  pixels, but wants 128 for 8 byte ones (RGBA16F) because of GMEM stores,
  so the a6xx hunk drops that extra alignment for explicit layouts at 64
  byte pitches. We only render in sysmem (`FD_MESA_DEBUG=sysmem`, set in
  `sweetgl.c`), so nothing is stored through GMEM.
- QuartzCore patch sites. The dylib writes four entries of
  `tex_fragment_shaders` and the uniform switch of `create_shader` in
  QuartzCore's memory (texture functions CA's GL renderer has no shader
  for), and under `SWEETGL_TRACE` hooks a dozen renderer functions. Those
  are absolute addresses in the shared cache. Ours is the iPhone X
  (`iPhone10,3`) 20H392 cache, not the iPhone 8 one, and QuartzCore
  1045.17.2 sits exactly 0x4000 higher in it (same binary, every site
  checked byte for byte against our cache with `ipsw`). `eagl.c` carries
  the shifted addresses and still verifies the bytes at run time before
  writing.
- The GLI dispatch layout was regenerated from our GLEngine
  (`ipsw dyld disass CACHE --symbol _gliInitDispatchTable`, then
  `tools/gles-dispatch-layout.py`) and is identical to ios-sailfish's,
  all 410 named slots of the 1036.
- Build and install: Xcode comes from `xcrun` instead of a `research/xcode15`
  tree, the dylib is built on GitHub's macOS runners, and the install goes
  through the Linux root image builder and the Lineage recovery.

## Building

The workflow `.github/workflows/sweetgl.yml` (`macos-14`) fetches the pinned
Mesa commit, applies `mesa.patch`, configures with `mesa-setup.sh`, links
with `build.sh` and uploads the artifact `sweetgl` (`sweetgl.dylib`, 64 MiB
padded, `sweetgl-unpadded.dylib`, the generated `dispatch.c`, checksums). It
runs on pushes to `gles-user` touching `tools/sweetgl/` and on
`workflow_dispatch`. The Mesa source and build directory are cached under one
key (the build dir keeps absolute paths and ninja goes by mtimes, so they only
work as a pair).

```sh
gh workflow run sweetgl.yml --ref gles-user -R chardidathing/ios-sweet
gh run download RUN_ID -R chardidathing/ios-sweet -n sweetgl -D tools/sweetgl/out
```

On a Mac with Xcode the same scripts work locally: clone Mesa at the pinned
commit into `research/mesa`, `git apply tools/sweetgl/mesa.patch`, then
`tools/sweetgl/mesa-setup.sh` and `tools/sweetgl/build.sh` (`MESA_SRC` and
`MESA_BUILD` override the paths). meson, ninja, bison > 2.3, flex, python
mako and yaml are needed.

## Installing

The root is an HFS+ image flashed to the start of `userdata`, and the
recovery kernel cannot mount HFS+. The dylib goes in on the host, and its
block runs are recorded so later versions can be written over the same
blocks from recovery without reflashing 16 GB. `build.sh` pads the dylib to
64 MiB so the file keeps one size and the runs stay valid across versions.

Either when building the root:

```sh
SWEETGL_DYLIB=tools/sweetgl/out/sweetgl.dylib tools/mkiosroot.sh OS.dmg SYSTEMOS.dmg APPOS.dmg ios16-root.img
```

or into an existing image:

```sh
sudo tools/sweetgl/install.sh ios16-root.img          # out/sweetgl.dylib by default
```

Both leave `ios16-root.img.sweetgl-extents.txt` next to the image: one
"offset length" line per run, in bytes from the start of the volume
(`extents.py`, FIBMAP on the mounted image). Keep it with the image. Then
flash the root as the README says.

Later versions, with the phone in the Lineage recovery (`adb root` works
there, same as `tools/sweet-log-pull.sh`):

```sh
tools/sweetgl/push.sh ios16-root.img.sweetgl-extents.txt    # [-s SERIAL], [DYLIB]
```

It checks that the first run starts with a Mach-O header before writing
anything (wrong image or extents stop it there), writes each run with `dd`,
drops the page cache, reads everything back and compares the sha256. The
extents file belongs to one flashed image: after reflashing a new root,
use the new one.

## Boot-args and environment

The kernel side (branches `kernel-generic` and `gpu-kernel`) has to provide
the `sweetenv` boot-arg (ios-sailfish patches 0104 and 0163), the SweetGPU
user client of `sweet_gpu_abi.h`, and the IOSurface fixes (their 0152 to
0162). With those, on top of the usual pdx203 boot-args:

| Boot-arg | Why |
| --- | --- |
| `sweetenv=backboardd:DYLD_INSERT_LIBRARIES=/usr/lib/sweetgl.dylib` | loads the dylib into backboardd (the renderer lives there) |
| `cs_enforcement_disable=1` | the dylib is ad-hoc signed, and `eagl.c` writes QuartzCore's text and const pages |
| (`sweetnull`, default `backboardd,SpringBoard`) | writes to `/dev/null` from those processes are teed into the kernel log (patch 0048), which is how `sweet_drm_log` reports (`sweetgl: ...` lines). Nothing to add unless it was turned off |
| the GPU service switch | whatever the `gpu-kernel` branch names it (sailfish: `sweetgpu=8`) |

Several variables go after the process name separated by commas, and
several processes by `;`, e.g.
`sweetenv=backboardd:DYLD_INSERT_LIBRARIES=/usr/lib/sweetgl.dylib,SWEETGL_TEST=1;SpringBoard:DYLD_INSERT_LIBRARIES=/usr/lib/sweetgl.dylib`.

| Variable | Effect |
| --- | --- |
| `SWEETGL_TEST=1` | at load, on a thread: an offscreen triangle drawn, read back and checked, `MESA GLES ON THE ADRENO WORKS` or `WRONG` in the log |
| `SWEETGL_GLERR=1` | `glGetError` after every dispatch call, logged |
| `SWEETGL_TRACE=1` | draw tracing, shader sources, the QuartzCore research hooks |
| `SWEETGL_LAYERDUMP=1` | in SpringBoard: periodic dumps of the filtered layers |
| `FD_MESA_DEBUG`, `IR3_SHADER_DEBUG` | Mesa's own knobs; `sweetgl.c` defaults them to `sysmem,nofp16` and `nofp16` |

In SpringBoard the dylib only installs the vibrant fill workaround
(`layerdump.c`), the EAGL shim is for backboardd.

## Not verified

Nothing here has run on the phone: the kernel half is being written on
another branch and the dylib cannot be loaded anywhere else. The a6xx
specifics (sysmem rendering through CA's surfaces, the 64 byte pitch
relaxation for RGBA16F, Mesa's a650 defaults with no UBWC parameters from
the kernel) are what the sources say, not what the hardware did.
