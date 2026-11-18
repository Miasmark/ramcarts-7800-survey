"""ramuse.py RUNDIR [F0 F1] [--lo ADDR --hi ADDR]: cart RAM use by writer/reader PC, sorted by address.
Reads cpuw.txt and cpur.txt (survey.lua) and prints, per PC, the union address range,
the count, the frames it was seen in (first-last, how many). Limit to frames F0..F1.
Also: ramuse.py RUNDIR --diff FA FB   pages of $4000-$7FFF that differ between two dumps,
      ramuse.py RUNDIR --nz F         runs of non-zero bytes in $4000-$7FFF and $1800-$27FF of a dump
"""
import os
import sys


def parse(path, f0, f1, lo, hi):
    tot = {}
    for ln in open(path):
        head, _, rest = ln.partition("|")
        f = int(head.split()[0])
        if f < f0 or f > f1:
            continue
        for part in rest.split():
            pc, n, rng = part.split(":")
            a, b = rng.split("-")
            a, b = int(a, 16), int(b, 16)
            if b < lo or a > hi:
                continue
            pc = int(pc, 16)
            t = tot.setdefault(pc, [0, a, b, f, f, 0])
            t[0] += int(n)
            t[1] = min(t[1], a)
            t[2] = max(t[2], b)
            t[4] = f
            t[5] += 1
    return tot


def runs(buf, base, lo, hi, gap=8):
    out = []
    start = None
    last = None
    for a in range(lo, hi + 1):
        if buf[a]:
            if start is None:
                start = a
            last = a
        elif start is not None and a - last > gap:
            out.append((start, last))
            start = None
    if start is not None:
        out.append((start, last))
    return out


def main():
    rd = sys.argv[1]
    args = sys.argv[2:]
    if "--diff" in args:
        i = args.index("--diff")
        a = open(os.path.join(rd, "mem_f%05d.bin" % int(args[i + 1])), "rb").read()
        b = open(os.path.join(rd, "mem_f%05d.bin" % int(args[i + 2])), "rb").read()
        d = bytearray(len(a))
        for k in range(len(a)):
            d[k] = 1 if a[k] != b[k] else 0
        for lo, hi in ((0x40, 0xFF), (0x140, 0x1FF), (0x1800, 0x27FF), (0x4000, 0x7FFF)):
            for s, e in runs(d, 0, lo, hi, 16):
                print("  %04X-%04X  %5d bytes span, %d differ" % (s, e, e - s + 1, sum(d[s:e + 1])))
        return
    if "--nz" in args:
        i = args.index("--nz")
        a = open(os.path.join(rd, "mem_f%05d.bin" % int(args[i + 1])), "rb").read()
        for lo, hi in ((0x1800, 0x27FF), (0x4000, 0x7FFF)):
            for s, e in runs(a, 0, lo, hi, 32):
                print("  %04X-%04X  %5d bytes span, %d non-zero" % (s, e, e - s + 1, sum(1 for x in a[s:e + 1] if x)))
        return
    lo, hi = 0x1800, 0x7FFF
    if "--lo" in args:
        lo = int(args[args.index("--lo") + 1], 16)
    if "--hi" in args:
        hi = int(args[args.index("--hi") + 1], 16)
    skip = set()
    for opt in ("--lo", "--hi"):
        if opt in args:
            skip.add(args.index(opt) + 1)
    nums = [int(x) for k, x in enumerate(args) if x.isdigit() and k not in skip]
    f0, f1 = (nums + [0, 10 ** 9])[:2] if len(nums) >= 2 else (0, 10 ** 9)
    for name in [n for n in ("cpuw.txt", "cpur.txt", "conw.txt") if os.path.exists(os.path.join(rd, n))]:
        tot = parse(os.path.join(rd, name), f0, f1, lo, hi)
        print(name, "frames", f0, f1)
        for pc in sorted(tot, key=lambda p: (tot[p][1], tot[p][2], p)):
            t = tot[pc]
            print("  %04X-%04X  pc %05X  n %7d  f %d-%d (%d)" % (t[1], t[2], pc, t[0], t[3], t[4], t[5]))


if __name__ == "__main__":
    main()
