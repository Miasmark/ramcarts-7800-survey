"""mkannot.py RUNDIR [RUNDIR ...]: build disasm/annotations.json from the bank-tagged PCs that
survey2.lua logged (cpuw.txt, cpur.txt, conw.txt, regs.txt, bank.txt), plus extra entries
in disasm/entries_extra.txt (one "bN:ADDR" or "f7:ADDR" a line, '#' comments), then run the
toolkit's disasm.py into disasm/. Every PC of a logged access is the start of a real
instruction, so each is a safe trace entry."""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.dirname(HERE)
ROM = (os.environ.get("A7800_ROMS", "roms") + "/Impossible Mission (NTSC) (Atari) (1987) (3B1F2F47).a78")
TOOLKIT = os.environ.get("A7800_TOOLKIT", "a7800-toolkit/tools")


def space(tag):
    b, pc = tag >> 16, tag & 0xFFFF
    if pc >= 0xC000:
        return "f7:%04X" % pc
    if pc >= 0x8000:
        return "b%d:%04X" % (b, pc)
    return None


def main():
    ents = set(["f7:EE33", "f7:FF33", "f7:EE36"])
    for rd in sys.argv[1:]:
        for name in ("cpuw.txt", "cpur.txt", "conw.txt"):
            p = os.path.join(rd, name)
            if not os.path.exists(p):
                continue
            for ln in open(p):
                for m in re.finditer(r" ([0-9A-F]{5}):\d+:", ln):
                    s = space(int(m.group(1), 16))
                    if s:
                        ents.add(s)
        for name in ("regs.txt", "bank.txt"):
            p = os.path.join(rd, name)
            if not os.path.exists(p):
                continue
            for ln in open(p):
                for m in re.finditer(r"\(([0-9A-F]{5})\)", ln):
                    s = space(int(m.group(1), 16))
                    if s:
                        ents.add(s)
    extra = os.path.join(GAME, "disasm", "entries_extra.txt")
    if os.path.exists(extra):
        for ln in open(extra):
            ln = ln.split("#")[0].strip()
            if ln:
                ents.add(ln)
    os.makedirs(os.path.join(GAME, "disasm"), exist_ok=True)
    cfg = os.path.join(GAME, "disasm", "annotations.json")
    old = {}
    if os.path.exists(cfg):
        old = json.load(open(cfg))
    old["entries"] = sorted(ents)
    json.dump(old, open(cfg, "w"), indent=1)
    print(len(ents), "entries")
    r = subprocess.run([sys.executable, "-I", os.path.join(TOOLKIT, "disasm.py"), ROM, "-c", cfg,
                        "-o", os.path.join(GAME, "disasm"), "--ignore-lint"],
                       capture_output=True, text=True)
    out = (r.stdout + r.stderr)
    open(os.path.join(GAME, "disasm", "disasm.log"), "w").write(out)
    print(out[-1500:])


if __name__ == "__main__":
    main()
