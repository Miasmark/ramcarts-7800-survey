"""rooms.py [-v]: decode the 32 room records (bank 5, pointer table $A18F) as the builder at
5:$99CF-$9E75 reads them, and print each room's size in ROM. Format (code, 5:$9A5F on):
  4 bytes   colours: -> $2000 (BACKGRND shadow), $2011-$2013 (palette 4 shadow)
  floors    [x? , y?, len-1] ... $FF      (JSR $FC31 with Y=byte0, X=byte1; stores char $80 len times)
  lifts     [a, b] ... $FF                (5 cells cleared to 0 down a column)
  entry     6 bytes (player start for each side) ; +6 skipped
  robots    [type, x, y] ... $FF          (up to 4)
  one more  [kind, x, y] or $FF           (the ball / special), then
  liftdef   [a, b, c, d, stops... $FF] ... $FF
  furniture [x, y, type, slot] ... $FF    (slot = index into the $6000 search table)
"""
import os
import sys

ROM = (os.environ.get("A7800_ROMS", "roms") + "/Impossible Mission (NTSC) (Atari) (1987) (3B1F2F47).a78")
raw = open(ROM, "rb").read()[128:]
B5 = raw[5 * 0x4000:6 * 0x4000]


def pk(a):
    return B5[a - 0x8000]


def main():
    v = "-v" in sys.argv
    ptrs = [pk(0xA18F + 2 * i) | pk(0xA190 + 2 * i) << 8 for i in range(32)]
    tot = 0
    slots = set()
    for r, p in enumerate(ptrs):
        a = p + 4
        floors = []
        while pk(a) != 0xFF:
            floors.append((pk(a), pk(a + 1), pk(a + 2)))
            a += 3
        a += 1
        lifts = []
        while pk(a) != 0xFF:
            lifts.append((pk(a), pk(a + 1)))
            a += 2
        a += 1
        entry = [pk(a + i) for i in range(6)]
        a += 6
        robots = []
        while pk(a) != 0xFF:
            robots.append((pk(a), pk(a + 1), pk(a + 2)))
            a += 3
        a += 1
        special = None
        if pk(a) != 0xFF:
            special = (pk(a), pk(a + 1), pk(a + 2))
            a += 3
        else:
            a += 1
        ld = []
        while pk(a) != 0xFF:
            rec = [pk(a + i) for i in range(4)]
            a += 4
            stops = []
            while pk(a) != 0xFF:
                stops.append(pk(a))
                a += 1
            a += 1
            ld.append((rec, stops))
        a += 1
        furn = []
        while pk(a) != 0xFF:
            furn.append((pk(a), pk(a + 1), pk(a + 2), pk(a + 3)))
            slots.add(pk(a + 3))
            a += 4
        a += 1
        size = a - p
        tot += size
        cells = sum(f[2] + 1 for f in floors)
        print("room %2d @%04X %3d bytes: colours %s, %2d floor runs (%3d cells), %d lift shafts, %d robots, special %s, %d lifts, %2d furniture"
              % (r, p, size, " ".join("%02X" % pk(p + i) for i in range(4)), len(floors), cells, len(lifts),
                 len(robots), "yes" if special else "no ", len(ld), len(furn)))
        if v:
            print("   floors", floors)
            print("   lifts", lifts, "entry", entry)
            print("   robots", robots, "special", special)
            print("   liftdefs", ld)
            print("   furniture", furn)
    print("total %d bytes for 32 rooms (avg %.1f); %d distinct search slots (max %d)"
          % (tot, tot / 32.0, len(slots), max(slots) if slots else -1))


if __name__ == "__main__":
    main()
