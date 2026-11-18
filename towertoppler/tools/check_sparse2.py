"""check_sparse2.py DUMP: coordinator's check of the tower packing. Table at b0:$AD00: bitmap
pointers lo/hi at +0/+8, cell-data pointers lo/hi at +$10/+$18, row counts at +$20. Decodes all
eight towers, totals the packed size, and compares tower 1 with the map at $6A00 in a dump."""
import os
import sys
ROM = os.environ.get("A7800_ROMS", "roms") + "/Tower Toppler.a78"
b0 = open(ROM, "rb").read()[128:128 + 0x4000]
T = 0x2D00
tot_rows = tot_bm = tot_cells = 0
for t in range(8):
    bm = (b0[T + t] | b0[T + 8 + t] << 8) - 0x8000
    dp = (b0[T + 16 + t] | b0[T + 24 + t] << 8) - 0x8000
    rows = b0[T + 32 + t]
    out = bytearray()
    d0 = dp
    for r in range(rows):
        bits = b0[bm + 2 * r] | b0[bm + 2 * r + 1] << 8
        for i in range(16):
            if bits >> i & 1:
                out.append(b0[dp]); dp += 1
            else:
                out.append(0)
    tot_rows += rows; tot_bm += 2 * rows; tot_cells += dp - d0
    if t == 0:
        live = open(sys.argv[1], "rb").read()[0x6A00:0x6A00 + len(out)]
        same = sum(1 for a, b in zip(out, live) if a == b)
        print("tower 1: %d rows, %d cells, %d equal the dump, %d non-zero in the decode, %d in the dump"
              % (rows, len(out), same, sum(1 for x in out if x), sum(1 for x in live if x)))
print("8 towers: %d rows = %d cells; packed %d bitmap + %d cell bytes = %d (%.0f%%)"
      % (tot_rows, tot_rows * 16, tot_bm, tot_cells, tot_bm + tot_cells, 100.0 * (tot_bm + tot_cells) / (tot_rows * 16)))
