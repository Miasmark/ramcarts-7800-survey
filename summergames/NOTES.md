# Summer Games: working notes

Findings are in `docs/parts/summergames.md` and `docs/parts/summergames_techniques.md`. This file
says what is in the folder and how to repeat it.

## Tools (`summergames/tools/`, used for Winter Games too)

- `go.py GAME RUN EVENT PLAY [KEY=VALUE]`: title -> main menu -> "Practice one event" -> event
  number EVENT, then the SCRIPT fragment PLAY. Writes `runs/<RUN>.script.txt` with the full script.
  Menu timing: fire at frame 100 leaves the title; a menu move needs the stick held 8 frames
  (`f7:$D8FA` accepts a move after 5 of 8 frames), so each step is `9:d:0;12:-:0`.
- `lst.py GAME SPACE ADDR [N] [COLS]`: compact view of the traced listing in `<GAME>/disasm/`.
- `find.py GAME "HEX" [--ctx N]`: byte pattern search over the ROM, as bank:address.
- `rle.py GAME BANK SRC [DST]`: decodes a run-length stream, prints packed and unpacked sizes.
- `txt.py GAME BANK ADDR N`: bytes as text.
- `verify.py`: decodes streams, the diving mirror table and the bobsled tube frames and compares
  them with the memory dumps of the runs below.

## Runs (`summergames/runs/`)

| Run | What | Script |
|---|---|---|
| `s1` | the coordinator's first survey (title, menu, name entry) | fire pulsed |
| `m1` | menu attempt with 4-frame stick taps (too short: cursor did not move) | see sheet |
| `n1` | name entry ("3"), the flags screen, then diving in competition | in the run's command: `100:-:0;5:-:1;60:-:0;6:-:1;60:-:0;3:u:0;12:-:0;5:-:1;20:-:0;3:d:0;12:-:0;5:-:1;200:-:0;...` |
| `e0` | practice: platform diving (bank 3 loader, bank 4) | `e0.script.txt` |
| `e1` | practice: 4x400m relay (bank 1) | `e1.script.txt` |
| `e2` | practice: 100m dash (bank 1) | `e2.script.txt` |
| `e3` | practice: gymnastics (bank 0, data from bank 2) | `e3.script.txt` |
| `e4` | practice: freestyle relay (bank 5) | `e4.script.txt` |
| `e5` | practice: 100m freestyle (bank 5) | `e5.script.txt` |

Each run has `sheet.png` (contact sheet), the logs, memory dumps and decoded lists
(`dll_fNNNNN.txt` where `tools/dll.py` was run). The track and swim runs false-start: the play
script moves the stick before the gun. A script that waits for the gun was not written.

## Listing

`annotations.json` holds only entry points (each bank's `$8000`/`$8003`, the fixed bank's table,
`b3:$A800`, `b3:$A8FE`). `disasm/*.asm` is the toolkit tracer's output from them: bank 0 26%, bank 1
33%, bank 3 11%, bank 4 22%, bank 5 32%, bank 7 22% of bytes reached as code. Banks 2 and 6 are data.
No labels were added. Code behind computed jumps and the unreached parts were read, where needed,
with `tools/dis.py` from a known instruction.

## Things that cost time

- The memory dump made at each snapshot frame shows up in `cpur.txt` as 16,384 reads of
  `$4000-$7FFF` by whatever PC the frame ended on. Ignore read totals of exactly 16,384.
- `bank.txt` prints a frame only when its write sequence changes, so the bank that is in at a
  frame is the last non-empty line at or before it.
- The run-length streams end with `00 v 00`; a decode that stops at the first `00 00` is wrong
  (`00 00 n` is a run of zeros).
