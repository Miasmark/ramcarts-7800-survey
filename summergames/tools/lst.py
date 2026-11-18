"""lst.py GAME SPACE ADDR [N] [COLS]: compact view of the traced listing <GAME>/disasm/<SPACE>.asm
from the first line at or after ADDR (hex), N instruction/data lines (default 60), COLS per row (3).
Labels are shown inline as 'name:'."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))


def main():
    game, space, addr = sys.argv[1], sys.argv[2], int(sys.argv[3], 16)
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 60
    cols = int(sys.argv[5]) if len(sys.argv) > 5 else 3
    path = os.path.join(PROJ, game, "disasm", space + ".asm")
    out, pend, started = [], "", False
    rx = re.compile(r"^\s+(.*?)\s*;\s*([0-9A-F]{4}):\s*(.*)$")
    for ln in open(path, encoding="utf-8", errors="replace"):
        ln = ln.rstrip("\n")
        m = rx.match(ln)
        if m:
            a = int(m.group(2), 16)
            if not started and a >= addr:
                started = True
            if started:
                ins = re.sub(r"\s+", " ", m.group(1))
                out.append("%s%04X %s" % (pend, a, ins))
                pend = ""
                if len(out) >= n:
                    break
        elif started and ln and not ln.startswith(";") and ln.rstrip().endswith(":"):
            pend = "[" + ln.strip() + "] "
        elif started and ln.startswith("; ") and len(ln) > 4 and "----" not in ln and "====" not in ln:
            pass
    for i in range(0, len(out), cols):
        print(" | ".join(x.ljust(36) for x in out[i:i + cols]))


if __name__ == "__main__":
    main()
