"""regen.py: regenerate the traced listing in jinks/disasm/src from jinks/disasm/annotations.json
with the toolkit's disasm.py (read-only use of the toolkit). Prints the coverage lines."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DIS = os.path.join(HERE, "..", "disasm")
ROM = (os.environ.get("A7800_ROMS", "roms") + "/Jinks (NTSC) (Atari) (1989) (0818D8CD).a78")
TOOL = os.environ.get("A7800_TOOLKIT", "a7800-toolkit/tools") + "/disasm.py"
r = subprocess.run([sys.executable, "-I", TOOL, ROM, "-c", os.path.join(DIS, "annotations.json"),
                    "-o", os.path.join(DIS, "src")] + sys.argv[1:], capture_output=True, text=True)
lines = (r.stdout + r.stderr).splitlines()
for ln in lines:
    if "%" in ln or "error" in ln.lower() or "unresolved" in ln.lower():
        print(ln[:200])
