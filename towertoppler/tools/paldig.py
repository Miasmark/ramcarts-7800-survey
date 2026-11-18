"""paldig.py RUNDIR: digest of pal.txt (tt.lua): the distinct per-frame sequences of MARIA register
writes with the line numbers dropped, each with the first frame it was seen and how many frames.
Lines: also prints the min-max raster line each PC wrote on."""
import re
import sys
from collections import OrderedDict

REG = {0x20: "BG", 0x22: "P0C2", 0x26: "P1C2", 0x2A: "P2C2", 0x2E: "P3C2", 0x32: "P4C2", 0x36: "P5C2",
       0x3A: "P6C2", 0x3E: "P7C2", 0x2C: "DPPH", 0x30: "DPPL", 0x34: "CHARBASE", 0x3C: "CTRL", 0x38: "OFFSET"}
seqs = OrderedDict()
lines = {}
for ln in open(sys.argv[1] + "/pal.txt"):
    p = ln.split()
    if len(p) < 2:
        continue
    f = int(p[0])
    key = []
    for w in p[1:]:
        m = re.match(r"(..)=(..)@(\d+)\((....)\)", w)
        r, v, l, pc = int(m.group(1), 16), m.group(2), int(m.group(3)), m.group(4)
        key.append("%s=%s" % (REG.get(r, "%02X" % r), v))
        lo, hi = lines.get(pc, (999, -1))
        lines[pc] = (min(lo, l), max(hi, l))
    key = " ".join(key)
    if key not in seqs:
        seqs[key] = [f, 0]
    seqs[key][1] += 1
for k, (f, n) in seqs.items():
    print("first f%d, %d changes: %s" % (f, n, k))
print("raster lines by PC:", " ".join("%s:%d-%d" % (pc, a, b) for pc, (a, b) in sorted(lines.items())))
