"""run.py: one windowless MAME run of a cart with a Lua autoboot script, in its own folder.

usage: python -I run.py GAME RUNNAME LUA [KEY=VALUE ...]
  GAME     towertoppler | jinks | impossiblemission | summergames | wintergames
  RUNNAME  folder <project>/<GAME>/runs/<RUNNAME> (wiped first)
  LUA      a script in tools/ (name only) or a path
  KEY=VALUE environment for the script (SCRIPT, SNAPS, END, ...)
Options (as KEY=VALUE too): DEBUG=1 adds "-debugger script -debug"; BIOS=name (default skip).
MAME is the user's fork, always -video none -sound none -nothrottle, with ui.ini skip_warnings 1
and its own cfg / nvram / snapshot directories inside the run folder.
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
MAME = os.environ.get("A7800_MAME", "a78.exe")
ROMDIR = os.environ.get("A7800_ROMS", "roms") + "/"
ROMS = {
    "towertoppler": "Tower Toppler.a78",
    "jinks": "Jinks (NTSC) (Atari) (1989) (0818D8CD).a78",
    "impossiblemission": "Impossible Mission (NTSC) (Atari) (1987) (3B1F2F47).a78",
    "summergames": "Summer Games (NTSC) (Atari) (1987) (65C6DF3F).a78",
    "wintergames": "Winter Games (NTSC) (Atari) (1987) (8981B531).a78",
}


def main():
    game, runname, lua = sys.argv[1:4]
    kv = dict(a.split("=", 1) for a in sys.argv[4:])
    rd = os.path.join(PROJ, game, "runs", runname)
    shutil.rmtree(rd, ignore_errors=True)
    os.makedirs(os.path.join(rd, "cfg"))
    open(os.path.join(rd, "ui.ini"), "w").write("skip_warnings 1\n")
    rom = os.path.join(ROMDIR, ROMS[game])
    if not os.path.isabs(lua) and not os.path.exists(lua):
        lua = os.path.join(HERE, lua)
    env = dict(os.environ)
    env.update(kv)
    env["TOOLS"] = HERE.replace("\\", "/")
    cmd = [MAME, "a7800", "-cart", rom, "-bios", kv.get("BIOS", "skip"), "-skip_gameinfo",
           "-video", "none", "-sound", "none", "-nothrottle", "-inipath", ".",
           "-cfg_directory", "cfg", "-nvram_directory", "nv", "-snapshot_directory", "snap",
           "-autoboot_script", lua]
    if kv.get("DEBUG"):
        cmd += ["-debug", "-debugger", "script"]
    with open(os.path.join(rd, "mame.out"), "w") as o:
        r = subprocess.run(cmd, cwd=rd, env=env, stdout=o, stderr=subprocess.STDOUT,
                           timeout=int(kv.get("TIMEOUT", "1800")))
    print("exit", r.returncode, rd)
    out = open(os.path.join(rd, "mame.out")).read()
    if out.strip():
        print(out[-2000:])


if __name__ == "__main__":
    main()
