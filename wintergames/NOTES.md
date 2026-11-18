# Winter Games: working notes

Findings are in `docs/parts/wintergames.md` (differences from Summer Games) and
`docs/parts/summergames_techniques.md`. The tools are Summer Games' (`summergames/tools/`, see
`summergames/NOTES.md`); `wintergames/tools/tube.py` measures the bobsled's tube frames.

## Runs (`wintergames/runs/`)

| Run | What |
|---|---|
| `s1` | the coordinator's first survey (title, menu, name entry) |
| `e0` | practice: biathlon (bank 0, pictures from bank 5). Loads, stands at the start: the script does not ski |
| `e1` | practice: speed skating (bank 3). False start |
| `e2` | practice: ski jump (bank 1, second picture from bank 6). Several jumps |
| `e3` | practice: bobsled (bank 4, pictures from banks 6 and 2). Five runs |

All four made with `summergames/tools/go.py wintergames eN N PLAY SNAPEVERY=130`; the full script
of each is in `runs/eN.script.txt`. The menu behaves as Summer's (fire at frame 100, stick held 9
frames a move); the event list is A biathlon, B speed skating, C ski jump, D bobsled.

## Listing

`annotations.json` holds entry points only (each code bank's `$8000`/`$8003`, the fixed bank's
table at `$C000`, reset `$FEC5`). `disasm/*.asm`: bank 0 20%, bank 1 19%, bank 2 9%, bank 3 15%,
bank 4 17%, bank 7 22% reached as code. Banks 5 and 6 are data (bank 6 opens with
`JMP $C000` / `JMP $C003`).

## Notes

- Winter's font stream starts at `b6:$8006`, after the stub; decoding from `$8000` gives 2,127
  bytes and looks plausible but is wrong.
- The biathlon dump at frame 660 does not match the table's first stream (`b5:$8000`): three
  unpacks run one after another at load (frames 286-350: 8,016, 8,128, 8,128 bytes) and the
  picture that stays is `b5:$8F14` (equal byte for byte, `summergames/runs/verify.txt`).
