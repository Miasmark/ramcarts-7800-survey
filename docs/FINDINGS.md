# Five retail carts with RAM at $4000: findings

Survey of 2026-11-18. Tower Toppler (64K SuperGame + RAM), Jinks, Impossible Mission, Summer Games
and Winter Games (128K SuperGame + RAM). This file is the consolidated view; the full write-up of
each game, with every address, is in `docs/parts/<game>.md`, and each game folder has a `NOTES.md`
listing its runs, scripts and listings. The harness and the rules every run followed are in
`tools/HARNESS.md`.

Evidence tags: **live** (seen in MAME: a write log, a list dump, a watch, a poke that changed
behaviour), **code** (read from a disassembly only), **hint** (a guess). Addresses are
`bank:address`; `f3`/`f7` is the fixed bank.

## Method and what was checked

- First pass, all five: `tools/survey.lua` logged every CPU write and read of `$4000-$7FFF` by PC
  and frame, MARIA's own reads of cart RAM by page (her `dma` address space), CTRL, CHARBASE and DPP
  writes by line, and bank writes; `tools/dll.py` decoded the DLL and every list from memory dumps.
- Second pass: four workers in parallel, one per game (Summer and Winter Games together). Deep on
  Tower Toppler and on Summer/Winter Games; survey plus a focused read on Jinks and Impossible
  Mission. The first guess had Tower Toppler plus "whichever unpacks": only the Epyx pair unpacks.
- Checked again by the coordinator: the tower packing. `towertoppler/tools/check_sparse2.py`
  decodes tower 1 from the ROM and compares it with `$6A00` in a play dump: 752 of 752 cells equal
  (live). Over eight towers it counts 2,483 packed bytes for 9,104 cells; the worker counted 2,487
  (the loader reads one row more than the table says: hint for the difference).
- Everything else below is each worker's finding with the worker's own tag.

## Across the five

- **Only Summer and Winter Games unpack** (one run-length scheme, plus the bobsled's mask-per-cell
  frames). Tower Toppler packs only its tower maps. Jinks and Impossible Mission store everything
  as drawn; Impossible Mission generates instead.
- **No game packs text.** Text is plain character codes everywhere.
- **Three games put display lists in cart RAM** (Tower Toppler always, Impossible Mission in rooms,
  the Epyx pair for the opening picture), each because console RAM was full of a RAM character set.
  Not allowed under BankSet.
- **Code in cart RAM**: only Impossible Mission, two 4-byte thunks at `$7270/$7274` (live).
- **`$4000-$5FFF` is never touched** by Tower Toppler, Jinks or Impossible Mission (live for the
  scenes run). They use 6-8K of the 16K.
- **Sampled sound**: only Jinks (f7:`$FC91`).
- **The bank's own number at `$BFFF`** appears in Tower Toppler and Jinks; the other three write the
  bank register at `$BFFF` and keep no shadow either.

## Tower Toppler

Full write-up: `docs/parts/towertoppler.md`. In one line: the play screen is one-colour 320A
throughout, and the tower is a 24 x 18 character map shown through a character set in which
character `c` draws the bit pattern `c`.

### Cart RAM map (live)

| Range | Size | Use | Writers | Read by |
|---|---|---|---|---|
| `$6000-$647F`, `$6500-$697F` | 1,152 each | two display-list sets, 18 zones x 64 bytes | f3:`E53E`, `E5DF`, `CA19`, `DE98` | MARIA |
| `$6480-$64FF`, `$6980-$699F` | 160 | variables; the window's colour shadow `$64C0-$64C7` | many | CPU, DLI f3:`FF19` |
| `$6A00-$707F` | 1,664 | unpacked tower map, 16 bytes a row | f3:`C8CA` | CPU |
| `$7100-$78FF` | 2,048 | sprite strip, 8 line pages x 256 columns, double-buffered by column bit 7 | f3:`DA08`, `DECC`, `E149` | MARIA only |
| `$4000-$5FFF`, `$7900-$7FFF` | 9,984 | never touched | - | - |

The lists are in cart RAM because console RAM is full: a generated 2K character set at `$1800`, two
24 x 18 maps, the DLL and the HUD (live for the occupancy, hint for the motive).

### Answers

- **Unpacking** (live): tower maps only. Per tower a stream of 2-byte row bitmaps (LSB first) and a
  stream of the non-zero cells; table b0:`AD00` (bitmap pointers, cell pointers, row counts).
  27% of unpacked size; decoder f3:`C8CA-C974`, 65 bytes plus setup; about 35,000 cycles a load
  (estimate).
- **320-mode colours** (live): CTRL `$43` everywhere, no write-mode bit, so all 320A; only BACKGRND
  and `P0C2-P7C2` are written. A colour is an object's palette. Two bands of eight: the window's
  DLI (f3:`FF19`) loads eight from the RAM shadow, the bottom DLI (f3:`FE8A`) the HUD's eight from
  f3:`D27D`; 56 cycles each. Bricks are one palette and a bit pattern. Text screens are one colour
  a line; only the HUD has several on a line, by cutting it into objects (3 palettes on a line).
  Headers are all 5-byte: `lo, $60 or $40, hi, palette<<5 | width, x`.
- **The rotation** (live): every tick the hidden map is rebuilt with byte masks. The wall is 8
  phases x 16 bytes (b2:`A200`); elements are ANDed and ORed in from four pre-shifted shapes at an
  x from a 128-byte angle table (b2:`A2D8`, shapes b2:`A100`); doors have one shape per angle (512
  bytes). 1,088 bytes of tables in all. Compositors f3:`C4AA`, `C6F7-C769`, `C630`.
- **The sea** (live): static dither, eight characters of rising density, one row of the same
  character per zone. No reflection, no animation.
- **Vertical scroll** (live): the first zone is 1-7 lines and the last 9 minus that; a DLI raises
  CHARBASE on the short last zone (f3:`FEEB`, `E6FF`).
- **The strip** (live): sprites are copied from the switched banks into fixed 3-byte columns;
  vertical position in 2-line steps by four entry points into unrolled copy code; clipping by byte
  masks. The art's bank is in only during the copy. Nothing is read back.
- **Frame cost** (live, `towertoppler/tools/prof.lua`): a play tick is always three frames (20 Hz)
  and rebuilds everything, moving or not: about 53,000 cycles, 31,000 of it the tower. DMA is 8,170
  cycles a frame in play, 12,870 in the 160A intermission. The NMI is `JMP ($0060)`, three stages
  re-arming each other; it switches banks for sound and restores from `$BFFF`.
- **Flip** (live): one DLL; the flip stores the list page into 18 DLL entries (f3:`E68B`).

### Dead ends and not determined

- The stepping CHARBASE `$18-$1E` is scroll compensation, not animation. The stores at
  `E5FE-E622` clear slots, they do not write lists.
- Not read: game logic f3:`F28E-F9FF`, most of b2, music and effect formats. Not run: towers 2-8,
  two-player play. DMA was measured as a remainder, not against `dmabudget.py`.

## Jinks

Full write-up: `docs/parts/jinks.md`. In one line: nothing is packed; cart RAM is a second bank
window, and what is copied there is then edited in place. All code is in bank 7.

### Cart RAM map (live)

| Range | Size | Use | Writers | Read by |
|---|---|---|---|---|
| `$6000-$7EFF` | 7,936 | title and menu: sample images from bank 0 | f7:`$FD3F` | CPU (f7:`$FC91`) |
| `$6000-$74FF` | 5,376 | play: character map, 21 rows x 256, a row a page | f7:`$CB79`; bricks f7:`$E7E6` | MARIA and CPU (f7:`$E719`) |
| `$7500-$7CFF` | 2,048 | character set, CHARBASE `$75` | f7:`$CB9B`; f7:`$DF87` | MARIA |
| `$7D00-$7DFF` | 256 | object records | f7:`$CC8C` | CPU |
| `$7F2F-$7FFE` | 208 | high scores, menu text, score digits, score delta | f7:`$FA43`, `$FC41` | MARIA and CPU |
| `$4000-$5FFF` | 8,192 | never touched | - | - |

### Answers

- **Level load** (live): a plain copy, 5 frames with the display off (f7:`$CB47`). Levels 1-2 are in
  bank 6 (play bank 4), 3-4 in bank 5 (play bank 3). Offline (`jinks/tools/romstats.py`): zlib would
  pack the maps to 23-32%, run-length only to 58-86%. The title is 16,000 bytes of unpacked 160B,
  all of bank 1.
- **Scrolling** (live): a row of the map in a page, so a scroll step is the header's low byte plus
  x; two objects a row (32 + 10 characters). f7:`$D7E8`.
- **Tile animation** (live): every 6th frame the 8 bytes of character `$FA` are rotated in the RAM
  set; every cell showing it moves (32 in level 1). f7:`$DF69`, about 470 cycles (estimate).
- **Bricks** (live): two map stores of the floor character (f7:`$E7E4`); collision reads the drawn
  map, with code ranges ordered by meaning.
- **One character set, four levels** (live): a level is a map, 6 palette bytes and a background
  (f7:`$CC34`).
- **Samples** (live): f7:`$FC91`, 4-bit pairs at 5,245 Hz clocked by WSYNC, the CPU locked, never
  during play; 24K of ROM for about 9 seconds.
- **Frame**: 30 Hz, slipping to 20; two full list sets flipped each frame; the HUD font comes from
  bank 2 by a DLI that spins inside the NMI.

### Dead ends and not determined

- f7:`$FD3F` copies samples; the first survey read it as a clear.
- Not measured: frame cost in cycles. Not known: whether the RAM chip is 8K, what f7:`$E3AB` and
  `$E42E` test, whether the H8 holes its sprites rely on work on hardware (live in MAME only).

## Impossible Mission

Full write-up: `docs/parts/impossiblemission.md`. In one line: the game is generated from a seed at
Reset and kept in cart RAM; a room's DLL, lists and character map are built there on entry.

### Cart RAM map (live)

| Range | Size | Use | Writers | Read by |
|---|---|---|---|---|
| `$6000-$67A8` | about 1,700 | the generated game: 172-byte search table, 9 puzzle pictures (1,296), 36 piece records, inventory, password | 4:`AE4E`, 4:`A9A9`, 4:`AA86` | CPU |
| `$6812-$6EA2` | about 1,000 | six 144-byte piece buffers and the cutting scratch | 4:`A8F3`, 4:`AB89` | CPU |
| `$6EA3-$73AE` | about 1,300 | variables, robots, the 9 x 6 room grid, lift positions, palette fade; the pocket computer's map and two text lines | 7:`D938`, 5:`8837`, 4:`8F57` | CPU; MARIA reads `$6FA9-$713D` |
| `$7270-$7277` | 8 | code: two patched thunks | 4:`AD96` | CPU executes |
| `$7400-$7B3F` | 1,856 | the room's DLL and lists, 68 bytes a zone | 7:`EE93` copies 6:`8800` | MARIA and CPU |
| `$7C00-$7FE7` | 1,000 | the room's 40 x 25 character map, also the collision map | 5:`9A2F-9E62` | MARIA and CPU |
| `$4000-$5FFF` | 8,192 | never written | - | - |

Console RAM `$1800-$1FFF` is a RAM character set and sprite canvas.

### Answers

- **Generation** (live dumps, formats from code): the building (108 bytes), hidden items, 94 robot
  behaviours and the puzzle pictures come from one 40-bit generator (7:`DB98`); 7:`D938-DA7F`,
  4:`AE4A`, 5:`8816`. The first game after power-on is always the same in MAME: the seed counter
  starts at 0.
- **Rooms** (live for two rooms): records of 80-185 bytes (floors as runs, doors, robots, lifts,
  furniture) expand into the 1,000-byte map and patches to a shared 1,856-byte list template. 32
  rooms cost 3,599 bytes. 5:`99CF-9E75`; decoder `impossiblemission/tools/rooms.py`.
- **Puzzle pieces** (live): four pieces from two masks, `picture AND (A or not A) AND (B or not
  B)`, cut on demand (4:`AB6F`); flips through a bit-reverse table (4:`AC99`, `AD0A`); recolour by
  palette bits (4:`AC26`). 2,688 bytes of tables against 5,184 stored.
- **Lists** (live): a background object is added by moving the zone's DLL pointer back 4 bytes
  (5:`9DF7`). Character rows are trimmed to their contents (5:`9CF5`, code).
- **Pocket computer** (live writes; the colour mapping is a hint): CTRL `$43` from a DLI at line
  159, 320C icon panels beside 320A text, C2 colours loaded by the DLI (7:`CBDC`).
- **Frame**: NMI is `JMP ($2101)`, three DLIs; the main loop waits on `$6EAE` against `$6FA1`.
  DLIs call bank 5 code.
- **Why RAM with 32K of ROM empty**: the game needed writable room, not more ROM (hint).

### Dead ends and not determined

- "No code in cart RAM" holds only outside the puzzle screen. `$6800-$6DA1` are CPU bitmaps, not
  MARIA's.
- Not determined: bank 2 (never selected in any run), the scene at 6:`B2EE`, how piece 0 is
  obtained, rooms 17 and 27. DMA and cycle costs are estimates. No sampled speech was found; not
  every AUDV store site was read.

## Summer Games

Full write-up: `docs/parts/summergames.md`. In one line: the Commodore 64 game's data kept in C64
shapes and converted at each scene's load into MARIA's line-per-page layout in cart RAM. Nothing in
cart RAM survives an event; lasting state is console RAM `$2600-$27FF`.

### Cart RAM map (live)

| Scene | Range | Use | Writers |
|---|---|---|---|
| Shell | `$4000-$43BF` | 40 x 24 text map | f7:`$FC30`, `$FC5D`, `$FC99` |
| Flags screen | `$4000-$57DF`, `$6000-$77DF` | nine flags, a two-layer 160A bitmap, 12K | f7:`$FE91` from bank 6 |
| Opening picture | `$6000-$65FF` | display lists (292 objects) | b3:`$8016` |
| | `$6800-$6FC5`, `$4500-$59BF` | background cells and 64 sprites, a line a page | b3:`$80EF`, `$814D` |
| Track | `$4000-$5FFF`, `$6000-$65FF` | font, 44 runner sprites, the character screen | b1:`$9CCF`, `$9E7C` |
| Gymnastics | `$4400-$5FFF`, `$6000-$7FFF` | the gymnast and strips; 8K of bank 2 copied in for the CPU | b0:`$8CCA`, f7:`$FD8D` |
| Diving | `$4300-$5FD7`, `$7800` | diver, font, strips; a bit-reversal table made by code | b4:`$8835`, `$88EA` |
| Swimming | `$4000-$5FFF`, `$6000-$7F1F` | swimmers, font, the unpacked pool picture | b5:`$A805`, f7:`$FE91` |

Events keep their lists and DLL in console RAM `$1800-$1E00`. No code runs from cart RAM.

### Answers

- **Run-length unpacker** (live: decoded streams equal the dumps): f7:`$FE63-$FE9B`, about 70 bytes.
  A non-zero byte is a literal, `00 v n` a run, `00 v 00` the end. Font 0.38, swim picture 0.37,
  flags 0.72. 410-450 bytes a frame with DMA off, about 69 cycles a byte. Pictures are stored in
  MARIA's layout, so runs follow scan lines.
- **Re-shaped, not packed** (live writers): sprites, fonts and cell strips sit in C64 shapes and are
  spread a line a page at load (b3:`$814D`, b1:`$9CCF`, b1:`$9E7C`, b3:`$80EF`).
- **One pose, four orientations** (live writers, code for the flags): the gymnast's frame is
  expanded into zero page, mirrored through a bit-reversal table, and written counting pages up or
  down (b0:`$8B41-$8D61`). Plain bit reversal works because the sprite palettes hold one colour
  three times. Diving generates the table with 18 bytes of code (b4:`$88EA`, live).
- **Event loading** (code, live): each code bank opens with `JMP entry` / `JMP nmi`, and the NMI
  vector is `$8003` in the window. The shell runs with bank 7 also in the window. Data banks 2 and
  6 are visited only with DMA off. One bank-switch routine, f7:`$FDDA`. An event is a program: it
  resets the stack and leaves by `JMP $C000`.
- **Text** (code, live writes): script interpreter f7:`$FC99` with cursor, jump and decimal codes.
- **Frame**: the shell polls MSTAT at 60 Hz; the track's NMI counts its DLIs and sets the frame
  flag from the middle of the screen.
- **Sound**: TIA only, all in the fixed driver (code).

### Dead ends and not determined

- f7:`$FC44-$FC56` is the text screen's clear, not a scroll. The font at `$1800` is a run-length
  stream, not a copy.
- Swimming is from logs and list dumps only. Not determined: the diver's page shifting, medal,
  record and ceremony screens. Track and swim runs false-started in the scripts.

## Winter Games

Full write-up: `docs/parts/wintergames.md`. The same shell, unpacker (f7:`$FE09`), opening picture,
text screen and flags screen as Summer Games (live).

### What is different

- **Every event is a full-screen picture**: a 40-byte 160A bitmap unpacked into cart RAM
  `$6000-$7FBF` (8,128 bytes), sprites a line a page in `$4000-$57FF`, lists and font in console
  RAM (live).
- **A data bank that can stay in with the screen on**: bank 6 opens with `JMP $C000` / `JMP $C003`,
  forwarding the entry and the NMI to the fixed bank (code, live).
- **Unpack ratios** (sizes by `summergames/tools/rle.py`): biathlon scenes 0.47-0.61, bobsled
  picture 0.66, ski jump's dithered pictures 0.74, skating's character map 0.97, small fonts
  0.18-0.38.
- **Pictures on demand**: biathlon keeps four 8K pictures packed and unpacks the one in view into
  the same RAM, about 18 blank frames a picture (live for the load, code for the swap). Each stream
  carries its own bank byte, and the flag blocks sit in the spare ends of banks 6, 5, 3, 3, 5, 6.
- **Bobsled's tube view** (live: three frames rebuilt and equal to dumps): 31 frames in a
  mask-per-cell packing, b4:`$885D-$88CF`. A cell is one byte by 8 lines: a mask byte, then one
  literal per set bit; a clear bit draws the background byte `$AA`. 23,560 bytes in 8,788 (0.37);
  about 30,000 cycles a 760-byte redraw as written (hint). The near view uses the same packing as a
  patch (b4:`$88D0-$894B`, code).

### Not determined

- Biathlon's later scenes and shooting range, ski jump's flight drawing, skating's map: from logs
  only.
