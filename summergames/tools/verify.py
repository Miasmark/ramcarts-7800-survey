"""verify.py: compare code readings with memory dumps of the survey runs (live checks).
 1. the run-length streams against cart RAM (Summer swim picture, flags; Winter bobsled, biathlon)
 2. Summer diving's mirror table at $7800 (bit reversal)
 3. Winter bobsled tube frames (mask-per-cell) against $4824.. in a dump
Prints matching byte counts."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(PROJ, "tools"))
sys.path.insert(0, HERE)
import dis  # noqa: E402
import rle  # noqa: E402


def mem(game, run, frame):
    return open(os.path.join(PROJ, game, "runs", run, "mem_f%05d.bin" % frame), "rb").read()


def cmp_rle(game, bank, src, dst, run, frame, label):
    raw, nb = dis.load(game)
    out = rle.decode(raw, nb, bank, src)[0]
    m = mem(game, run, frame)
    n = min(len(out), 0x8000 - dst)
    same = sum(1 for i in range(n) if m[dst + i] == out[i])
    print("%-34s %s f%d: %d of %d bytes equal at $%04X" % (label, run, frame, same, n, dst))


def main():
    cmp_rle("summergames", 6, 0xA600, 0x6000, "e4", 684, "SG swim picture b6:$A600")
    cmp_rle("summergames", 6, 0xB190, 0x5800, "e4", 684, "SG swim font b6:$B190")
    cmp_rle("summergames", 6, 0x9FA5, 0x6FE0, "n1", 430, "SG flags block 6 b6:$9FA5")
    cmp_rle("summergames", 6, 0x830C, 0x4000, "n1", 430, "SG flags block 1 b6:$830C")
    cmp_rle("summergames", 6, 0x8000, 0x1800, "n1", 430, "SG font b6:$8000")
    cmp_rle("wintergames", 6, 0x9A69, 0x6000, "e3", 723, "WG bobsled picture b6:$9A69")
    cmp_rle("wintergames", 5, 0x8000, 0x6000, "e0", 660, "WG biathlon scene 1 b5:$8000")
    cmp_rle("wintergames", 5, 0x8F14, 0x6000, "e0", 660, "WG biathlon scene 2 b5:$8F14")
    cmp_rle("wintergames", 5, 0xA29C, 0x6000, "e0", 660, "WG biathlon scene 3 b5:$A29C")
    cmp_rle("wintergames", 0, 0xAD2D, 0x6000, "e0", 660, "WG biathlon range b0:$AD2D")
    cmp_rle("wintergames", 0, 0xAA49, 0x5800, "e0", 660, "WG biathlon b0:$AA49")
    cmp_rle("wintergames", 1, 0xA746, 0x6000, "e2", 702, "WG ski jump b1:$A746")
    cmp_rle("wintergames", 6, 0x8312, 0x6000, "e2", 702, "WG ski jump b6:$8312")
    m = mem("summergames", "e0", 380)
    rev = bytes(int("{:08b}".format(i)[::-1], 2) for i in range(256))
    print("SG diving mirror table $7800: %d of 256 bytes are the bit reversal" %
          sum(1 for i in range(256) if m[0x7800 + i] == rev[i]))
    # bobsled tube frames
    raw, nb = dis.load("wintergames")

    def pk(a):
        return dis.peek(raw, nb, 4, a)

    frames = {}
    for i in range(35):
        p = pk(0x8DD6 + 2 * i) | pk(0x8DD7 + 2 * i) << 8
        a = p
        img = {}
        ptr = 0x4824
        for col in range(19):
            for cell in range(5):
                top = ptr + 0x800
                mask = pk(a)
                a += 1
                for row in range(8):
                    top -= 0x100
                    v = 0xAA
                    if mask & (0x80 >> row):
                        v = pk(a)
                        a += 1
                    img[top] = v
                ptr += 0x13
            ptr -= 0x5E
        frames[i] = img
    for fr in (463, 723, 853, 1243):
        try:
            m = mem("wintergames", "e3", fr)
        except OSError:
            continue
        best = max(((sum(1 for k, v in img.items() if m[k] == v), i) for i, img in frames.items()))
        print("WG bobsled tube, dump f%d: best frame %d matches %d of 760 bytes" % (fr, best[1], best[0]))


if __name__ == "__main__":
    main()
