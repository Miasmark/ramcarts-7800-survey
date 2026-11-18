"""tube.py: measure Winter Games' bobsled tube frames (b4:$885D, pointer table b4:$8DD6, 35 entries).
Each frame is 19 columns x 5 cells; a cell is a mask byte, then one literal byte per set bit
(MSB = top row); a clear bit draws $AA.  Prints packed and unpacked sizes."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import dis  # noqa: E402

raw, nb = dis.load("wintergames")


def pk(a):
    return dis.peek(raw, nb, 4, a)


tot_p = tot_u = 0
sizes = []
ptrs = []
for i in range(35):
    p = pk(0x8DD6 + 2 * i) | pk(0x8DD7 + 2 * i) << 8
    ptrs.append(p)
    a = p
    for cell in range(19 * 5):
        m = pk(a)
        a += 1 + bin(m).count("1")
    sizes.append(a - p)
    tot_p += a - p
    tot_u += 19 * 5 * 8
print("frames 35, pointers $%04X..$%04X, distinct %d" % (min(ptrs), max(ptrs), len(set(ptrs))))
print("packed sizes", sizes)
dist = {}
for p, s in zip(ptrs, sizes):
    dist[p] = s
print("distinct frames %d: packed %d bytes for %d unpacked (ratio %.2f)"
      % (len(dist), sum(dist.values()), len(dist) * 760, sum(dist.values()) / (len(dist) * 760.0)))
