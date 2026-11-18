"""go.py GAME RUN EVENT PLAY [KEY=VALUE ...]: a survey run that goes title -> main menu -> Practice one
event -> event number EVENT (0-5; Winter Games 0-3), then plays PLAY (a SCRIPT fragment, may be
empty: "600:-:0").  Snapshots: SNAPS=... given, or every SNAPEVERY frames (default 100) from frame
MENUEND on.  LUA=script (default survey.lua).  Prints the frame the event choice is made at.
  summergames: fire at 100 (title), menu up by ~115.  Menu moves need the stick held 8 frames.
  Options (KEY=VALUE): MODE=practice|one (menu option 4 or 3), PRE=frames before the first fire.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))


def main():
    game, run, event, play = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    kv = dict(a.split("=", 1) for a in sys.argv[5:])
    pre = int(kv.pop("PRE", "100"))
    opt = {"practice": 3, "one": 2, "all": 0}[kv.pop("MODE", "practice")]
    down = "9:d:0;12:-:0;"
    s = "%d:-:0;5:-:1;60:-:0;" % pre
    s += down * opt + "6:-:1;40:-:0;" + down * event + "6:-:1;20:-:0;"
    t = sum(int(x.split(":")[0]) for x in s.split(";") if x)
    s += play
    total = sum(int(x.split(":")[0]) for x in s.split(";") if x)
    every = int(kv.pop("SNAPEVERY", "100"))
    snaps = kv.pop("SNAPS", None)
    if snaps is None:
        snaps = ",".join(str(f) for f in range(t - 30, total + 1, every))
    elif snaps.startswith("+"):
        snaps = ",".join(str(t + int(x)) for x in snaps[1:].split(","))
    lua = kv.pop("LUA", "survey.lua")
    cmd = [sys.executable, "-I", os.path.join(PROJ, "tools", "run.py"), game, run, lua,
           "SCRIPT=" + s, "SNAPS=" + snaps, "END=%d" % total] + ["%s=%s" % i for i in kv.items()]
    print("event chosen at frame", t, "end", total)
    open(os.path.join(PROJ, game, "runs", run + ".script.txt"), "w").write(
        "SCRIPT=%s\nSNAPS=%s\nT0=%d\n" % (s, snaps, t))
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
