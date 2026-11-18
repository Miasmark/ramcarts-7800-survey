"""runpz.py RUN SCRIPT SNAPS [LUA]: a run with all 36 puzzle pieces poked into the inventory at
frame 340 (what the dead debug branch at 7:$C861 does: $6740+i = i, $6770+i = i&3 (3 -> 0),
$6E12 = $24, $73AE = 1, $73AB = 9, $6764 = $FF), then SCRIPT (survey.lua syntax) from frame 0."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))


def main():
    run, script, snaps = sys.argv[1:4]
    lua = sys.argv[4] if len(sys.argv) > 4 else os.path.join(HERE, "survey2.lua").replace("\\", "/")
    p = []
    for i in range(36):
        p.append("%X=%X" % (0x6740 + i, i))
        c = i & 3
        p.append("%X=%X" % (0x6770 + i, 0 if c == 3 else c))
    p += ["6764=FF", "6E12=24", "73AE=1", "73AB=9"]
    pokes = "340:" + ",".join(p)
    cmd = [sys.executable, "-I", os.path.join(PROJ, "tools", "run.py"), "impossiblemission", run, lua,
           "SCRIPT=" + script, "SNAPS=" + snaps, "POKES=" + pokes]
    for a in sys.argv[5:]:
        cmd.append(a)
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
