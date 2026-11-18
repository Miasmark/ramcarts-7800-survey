"""mkprof.py: build prof.lua = the opcode tables of the toolkit's cyclebudget.lua + prof_tail.lua."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("A7800_TOOLKIT", "a7800-toolkit/tools") + "/../probes/cyclebudget.lua"
lines = open(SRC).read().split("\n")
keep = [ln for ln in lines if ln.startswith(("local MACHINE", "                and manager", "local cpu", "local mem",
                                              "local PCs", "local CYC", "local MODE", "local PEN"))]
tail = open(os.path.join(HERE, "prof_tail.lua")).read()
open(os.path.join(HERE, "prof.lua"), "w").write("\n".join(keep) + "\n" + tail)
print(len(keep), "lines kept")
