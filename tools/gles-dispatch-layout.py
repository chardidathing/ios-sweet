#!/usr/bin/env python3
# after ios-sailfish by joranv1, ported to the xperia 1 ii (pdx203)
"""iOS GLI dispatch layout from GLEngine's gliInitDispatchTable (ipsw
disassembly): every entry is stored as `add xR, xR, #lo ; _glName_Suffix`
then `str xR, [xB, #off]`. Prints "index name" (index = off / 8 into the
dispatch table, which CA reaches at {rctx, disp...} + 8 + 8*index)."""
import re, sys
lines = open(sys.argv[1]).read().split('\n')
start = lines.index('_gliInitDispatchTable:')
regname, table = {}, {}
for l in lines[start + 1:]:
    if l and not l.startswith(('0x', ' ', ';')):
        break
    l = l.replace('\t', ' ')
    m = re.search(r'add (x\d+), x\d+, #0x[0-9a-f]+ ; _(gl\w+)', l)
    if m:
        regname[m.group(1)] = m.group(2)
        continue
    m = re.search(r'str (x\d+), \[x\d+, #(0x[0-9a-f]+)\]', l)
    if m and m.group(1) in regname:
        off = int(m.group(2), 16)
        name = re.sub(r'_(Comp|Exec|Imm|Disp|Err|Mixed|NoOp|Invalid|PackThread)\w*$', '', regname[m.group(1)])
        table.setdefault(off // 8, name)
for i in sorted(table):
    print(i, table[i])
