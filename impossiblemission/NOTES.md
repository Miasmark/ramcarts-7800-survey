# Impossible Mission: working notes

Findings are in `docs/parts/impossiblemission.md` and `docs/parts/impossiblemission_techniques.md`.
This file only says how the runs were made and what each tool does.

## Runs (all through `tools/run.py`, windowless; give the Lua script as an absolute path)

    L="impossiblemission/tools/survey2.lua"
    python -I tools/run.py impossiblemission p2 "$L" "SCRIPT=300:-:0;10:-:1;140:-:0;400:l:0;200:-:0;400:r:0;600:r:0" "SNAPS=300,312,314,316,318,320,324,440,572,576,578,580,598,620,800,1300,1600"
    python -I tools/run.py impossiblemission p3 "$L" "SCRIPT=300:-:0;10:-:1;140:-:0;300:d:0;100:-:0;200:r:0" "SNAPS=448,470,...,478,520,600,760,840,1000"
    python impossiblemission/tools/runpz.py z3 "300:-:0;10:-:1;150:-:0;10:-:1;60:-:0;30:u:0;10:-:0;70:l:0;10:-:1;60:-:0;70:r:0;10:-:1;60:-:0;22:r:0;10:-:1;60:-:0;45:d:0;10:-:1;60:-:0;22:l:0;10:-:1;60:-:0" "640,700,780,850,880,950,1000,1080,1110,1160"
    python -I tools/run.py impossiblemission k1 "$L" "SCRIPT=300:-:0;10:-:1;140:-:0;400:l:0" "SNAPS=640" "POKES=340:6035=FE,6036=FE,6039=FE"

- Fire at frame 300 starts the game (set-up runs in frames 311-322). In the lift: left or right
  walks to a room (the room at the left of the start is room 30, at the right room 3), down
  rides the lift, fire opens the pocket computer's puzzle screen.
- The hand moves about 1.6 pixels a frame. From its start, 30 frames up puts it on the vertical
  flip icon; 70 frames left from there on the first piece of the list; 45 frames down from the
  top icon row on the colour buttons.
- `p2`: set-up and two rooms. `p3`: lift ride (DLL dumps on 9 consecutive frames) and the map.
  `z3`: a piece selected (frame 780), flipped (950), recoloured (1000); PCs `$7270-$7277` in
  `summary.txt`. `k1`: three objects of room 30 removed by poking the search table.
- The first game after power-on is always the same in MAME (password ALLIGATOR).

## Tools here

- `survey2.lua`: the shared `survey.lua` with PCs tagged by bank (`4A92C` = bank 4 `$A92C`,
  `7xxxx` = fixed bank) and `conw.txt`, a write log of console RAM `$1800-$27FF`.
- `ramuse.py RUN [F0 F1] [--lo A --hi B]`: every PC that wrote or read a range, sorted by address;
  `--nz FRAME` non-zero runs of a dump; `--diff FA FB` what changed between two dumps.
- `rooms.py [-v]`: decodes the 32 room records from the ROM (output in `disasm/rooms.txt`).
- `runpz.py RUN SCRIPT SNAPS`: a run with all 36 pieces poked into the inventory at frame 340.
- `mkannot.py RUN...`: makes `disasm/annotations.json` (trace entries = every logged PC) and runs
  the toolkit's `disasm.py`; `lst.py SPACE START END` prints a listing range compactly.

## Listing coverage

Traced from live PCs only: bank 3 6%, bank 4 32%, bank 5 29%, bank 7 38% of bytes reached as
code; banks 2 and 6 not traced (bank 6 read by hand at `$B2EE` only). No labels or comments.
The tracer names bank 5 routines called after an unresolved switch as `sub4_`/`dat4_` in
`f7.asm` (the switch at 7:`DEFF` takes the bank in A); read them in `b5.asm`.
