# Tower Toppler: working notes (2026-11-18)

Findings are in `docs/parts/towertoppler.md` and `docs/parts/towertoppler_techniques.md`. This file
says what is in this folder and how to repeat a run.

## Getting to places

- Boot, fire pulses at frames 30, 240, 450: play on tower 1 from about frame 620 (the submarine
  arrives first). Script: `SCRIPT=30:-:0;10:-:1;200:-:0;10:-:1;200:-:0;10:-:1;240:-:0;...`
- Walking right from frame 700 walks off the platform about 80 frames later (he drowns, the tower
  restarts): enough frames of rotation to measure.
- Intermission: `POKES=720:B1=02` (the tick result "tower done"). It starts about frame 796.
- Camera/scroll: poke `$89` (player y, 2 lines a unit). Map: poke `$6A00 + 16*row + column`.
- Colours: poke the shadow `$64C0-$64C7` (P0C2-P7C2 of the window).

## Tools (`tools/`)

- `tt.lua`: the shared `survey.lua` plus `pal.txt` (every MARIA register write with line and PC,
  logged when a frame's sequence changes), `conw.txt` (CPU writes to `$1800-$27FF` by PC) and a
  console-RAM section in `summary.txt`. Give `run.py` its full path.
- `paldig.py RUNDIR`: digest of `pal.txt` with the line numbers dropped.
- `prof.lua` (built by `mkprof.py` from the toolkit's `cyclebudget.lua` tables and
  `prof_tail.lua`): cycles per frame, split by the main loop's routines (`TOPLO`/`TOPHI` = the PC
  range of the loop body), NMI code, WSYNC stalls (timed) and DMA as the remainder. Takes `SCRIPT`
  and `POKES` like survey.lua. Output `prof.txt`.
- `d.py BANK START END [cols]`: compact linear disassembly; `d.py BANK ADDR N --hex`.

## Runs (`runs/`)

- `s1`: the coordinator's first survey (title, high scores, play, idle).
- `w1`: tt.lua, walking right/left, dying, restarts; dumps every 50 frames from 650.
- `i1`: the intermission (poke at 720), dumps to frame 3000.
- `v1`: `$89` poked at 700 to move the camera: DLL heights, CHARBASE, last-zone pages.
- `k1`: map cells and two colours poked at 690; `cmp_f700.png` compares with `w1`.
- `p1`: prof.lua over frames 100-790 (title, entering, standing, walking).
- `p2`: prof.lua in the intermission (frames 1000-1012, `TOPLO=B3A3 TOPHI=B447`).

## Disassembly (`disasm/`)

`annotations.json` + the toolkit's `disasm.py --cycles` give `f3.asm`, `b0-b2.asm`
(`disasm_report.txt` is the tracer's report). Entries added by hand: the four NMI stages (the vector
is `JMP ($0060)`), the blit routines reached through `JMP ($0062)`, the sound drivers, and bank 2's
intermission. The names cover what was read: display, tower, sprites, frame, loader. Game logic
(`F28E-F9FF`) and most of bank 2 are traced but unread; b0 and b1 are data.

## Traps met

- Shell heredocs eat backslashes here: Lua/Python with `\n` goes through the Write tool.
- `pal.txt` changes every frame (the bottom DLI lands on line 257 or 258): use `paldig.py`.
- A summary of read PCs is long: pipe everything through `head`/`cut`.
- Dumps taken through the read tap show the dump's own reads under the PC at that moment
  (`FD94`, `C607`, ... with range `4000-7FFF` in `s1`'s summary): not the game's.
