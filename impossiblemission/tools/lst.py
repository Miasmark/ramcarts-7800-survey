"""lst.py SPACE START END: a compact view of disasm/<SPACE>.asm between two addresses (hex).
One output line per run of straight-line code; a new line starts at every label, and after
RTS/JMP/RTI. Each line begins with its address."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    sp, a0, a1 = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16)
    path = os.path.join(os.path.dirname(HERE), "disasm", sp + ".asm")
    cur = []
    newline = True
    out = []
    pend_label = False
    xr = False
    for ln in open(path):
        s = ln.rstrip("\n")
        m = re.match(r"^\s+(\S.*?)\s*; ([0-9A-F]{4}): ([0-9A-F ]+?)\s*$", s)
        if not m:
            if s.startswith("; xrefs:"):
                xr = True
            elif re.match(r"^[A-Za-z_]\w*:", s):
                pend_label = xr
                xr = False
            continue
        ins, addr, raw = m.group(1), int(m.group(2), 16), m.group(3)
        if addr < a0 or addr > a1:
            pend_label = False
            continue
        ins = re.sub(r"\s+", " ", ins)
        ins = re.sub(r"\b(?:sub|dat|L|ram)\d?_([0-9A-F]{4})\b", r"$\1", ins)
        lab = pend_label
        pend_label = False
        if lab or newline:
            if cur:
                out.append(" ; ".join(cur))
            cur = ["%04X: %s" % (addr, ins)]
        else:
            cur.append(ins)
        newline = ins.split()[0] in ("RTS", "JMP", "RTI", "BRK")
        if newline:
            out.append(" ; ".join(cur))
            cur = []
    if cur:
        out.append(" ; ".join(cur))
    for o in out:
        print(o)


if __name__ == "__main__":
    main()
