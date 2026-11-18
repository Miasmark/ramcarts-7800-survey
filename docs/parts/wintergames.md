## Winter Games (Epyx / Atari 1987, 128K SuperGame + 16K RAM)

Read `summergames.md` first: Winter Games is the same shell rebuilt with the code moved (the
opening picture is Summer's stadium recoloured, and bank 2 still holds the string "SUMMER GAMES").
This file gives the differences. Evidence tags as there. Runs in `wintergames/runs/`, listings in
`wintergames/disasm/` (traced from each bank's `$8000`/`$8003`: 9-22% of each code bank reached),
the tube measurement in `wintergames/tools/tube.py`, the shared tools in `summergames/tools/`.

### Coverage

- Live: boot, opening picture, menus, and all four events through "Practice one event". Bobsled
  ran whole, five runs (run `e3`). Ski jump jumped (run `e2`). Biathlon loaded and stood at the
  start (the script does not ski), speed skating false-started.
- Code read: the unpacker and its twelve callers, the event launcher, the bobsled's drawing
  (`b4:$885D-$894B`, `$8FD5-$9010`) and NMI (`b4:$8329`). Biathlon, ski jump and skating are
  described from logs, list dumps and their unpack calls only.

### The same

- NMI vector `$8003`; every code bank opens with `JMP entry` / `JMP nmi` (b0 `$9A4F`/`$9985`, b1
  `$9A80`/`$99E0`, b2 `$8006`/`$80EB`, b3 `$8445`/`$8358`, b4 `$83DC`/`$8329`); the fixed bank's
  table at `$C000` (shell `$C10D`, shell NMI `$C015`, tune calls `$D1F7`/`$D1F9`/`$D1F0`, sound tick
  `$CDEE`) (code).
- One bank-switch routine, `f7:$FD80` (`STA $BFFF; RTS`), 8 callers (code).
- The run-length unpacker, the same routine instruction for instruction at `f7:$FE09-$FE41`
  (code; live: four streams decoded by `tools/verify.py` equal the dumps).
- The opening picture's build (lists in cart RAM `$6000-$64FF`, cells to `$6800`, 64 sprites to
  `$4500-$59BF`), the text screen at `$4000-$43BF`, the shell's variables at `$5964`, `$5990-$5995`,
  the flags screen (the same six streams, the same sizes) (live).
- Events are programs entered at `$8000` and left through `$C000`; lasting state is in console RAM
  `$2700`...; cart RAM is cleared by each event (code, live clears).
- TIA sound only: every AUDV store is in the fixed driver `f7:$CE26-$CEE7` (code: byte search).

### What is different

- **A data bank that can stay in while the screen is on.** Bank 6 (font, pictures, the shell's
  tables) opens with `JMP $C000` / `JMP $C003`: six bytes that forward the entry and the NMI to the
  fixed bank. The shell runs with bank 6 in the window (live: bank register 6 through the menus),
  reads its tables straight from it (`b6:$BF7E` event flag pointers, `b6:$BF86` event banks
  `00 03 01 04`), and its DLIs still arrive. Summer needed a second copy of the fixed bank in the
  window for that, and a DMA-off visit for every table in bank 6. Bank 5 (biathlon's pictures) has
  no stub and is still visited only with DMA off (live: bank 5 in for frames 286-303, 311-328,
  332-350 of run `e0`, screen off).
- **Every event is a full-screen picture, so the events share one screen kit** (live, list dumps):
  DLL and lists stay in the shell's console RAM block (`$2206`/`$2207`, lists `$2200-$24FF`), the
  font stays in console RAM `$1800`, the picture is a 40-byte 160A bitmap in cart RAM
  `$6000-$7FBF` (four 2K blocks `$7F0` apart, two 20-byte objects a zone, 8,128 bytes), sprites sit
  a line a page in `$4000-$57FF`, and the NMI reloads palettes band by band (`b4:$8329`: a DLI
  counter in `$97`, a compare chain, P2, P4 and P7 rewritten at each stage; code). Summer's events
  each had their own list layout in `$1800-$1DFF`.
- **Far more unpacking, and pictures on demand** (code for the calls, sizes by `tools/rle.py`):

| Event | Stream | Packed | Unpacked | Ratio | To |
|---|---|---|---|---|---|
| shell | font `b6:$8006` | 773 | 2,048 | 0.38 | `$1800` |
| biathlon (b0) | `b0:$AA49` | 734 | 2,048 | 0.36 | `$5800` |
| | scenes `b5:$8000`, `$8F14`, `$A29C` (table `b0:$A6CA`, index `$27DA`) | 3,851 / 4,984 / 3,765 | 8,016 / 8,128 / 8,016 | 0.48 / 0.61 / 0.47 | `$6000` |
| | scene 3 `b0:$AD2D` | 4,034 | 8,016 | 0.50 | `$6000` |
| ski jump (b1) | `b1:$A746`, `b6:$8312` | 6,025 / 5,975 | 8,128 each | 0.74 | `$6000` |
| speed skating (b3) | `b3:$A797` | 991 | 1,025 | 0.97 | `$6000` (character map) |
| bobsled (b4) | picture `b6:$9A69` | 5,341 | 8,128 | 0.66 | `$6000` |
| | `b2:$AA00`, `b6:$AF59` | 367 / 530 | 2,048 each | 0.18 / 0.26 | `$5800`, `$4024` |
| flags | six blocks in banks 6, 5, 3, 3, 5, 6 | 8,863 | 12,288 | 0.72 | as Summer |

  - Biathlon's course is four pictures swapped in the same 8K of cart RAM, each unpacked when the
    skier reaches it (code), about 18 frames of blank screen a picture (live: three unpacks in a
    row at load, frames 286-350 of run `e0`, of 8,016, 8,128 and 8,128 bytes; the picture then on
    screen equals `b5:$8F14` byte for byte; why three at load, and the later scenes, were not
    followed). Ski jump swaps its two
    pictures every jump (live: `$FE37` wrote 6 x 8,128 bytes in run `e2`).
  - The table-driven callers carry a bank byte per stream, and the flag blocks were moved into
    whatever banks had room left (table `f7:$C20B`, banks `$C223` = `06 05 03 03 05 06`; code).
  - Ski jump's dithered pictures pack worst (0.74) and skating's map not at all (0.97).
- **Speed skating keeps Summer's track kit instead**: a character screen with its map in cart RAM
  (pages `$60`, `$68`), CTRL `$43`, direct graphics in pages `$40`, `$48-$49` (live, list dump of
  run `e1`, frame 681).

### Bobsled, looked at properly

Cart RAM (live, run `e3`): `$6000-$7FBF` the screen picture (map, frame, speed gauge), unpacked
once a run; `$4824`... 19 x 40 bytes, the tube view, redrawn whole when the curve changes;
`$4024`... the near view of the tube, 12 x 7 cells, patched in place; `$4800-$4F23` the sled, six
bytes a row (`b4:$8FFB`); `$4080-$57FF` cleared by the fixed bank's block fill `f7:$FDDB`.

- **The tube view is 31 stored frames in a mask-per-cell packing** (`b4:$885D-$88CF`, pointer
  table `b4:$8DD6` with 35 entries; code, and live: `tools/verify.py` rebuilds frames 0, 18 and 20
  and each equals the 760 bytes in a dump). The picture is cut into cells of one byte by 8 lines,
  stored column by column, five cells a column, 19 columns. A cell is one mask byte, then one
  literal byte for each set bit; a clear bit draws the background byte `$AA`. So only bytes that
  differ from the background are stored, at a cost of one bit each.
  - Measured (`wintergames/tools/tube.py`): 31 distinct frames, 23,560 bytes unpacked, **8,788
    bytes in ROM, ratio 0.37**; a frame is 191 to 673 bytes.
  - Time (live): 31,160 bytes written by `$889E` in 133 frames, 41 whole frames of the view in
    about 1,950 frames of play: one redraw every few frames, 760 stores each. The decoder calls a
    subroutine for every source byte (`f7:$FE4C`); a hint: about 30,000 cycles a redraw as written,
    under half that with the fetch inline.
- **The near view is the same packing as a patch** (`b4:$88D0-$894B`; code): a clear mask bit
  leaves the byte in RAM alone, a mask of zero either skips the cell or, if the next source byte is
  `$33`, fills the cell's 8 lines with the byte after it. A frame of it stores only what changes
  against what is already there.
- The decoders write only; nothing is read back from the picture.
- Frame: NMI `b4:$8329` as above; the unpack calls run with the screen off (live: black frames at
  each run's start in the sheet).

### Biathlon, from logs

Cart RAM (live, run `e0`): `$6000-$7FBF` the current course picture; `$5800-$5FFF` from
`b0:$AA49` (a hint: the status panel's characters or cells); `$4000-$57FF` skier sprites, a line a
page (writers `b0:$A59B` at load and the fixed bank's store helper `f7:$FE56` during play; what
each copies was not read). MARIA reads pages
`$40-$53`, `$58-$7F`. The scene index is `$27DA`; value 3 picks the stream in bank 0, the others
come from bank 5 (`b0:$A6D8-$A712`; code).

### Not determined

- Biathlon's scenes after the first, its shooting range, and what `$5800` holds.
- Skating's map and why it is run-length coded at all (it saves 34 bytes).
- Ski jump's flight and landing drawing; whether the jumper is composed like Summer's gymnast.
- The opening ceremony beyond the first picture, medal and record screens.
