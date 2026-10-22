#!/usr/bin/env python3
"""extents.py FILE: where FILE's blocks sit on its volume, one "offset length"
line per run (bytes from the start of the volume), for writing a file over
its own blocks on the phone (push.sh). FILE is on the hfs+ root image
mounted on linux (FIBMAP, so run as root). the image is flashed to the
start of userdata, so volume offsets are partition offsets.
"""
import array, fcntl, os, sys

FIBMAP = 1

if len(sys.argv) != 2:
    sys.exit(__doc__)
path = sys.argv[1]
size = os.stat(path).st_size
bs = os.statvfs(path).f_bsize
if bs % 4096:
    sys.exit('block size %d is not a multiple of 4096' % bs)
fd = os.open(path, os.O_RDONLY)
runs = []
for blk in range((size + bs - 1) // bs):
    arg = array.array('i', [blk])
    fcntl.ioctl(fd, FIBMAP, arg, True)
    phys = arg[0]
    if phys == 0:
        sys.exit('block %d of %s is not allocated' % (blk, path))
    if runs and runs[-1][0] + runs[-1][1] == phys * bs:
        runs[-1][1] += bs
    else:
        runs.append([phys * bs, bs])
for off, length in runs:
    print(off, length)
print('%d runs, %d bytes' % (len(runs), sum(r[1] for r in runs)), file=sys.stderr)
