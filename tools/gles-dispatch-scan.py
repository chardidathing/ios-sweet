#!/usr/bin/env python3
# after ios-sailfish by joranv1, ported to the xperia 1 ii (pdx203)
"""Which GLI dispatch entries does QuartzCore's GL renderer call?
Input: ipsw disassembly of QuartzCore (function-name lines + instruction lines)
and macOS gliDispatch.h. A register loaded from [x, #0x7f8] holds the
CGL-style {rctx, disp...} pointer; loads from it at #off (off >= 8) are
dispatch entries, index off/8 - 1."""
import re, sys
asm, hdr = sys.argv[1], sys.argv[2]
names = re.findall(r'\(\*(\w+)\)\s*\(', open(hdr).read())
used = {}
fn, disp = None, set()
ins = re.compile(r'^0x[0-9a-f]+:\s+(?:[0-9a-f]{2} ){4}\s*(\w+)\s+(.*)$')
for line in open(asm):
    line = line.rstrip('\n')
    if line and not line.startswith('0x') and not line.startswith(' ') and not line.startswith(';'):
        fn, disp = line.strip(), set()
        continue
    m = ins.match(line.replace('\t', ' '))
    if not m:
        continue
    op, args = m.group(1), m.group(2)
    a = [x.strip() for x in re.split(r',(?![^\[]*\])', args.split(';')[0])]
    if op == 'ldr' and len(a) == 2:
        mm = re.match(r'\[(\w+), #(0x[0-9a-f]+|\d+)\]', a[1])
        if mm:
            base, off = mm.group(1), int(mm.group(2), 0)
            if off == 0x7f8:
                disp.add(a[0]); continue
            if base in disp and off >= 8 and off % 8 == 0:
                i = off // 8 - 1
                nm = names[i] if i < len(names) else '?%d' % i
                used.setdefault(nm, set()).add(fn)
            disp.discard(a[0])
            continue
    if a and a[0] in disp and op not in ('str', 'stp', 'cmp', 'cbz', 'cbnz'):
        disp.discard(a[0])
print(len(names), 'entries in header;', len(used), 'used')
for nm in sorted(used, key=lambda n: names.index(n) if n in names else 9999):
    print('%4s %-40s %d' % (names.index(nm) if nm in names else '?', nm, len(used[nm])))
