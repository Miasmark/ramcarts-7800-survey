"""romstats.py: what Jinks keeps in each bank, and how well its level maps would pack.
Run with python -I. Prints a short report (also written to jinks/romstats.txt).
- per bank: pages that are blank (all $00 or all $FF) against used, as ranges
- per level map (21 rows x 256, row-major, a page a row): distinct characters, the last column
  with anything in it, and the size under four simple schemes: byte RLE, per-row RLE, 2x2 and
  4x4 metatile dictionaries (map of indices + dictionary), and zlib -9 as a yardstick
- the character sets: how many of the 256 cells are blank, how many differ between banks
"""
import os
import sys
import zlib

ROM = (os.environ.get("A7800_ROMS", "roms") + "/Jinks (NTSC) (Atari) (1989) (0818D8CD).a78")
HERE = os.path.dirname(os.path.abspath(__file__))
raw = open(ROM, "rb").read()[128:]
out = []


def P(s=""):
    out.append(s)


def bank(b):
    return raw[b * 0x4000:(b + 1) * 0x4000]


def rle(data):
    """(count, byte) pairs, count 1-255: the plainest scheme."""
    n, i = 0, 0
    while i < len(data):
        j = i
        while j < len(data) and data[j] == data[i] and j - i < 255:
            j += 1
        n += 2
        i = j
    return n


def rle_lit(data):
    """control byte: 0-127 = n+1 literals follow, 128-255 = repeat next byte n-126 times."""
    n, i = 0, 0
    lit = 0
    while i < len(data):
        j = i
        while j < len(data) and data[j] == data[i] and j - i < 129:
            j += 1
        if j - i >= 3:
            if lit:
                n += lit + (lit + 127) // 128
                lit = 0
            n += 2
        else:
            lit += j - i
        i = j
    if lit:
        n += lit + (lit + 127) // 128
    return n


def metatile(rows, w, h):
    """dictionary of w x h blocks: returns (blocks, index map bytes, dictionary bytes)."""
    seen = {}
    nrows = len(rows)
    ncols = len(rows[0])
    cells = 0
    for y in range(0, nrows, h):
        for x in range(0, ncols, w):
            key = tuple(tuple(rows[yy][x:x + w]) if yy < nrows else (0,) * w for yy in range(y, y + h))
            seen.setdefault(key, len(seen))
            cells += 1
    n = len(seen)
    idx = cells * (1 if n <= 256 else 2)
    return n, idx, n * w * h


P("== banks: used pages (a page is blank when all $00 or all $FF)")
for b in range(8):
    d = bank(b)
    runs, start = [], None
    for p in range(64):
        pg = d[p * 256:(p + 1) * 256]
        blank = pg == bytes(256) or pg == b"\xff" * 256
        if not blank and start is None:
            start = p
        if blank and start is not None:
            runs.append((start, p - 1))
            start = None
    if start is not None:
        runs.append((start, 63))
    base = 0xC0 if b == 7 else 0x80
    used = sum(e - s + 1 for s, e in runs)
    P("bank %d: %2d of 64 pages used: %s" % (b, used, " ".join(
        "$%02X-$%02X" % (base + s, base + e) for s, e in runs)))

P()
P("== level maps: 21 rows x 256 = 5,376 bytes each, stored as they are drawn")
for name, b, off in (("level 1 (b6 $8000)", 6, 0x0000), ("level 2 (b6 $A000)", 6, 0x2000),
                     ("level 3 (b5 $8000)", 5, 0x0000), ("level 4 (b5 $A000)", 5, 0x2000)):
    m = bank(b)[off:off + 21 * 256]
    rows = [m[r * 256:(r + 1) * 256] for r in range(21)]
    distinct = len(set(m))
    last = max(x for x in range(256) if any(rows[r][x] != rows[r][255] for r in range(21)))
    r1 = rle(m)
    r2 = rle_lit(m)
    rr = sum(rle_lit(r) for r in rows)
    cols = bytes(rows[r][x] for x in range(256) for r in range(21))
    rc = rle_lit(cols)
    n2, i2, d2 = metatile(rows, 2, 2)
    n4, i4, d4 = metatile(rows, 4, 4)
    n42, i42, d42 = metatile(rows, 4, 2)
    z = len(zlib.compress(m, 9))
    P("%s: %3d distinct chars, last changing column %d" % (name, distinct, last))
    P("   pair RLE %5d | literal/run RLE %5d (by rows %5d, by columns %5d) | zlib %5d" % (r1, r2, rr, rc, z))
    P("   2x2 blocks: %4d distinct, map %5d + dict %5d = %5d" % (n2, i2, d2, i2 + d2))
    P("   4x2 blocks: %4d distinct, map %5d + dict %5d = %5d" % (n42, i42, d42, i42 + d42))
    P("   4x4 blocks: %4d distinct, map %5d + dict %5d = %5d" % (n4, i4, d4, i4 + d4))

P()
P("== character sets: 8 line pages at $9500-$9CFF of banks 5 and 6 (page $95 = the bottom line)")
cs = {}
for b in (5, 6):
    c = bank(b)[0x1500:0x1D00]
    chars = [bytes(c[p * 256 + i] for p in range(8)) for i in range(256)]
    cs[b] = chars
    blank = sum(1 for ch in chars if ch == bytes(8))
    P("bank %d: %d of 256 characters blank, %d distinct shapes, zlib %d of 2048" % (
        b, blank, len(set(chars)), len(zlib.compress(c, 9))))
P("characters that differ between the two sets: %d" % sum(1 for i in range(256) if cs[5][i] != cs[6][i]))
for b in (5, 6):
    used = set()
    for off in (0, 0x2000):
        used |= set(bank(b)[off:off + 21 * 256])
    P("bank %d: its two maps use %d characters between them; $FA is %s" % (
        b, len(used), " ".join("%02X" % x for x in cs[b][0xFA])))

P()
P("== the two sample images in bank 0 (4-bit pairs, big-endian length word first)")
d = bank(0)
for name, off in (("image 2, $8000 (menu)", 0x0000), ("image 1, $9900 (title)", 0x1900)):
    p = off
    blocks = []
    end = 0x1900 if off == 0 else 0x3800
    while p < end - 2:
        ln = d[p] * 256 + d[p + 1]
        if ln == 0 or p + ln > end + 2:
            break
        blocks.append((p, ln))
        p += ln + 2
    P("%s: %s" % (name, ", ".join("$%04X len %d (%.2f s at 5,245 Hz)" % (0x8000 + s, ln, ln * 2 / 5245.0)
                                  for s, ln in blocks)))
for b in (2,):
    d = bank(b)
    ln = d[0x1000] * 256 + d[0x1001]
    P("bank %d $9000: length word %d (%.2f s)" % (b, ln, ln * 2 / 5245.0))

txt = "\n".join(out)
print(txt)
open(os.path.join(HERE, "..", "romstats.txt"), "w").write(txt + "\n")
