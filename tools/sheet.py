"""sheet.py RUNDIR [cols]: a contact sheet of a run's snapshots (snap/a7800/*.png), labelled
with the SNAPS frame numbers taken from the mem_fNNNNN.bin files. Writes RUNDIR/sheet.png."""
import glob
import os
import sys
from PIL import Image, ImageDraw

rd = sys.argv[1]
cols = int(sys.argv[2]) if len(sys.argv) > 2 else 4
pngs = sorted(glob.glob(os.path.join(rd, "snap", "a7800", "*.png")))
frames = sorted(int(os.path.basename(p)[5:10]) for p in glob.glob(os.path.join(rd, "mem_f*.bin")))
ims = [Image.open(p).convert("RGB") for p in pngs]
if not ims:
    sys.exit("no snapshots")
w, h = ims[0].size
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * (h + 12)), (40, 40, 40))
d = ImageDraw.Draw(sheet)
for i, im in enumerate(ims):
    x, y = (i % cols) * w, (i // cols) * (h + 12)
    sheet.paste(im, (x, y + 12))
    d.text((x + 2, y), "f%d" % (frames[i] if i < len(frames) else -1), fill=(255, 255, 0))
sheet.save(os.path.join(rd, "sheet.png"))
print(os.path.join(rd, "sheet.png"), sheet.size, len(ims))
