# Jinks: working notes (2026-11-18)

Findings are in `docs/parts/jinks.md` and `docs/parts/jinks_techniques.md`. This file only says how
the runs were made. All from the project root, through `tools/run.py` (windowless).

## Runs

- `s1`: the coordinator's first survey (fire pulsed, 3,000 frames).
- `s2_move`: `SCRIPT=150:-:0;10:-:1;100:-:0;10:-:1;100:-:0;10:-:1;320:-:0;400:r:0;400:l:0;200:u:0;200:d:0;300:r:1;300:r:0`,
  21 snaps from 690 to 2500. Scroll positions; `map_level1.png` is the whole level drawn from the
  dump's map and character set (`jinks/tools/mapinfo.py DUMP --png=OUT`).
- `s3_levels`: the same start with `520:-:0` as its last step, then four times
  `20:-:4;20:-:12;20:-:0;640:r:0` (Pause, Pause + Select, release: the next level). Snaps 890, 1250,
  1590, 1950, 2290, 2650, 2990, 3350, 3690. Bank log: levels 1-2 load from bank 6 and play in bank
  4; levels 3-4 load from bank 5 and play in bank 3; the fifth wraps to level 1.
  The skip only works once the level's start phase is over (about 340 frames after the load).
- `s4_brick`: `POKES=720:CC=70,CD=00,CE=12` puts the ball (x `$CC/$CD`, y `$CE`) on a brick of
  level 1; `cpuw.txt` shows `$E7E6`/`$E7E9` storing `$FD` into the two cells, five times as the
  ball falls through the block.
- `s5_bonus`: `POKES=900:2130=01` sets the level-complete flag: the interlude loads
  (`$D0D7` copies 1,024 bytes to `$6000`).

## Zero page and RAM seen

`$40/$41` DPP shadow, `$42/$43` the back list set, `$44/$45` NMI vector, `$46` DLI counter, `$47`
spin flag, `$48/$49` background colour toggle, `$50` map page select (`$00`/`$20`), `$51` level,
`$56/$57` scroll x, `$CC/$CD` ball x, `$CE` ball y, `$D1` tile animation divider, `$EA` frames since
the last game frame, `$F4/$F5` sample pointer, `$2111-$2113` score (BCD), `$212E` saved bank,
`$2130` level complete, `$2137` sample may be interrupted.

## Listing

`python jinks/tools/annotate.py` writes the labels into `disasm/annotations.json` and regenerates
`disasm/src/`; `python jinks/tools/show.py D7E8 D845` prints a range compactly.
