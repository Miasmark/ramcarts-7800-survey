"""rle.py GAME BANK SRC [DST] [--out FILE]: decode the shell's run-length stream (f7:$FE63 in Summer
Games): a non-zero byte is a literal; 00 v n is n copies of v; 00 v 00 ends.  Prints packed and
unpacked sizes and the share of runs.  --out writes the unpacked bytes."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import dis  # noqa: E402


def decode(raw, nb, bank, src):
    out = bytearray()
    a = src
    lit = runs = runbytes = 0
    while True:
        b = dis.peek(raw, nb, bank, a)
        a += 1
        if b:
            out.append(b)
            lit += 1
            continue
        v = dis.peek(raw, nb, bank, a)
        n = dis.peek(raw, nb, bank, a + 1)
        a += 2
        if n == 0:
            break
        out += bytes([v]) * n
        runs += 1
        runbytes += n
        if a > 0xC000 and bank != nb - 1:
            print("ran off the bank")
            break
    return out, a - src, lit, runs, runbytes


def main():
    game, bank, src = sys.argv[1], int(sys.argv[2]), int(sys.argv[3], 16)
    dst = int(sys.argv[4], 16) if len(sys.argv) > 4 and not sys.argv[4].startswith("--") else 0
    raw, nb = dis.load(game)
    out, packed, lit, runs, runbytes = decode(raw, nb, bank, src)
    print("bank %d $%04X-$%04X packed %d -> %d bytes (dst $%04X-$%04X)  ratio %.2f  literals %d, runs %d (%d bytes, %d single)"
          % (bank, src, src + packed - 1, packed, len(out), dst, dst + len(out) - 1,
             packed / max(1, len(out)), lit, runs, runbytes, 0))
    if "--out" in sys.argv:
        open(sys.argv[sys.argv.index("--out") + 1], "wb").write(out)


if __name__ == "__main__":
    main()
