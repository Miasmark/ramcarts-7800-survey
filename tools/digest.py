"""digest.py RUNDIR [--top N] [--segs N]: a short digest of a survey.lua run.
Segments the per-frame logs (cpuw/cpur/mariar) into runs of frames with the same set of PCs
(or pages), so a load burst stands out from the steady state."""
import os
import re
import sys


def ranges(vals):
    vals = sorted(vals)
    out, i = [], 0
    while i < len(vals):
        j = i
        while j + 1 < len(vals) and vals[j + 1] == vals[j] + 1:
            j += 1
        out.append((vals[i], vals[j]))
        i = j + 1
    return out


def load(path):
    rows = []
    if not os.path.exists(path):
        return rows
    for ln in open(path):
        head, _, tail = ln.partition("|")
        f, n = head.split()
        items = []
        for it in tail.split():
            p = it.split(":")
            items.append(p)
        rows.append((int(f), int(n), items))
    return rows


def segments(rows, key, maxseg, label):
    segs = []
    for f, n, items in rows:
        k = key(items)
        if segs and segs[-1][0] == k and f - segs[-1][2] <= 2:
            segs[-1][2] = f
            segs[-1][3] += n
            segs[-1][4] += 1
        else:
            segs.append([k, f, f, n, 1])
    print("%s: %d frames with activity, %d segments" % (label, len(rows), len(segs)))
    # merge display: show biggest by total, in frame order
    big = sorted(segs, key=lambda s: -s[3])[:maxseg]
    for s in sorted(big, key=lambda s: s[1]):
        print("  f%5d-%5d (%4d fr) total %8d avg %7.0f  %s" % (s[1], s[2], s[4], s[3], s[3] / s[4], s[0]))


def main():
    rd = sys.argv[1]
    top = 14
    maxseg = 14
    if "--top" in sys.argv:
        top = int(sys.argv[sys.argv.index("--top") + 1])
    if "--segs" in sys.argv:
        maxseg = int(sys.argv[sys.argv.index("--segs") + 1])
    sm = open(os.path.join(rd, "summary.txt")).read().split("\n")
    sect = None
    count = 0
    pages = {}
    for ln in sm:
        if not ln.startswith("  "):
            sect = ln
            count = 0
            if ln.startswith("CPU") or ln.startswith("PCs") or ln.startswith("frames"):
                n = sum(1 for x in sm[sm.index(ln) + 1:] if x.startswith("  ")) if False else 0
                print(ln)
            continue
        if sect.startswith("MARIA"):
            a, n = ln.split()
            pages[int(a, 16) >> 8] = int(n)
            continue
        count += 1
        if count <= top:
            print(ln)
        elif count == top + 1:
            rest = 0
            i = sm.index(ln)
            while i < len(sm) and sm[i].startswith("  "):
                rest += 1
                i += 1
            print("  ... %d more PCs" % rest)
    print("MARIA reads of cart RAM by page range (total reads):")
    for a, b in ranges(pages):
        print("  %02X00-%02XFF  %d" % (a, b, sum(pages[p] for p in range(a, b + 1))))

    def pcs_key(items):
        ks = sorted(items, key=lambda p: -int(p[1]))[:6]
        return " ".join("%s[%s]" % (p[0], p[2]) for p in sorted(ks))

    def page_key(items):
        pg = [int(p[0], 16) for p in items]
        return " ".join("%02X-%02X" % r if r[0] != r[1] else "%02X" % r[0] for r in ranges(pg))

    segments(load(os.path.join(rd, "cpuw.txt")), pcs_key, maxseg, "CPU writes")
    segments(load(os.path.join(rd, "cpur.txt")), pcs_key, maxseg, "CPU reads")
    segments(load(os.path.join(rd, "mariar.txt")), page_key, maxseg, "MARIA reads")
    for name in ("regs.txt", "bank.txt"):
        lines = open(os.path.join(rd, name)).read().split("\n")
        seen = {}
        for ln in lines:
            if not ln.strip():
                continue
            f, _, rest = ln.partition(" ")
            k = re.sub(r"@\d+", "", rest)
            seen.setdefault(k, []).append(int(f))
        print("%s: %d change lines, %d distinct sequences (ignoring lines)" % (name, len(lines) - 1, len(seen)))
        for k, fs in sorted(seen.items(), key=lambda kv: kv[1][0])[:maxseg]:
            ex = [ln for ln in lines if ln.startswith("%d " % fs[0])][0]
            print("  first f%d (x%d): %s" % (fs[0], len(fs), ex.partition(" ")[2][:300]))


if __name__ == "__main__":
    main()
