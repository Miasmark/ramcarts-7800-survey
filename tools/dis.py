"""dis.py GAME BANK ADDR [COUNT] [--bytes]: a plain linear disassembly from one address.
  GAME  towertoppler | jinks | impossiblemission | summergames | wintergames
  BANK  the 16K bank number in the file (0-7; Tower Toppler 0-3). For $C000-$FFFF give the
        last bank (or any: the last is used). A bank-register value v selects v % nbanks.
  ADDR  hex CPU address ($8000-$FFFF); COUNT instructions (default 40)
Not a tracer: it decodes straight on, so start at a known instruction. Uses the toolkit's
opcode table read-only. Also: dis.py GAME BANK ADDR N --hex  dumps N bytes."""
import os
import sys

sys.path.insert(0, os.environ.get("A7800_TOOLKIT", "a7800-toolkit/tools"))
import m6502  # noqa: E402

ROMDIR = os.environ.get("A7800_ROMS", "roms") + "/"
ROMS = {
    "towertoppler": "Tower Toppler.a78",
    "jinks": "Jinks (NTSC) (Atari) (1989) (0818D8CD).a78",
    "impossiblemission": "Impossible Mission (NTSC) (Atari) (1987) (3B1F2F47).a78",
    "summergames": "Summer Games (NTSC) (Atari) (1987) (65C6DF3F).a78",
    "wintergames": "Winter Games (NTSC) (Atari) (1987) (8981B531).a78",
}
REGS = {0x20: "BACKGRND", 0x28: "WSYNC", 0x2C: "DPPH", 0x30: "DPPL", 0x34: "CHARBASE", 0x3C: "CTRL",
        0x28 + 0: "WSYNC", 0x08: "INPT0", 0x01: "INPTCTRL", 0x280: "SWCHA", 0x282: "SWCHB",
        0x15: "AUDC0", 0x16: "AUDC1", 0x17: "AUDF0", 0x18: "AUDF1", 0x19: "AUDV0", 0x1A: "AUDV1"}


def load(game):
    raw = open(ROMDIR + "/" + ROMS[game], "rb").read()[128:]
    return raw, len(raw) // 0x4000


def peek(raw, nb, bank, addr):
    if addr >= 0xC000:
        return raw[(nb - 1) * 0x4000 + addr - 0xC000]
    return raw[(bank % nb) * 0x4000 + addr - 0x8000]


def main():
    game, bank, addr = sys.argv[1], int(sys.argv[2]), int(sys.argv[3].lstrip("$"), 16)
    n = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else 40
    raw, nb = load(game)
    if "--hex" in sys.argv:
        for o in range(0, n, 16):
            print("%04X: %s" % (addr + o, " ".join("%02X" % peek(raw, nb, bank, addr + o + i)
                                                    for i in range(min(16, n - o)))))
        return
    for _ in range(n):
        if addr > 0xFFFF:
            break
        op = peek(raw, nb, bank, addr)
        mn, md, il = m6502.OPCODES[op]
        ln = m6502.LENGTH[op]
        b = [peek(raw, nb, bank, addr + i) for i in range(ln) if addr + i <= 0xFFFF]
        if md == "rel":
            v = "$%04X" % ((addr + 2 + (b[1] - 256 if b[1] > 127 else b[1])) & 0xFFFF)
        elif ln == 2:
            v = "$%02X" % b[1]
        elif ln == 3:
            v = "$%04X" % (b[1] | b[2] << 8)
        else:
            v = ""
        txt = (mn + " " + m6502.FMT[md].format(v=v)).strip()
        val = (b[1] | b[2] << 8) if ln == 3 else (b[1] if ln == 2 and md != "imm" and md != "rel" else None)
        note = ""
        if val in REGS and md != "imm":
            note = "  ; " + REGS[val]
        print("%04X: %-9s %s%s%s" % (addr, " ".join("%02X" % x for x in b), txt, " *" if il == "*" else "", note))
        addr += ln


if __name__ == "__main__":
    main()
