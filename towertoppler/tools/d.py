"""d.py BANK START END [cols]: compact linear disassembly of Tower Toppler, several instructions a line.
BANK is the file bank (0-3) for $8000-$BFFF; $C000-$FFFF is always bank 3.
Flow breaks (RTS, RTI, JMP, BRK) end a printed line, so routines read as paragraphs.
d.py BANK START N --hex dumps N bytes."""
import os
import sys

sys.path.insert(0, os.environ.get("A7800_TOOLKIT", "a7800-toolkit/tools"))
import m6502  # noqa: E402

ROM = (os.environ.get("A7800_ROMS", "roms") + "/Tower Toppler.a78")
RAW = open(ROM, "rb").read()[128:]


def peek(bank, a):
    if a >= 0xC000:
        return RAW[3 * 0x4000 + a - 0xC000]
    return RAW[bank * 0x4000 + a - 0x8000]


def main():
    bank, a = int(sys.argv[1]), int(sys.argv[2], 16)
    if "--hex" in sys.argv:
        n = int(sys.argv[3])
        for o in range(0, n, 32):
            print("%04X: %s" % (a + o, " ".join("%02X" % peek(bank, a + o + i) for i in range(min(32, n - o)))))
        return
    end = int(sys.argv[3], 16)
    cols = int(sys.argv[4]) if len(sys.argv) > 4 else 5
    line = []
    while a <= end:
        op = peek(bank, a)
        mn, md, il = m6502.OPCODES[op]
        ln = m6502.LENGTH[op]
        b = [peek(bank, a + i) for i in range(ln)]
        if md == "rel":
            v = "%04X" % ((a + 2 + (b[1] - 256 if b[1] > 127 else b[1])) & 0xFFFF)
        elif ln == 2:
            v = "%02X" % b[1]
        elif ln == 3:
            v = "%04X" % (b[1] | b[2] << 8)
        else:
            v = ""
        txt = (mn + " " + m6502.FMT[md].format(v=v).replace("$", "")).strip()
        if il == "*":
            txt = "?" + txt
        line.append("%04X %s" % (a, txt))
        a += ln
        if mn in ("RTS", "RTI", "JMP", "BRK") or len(line) >= cols:
            print(" | ".join(line))
            line = []
            if mn in ("RTS", "RTI", "JMP"):
                print()
    if line:
        print(" | ".join(line))


if __name__ == "__main__":
    main()
