"""mapinfo.py DUMP [DUMP2]: facts about the level map in a survey memory dump (mem_fNNNNN.bin,
$0000-$7FFF). Prints where the brick characters ($2F-$36, $6C-$6D) are, where $FA and $FD and $C8
are used, zero-page play variables, and with a second dump the map cells that differ.
With --png OUT renders the whole 1024x168 map from the dump's own character set (4 greys)."""
import sys

args = [a for a in sys.argv[1:] if not a.startswith("--")]
d = open(args[0], "rb").read()
rows = [d[0x6000 + r * 256:0x6000 + (r + 1) * 256] for r in range(21)]


def cells(pred):
    return [(r, c) for r in range(21) for c in range(256) if pred(rows[r][c])]


br = cells(lambda v: 0x2F <= v <= 0x36 or 0x6C <= v <= 0x6D)
print("brick cells: %d; first few (row,col,char): %s" % (
    len(br), " ".join("%d,%d,%02X" % (r, c, rows[r][c]) for r, c in br[:8])))
for ch in (0xFA, 0xFD, 0xC8):
    cs = cells(lambda v, ch=ch: v == ch)
    print("char $%02X: %d cells; rows %s cols %s" % (
        ch, len(cs), sorted(set(r for r, c in cs))[:21], sorted(set(c for r, c in cs))[:12]))
print("zp: scroll $56/57=%02X%02X  ball x $CC/CD=%02X%02X y $CE=%02X  $50=%02X $51=%02X  $48=%02X $49=%02X" % (
    d[0x57], d[0x56], d[0xCD], d[0xCC], d[0xCE], d[0x50], d[0x51], d[0x48], d[0x49]))
if len(args) > 1:
    e = open(args[1], "rb").read()
    diff = [(a, d[a], e[a]) for a in range(0x6000, 0x7500) if d[a] != e[a]]
    print("map cells that differ: %d  %s" % (len(diff), " ".join("%04X:%02X>%02X" % x for x in diff[:16])))
    diff = [(a, d[a], e[a]) for a in range(0x7500, 0x7D00) if d[a] != e[a]]
    print("charset bytes that differ: %d  %s" % (len(diff), " ".join("%04X:%02X>%02X" % x for x in diff[:16])))
for a in sys.argv[1:]:
    if a.startswith("--png="):
        from PIL import Image
        img = Image.new("L", (1024, 168))
        px = img.load()
        for r in range(21):
            for c in range(256):
                ch = rows[r][c]
                for ln in range(8):
                    b = d[0x7500 + (7 - ln) * 256 + ch]
                    for p in range(4):
                        v = (b >> (6 - 2 * p)) & 3
                        px[c * 4 + p, r * 8 + ln] = (0, 110, 180, 255)[v]
        img = img.resize((2048, 336))
        img.save(a[6:])
        print("wrote", a[6:])
