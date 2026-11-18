"""annotate.py: add the labels this survey settled on to jinks/disasm/annotations.json (idempotent),
then run regen.py. Labels only for routines that were read; see docs/parts/jinks.md for coverage."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "disasm", "annotations.json")
LABELS = {
    "f7:C046": "Boot_TitleAndSample",
    "f7:C07F": "Menu_Enter",
    "f7:C0A2": "Menu_SampleLoopA",
    "f7:C141": "Menu_SampleLoopB",
    "f7:C1B7": "Game_New",
    "f7:C1D1": "Level_GetReadyAndLoad",
    "f7:C221": "Play_StartPhaseLoop",
    "f7:C2C7": "Play_MainLoop",
    "f7:C695": "Game_Over",
    "f7:C6E9": "Title_BuildPicture",
    "f7:CB47": "Level_Load",
    "f7:CECC": "Interlude_Load",
    "f7:D73D": "Nmi_SetHandler",
    "f7:D759": "Nmi_Play",
    "f7:D7BB": "Nmi_Interlude",
    "f7:D7E8": "Scroll_WriteRowHeaders",
    "f7:D846": "Lists_ResetSpriteFill",
    "f7:D882": "Objects_Walk",
    "f7:DF69": "Tile_RotateCharFA",
    "f7:E446": "Read_ConsoleSwitches",
    "f7:E4B9": "Wait_VblankEdge",
    "f7:E4C2": "Wait_Vblank",
    "f7:E4C7": "Sound_Tick",
    "f7:E572": "Sound_Off",
    "f7:E589": "Sound_Request",
    "f7:E719": "Ball_MapCollide",
    "f7:E7E4": "Brick_Erase",
    "f7:FC91": "Sample_Play",
    "f7:FCF6": "Sample_PlayTail",
    "f7:FD2E": "Sample_CopyToRam",
    "f7:FD5B": "Display_Off",
}
COMMENTS = {
    "f7:CB5E": "level bank: dat_FD63[(level&3)>>1] = 6,5; map page $80 or $A0 by ram_0050",
    "f7:CB79": "21 pages of map, copied as stored (no unpacking)",
    "f7:CB9B": "8 pages of character set $9500 -> $7500",
    "f7:CC5B": "play bank = level bank - 2 (sprites, object lists, sound tables)",
    "f7:D77D": "the bank's own number is its byte at $BFFF: saved for the restore",
    "f7:D79A": "spin inside the NMI until the next DLI clears ram_0047",
    "f7:DF7D": "rotate the byte right twice (one 160A pixel), in each of the 8 line pages",
    "f7:E7E6": "both cells of the brick become $FD (floor); score delta to $7FFB",
    "f7:FCB2": "a byte = two 4-bit samples, high nibble first, one every 3 lines",
}
a = json.load(open(PATH))
a.setdefault("labels", {}).update(LABELS)
a.setdefault("comments", {}).update(COMMENTS)
json.dump(a, open(PATH, "w"), indent=2)
subprocess.run([sys.executable, "-I", os.path.join(HERE, "regen.py")])
