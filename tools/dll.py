"""dll.py RUNDIR [FRAME ...] [-v]: decode the DLL and display lists from survey.lua's memory dumps.
Writes RUNDIR/dll_fNNNNN.txt (every zone and header) and prints a summary per frame:
where the DLL and the lists live, how many zones, and where the graphics / character maps
MARIA is pointed at live (console RAM, cart RAM $4000-$7FFF, ROM)."""
import glob
import os
import sys


def region(a):
    if 0x4000 <= a < 0x8000:
        return "CARTRAM"
    if a >= 0x8000:
        return "ROM"
    if 0x1800 <= a < 0x2800 or a < 0x200:
        return "conRAM"
    return "other"


def spans(addrs):
    """pages touched -> compact ranges"""
    pg = sorted(set(a >> 8 for a in addrs))
    out, i = [], 0
    while i < len(pg):
        j = i
        while j + 1 < len(pg) and pg[j + 1] == pg[j] + 1:
            j += 1
        out.append("%02X-%02X" % (pg[i], pg[j]) if j > i else "%02X" % pg[i])
        i = j + 1
    return " ".join(out)


def decode(mem, dll, maxlines=243):
    zones = []
    line = 0
    a = dll
    while line < maxlines and len(zones) < 120:
        b0, hi, lo = mem[a], mem[a + 1], mem[a + 2]
        h = (b0 & 15) + 1
        dl = hi << 8 | lo
        ents = []
        p = dl
        n = 0
        while n < 40 and p + 4 < len(mem):
            b1 = mem[p + 1]
            if b1 & 0x5F == 0:
                break
            if b1 & 0x1F == 0:
                e = dict(at=p, gfx=mem[p + 2] << 8 | mem[p], wm=b1 >> 7, ind=(b1 >> 5) & 1,
                         pal=mem[p + 3] >> 5, w=32 - (mem[p + 3] & 31), x=mem[p + 4], n=5)
                p += 5
            else:
                e = dict(at=p, gfx=mem[p + 2] << 8 | mem[p], wm=None, ind=None,
                         pal=b1 >> 5, w=32 - (b1 & 31), x=mem[p + 3], n=4)
                p += 4
            ents.append(e)
            n += 1
        zones.append(dict(at=a, line=line, h=h, dli=b0 >> 7, h16=(b0 >> 6) & 1, h8=(b0 >> 5) & 1, dl=dl,
                          ents=ents, end=p))
        line += h
        a += 3
    return zones


def main():
    rd = sys.argv[1]
    verbose = "-v" in sys.argv
    frames = [int(x) for x in sys.argv[2:] if x.isdigit()]
    if not frames:
        frames = sorted(int(os.path.basename(p)[5:10]) for p in glob.glob(os.path.join(rd, "mem_f*.bin")))
    for fr in frames:
        mem = open(os.path.join(rd, "mem_f%05d.bin" % fr), "rb").read()
        regs = {}
        bank = None
        for ln in open(os.path.join(rd, "regs_f%05d.txt" % fr)):
            p = ln.split()
            if p[0] == "frame":
                bank = p[3]
            elif p[1] != "--":
                regs[int(p[0], 16)] = int(p[1], 16)
        if 0x2C not in regs or 0x30 not in regs:
            print("f%d: no DPP written yet" % fr)
            continue
        dll = regs[0x2C] << 8 | regs[0x30]
        if dll >= 0x8000:
            print("f%d: DLL %04X in ROM (bank %s) - not decoded from the RAM dump" % (fr, dll, bank))
            continue
        zones = decode(mem, dll)
        out = open(os.path.join(rd, "dll_f%05d.txt" % fr), "w")
        out.write("frame %d DLL %04X CTRL(last) %02X CHARBASE(last) %02X bank %s\n" %
                  (fr, dll, regs.get(0x3C, 0), regs.get(0x34, 0), bank))
        out.write("palettes(last): " + " ".join("%02X" % regs.get(a, 0) for a in range(0x20, 0x40)) + "\n")
        dls, gfx, maps = [], {}, {}
        nent = nind = n5 = nwm = 0
        for z in zones:
            out.write("zone @%04X line %3d h %2d %s%s%s DL %04X (%s) %d bytes\n" %
                      (z["at"], z["line"], z["h"], "DLI " if z["dli"] else "", "H16 " if z["h16"] else "",
                       "H8 " if z["h8"] else "", z["dl"], region(z["dl"]), z["end"] - z["dl"] + 2))
            dls.append(z["dl"])
            for e in z["ents"]:
                nent += 1
                kind = "ind" if e["ind"] else "dir"
                if e["n"] == 5:
                    n5 += 1
                if e["wm"]:
                    nwm += 1
                if e["ind"]:
                    nind += 1
                    maps.setdefault(region(e["gfx"]), []).append(e["gfx"])
                else:
                    gfx.setdefault(region(e["gfx"]), []).append(e["gfx"])
                out.write("    %04X: %s %04X (%s) w%2d pal%d x%3d%s\n" %
                          (e["at"], kind, e["gfx"], region(e["gfx"]), e["w"], e["pal"], e["x"],
                           "" if e["wm"] is None else " wm%d" % e["wm"]))
        out.close()
        print("f%d: DLL %04X (%s), %d zones (heights %s), %d DLI; lists in pages %s (%s)" %
              (fr, dll, region(dll), len(zones), ",".join(str(h) for h in sorted(set(z["h"] for z in zones))),
               sum(z["dli"] for z in zones), spans(dls), "/".join(sorted(set(region(d) for d in dls)))))
        print("      %d objects (%d 5-byte, %d indirect, %d wm=1); CTRL %02X CHARBASE %02X bank %s" %
              (nent, n5, nind, nwm, regs.get(0x3C, 0), regs.get(0x34, 0), bank))
        for reg, lst in sorted(gfx.items()):
            print("      direct gfx in %s: %d objects, pages %s" % (reg, len(lst), spans(lst)))
        for reg, lst in sorted(maps.items()):
            print("      char maps in %s: %d objects, pages %s" % (reg, len(lst), spans(lst)))
        if verbose:
            print(open(os.path.join(rd, "dll_f%05d.txt" % fr)).read())


if __name__ == "__main__":
    main()
