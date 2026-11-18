## Impossible Mission (Epyx / Atari 1987, 128K SuperGame + 16K RAM)

Survey plus a focused read, not a full disassembly. Addresses are `bank:address` (`7:` is the
fixed bank at `$C000`). Tags: **live** (seen in MAME), **code** (read from the listing), **hint**.
Everything is in `impossiblemission/` (runs, tools, `disasm/`); see "Files and coverage" at the end.

### Summary

- The cart uses about 6.5K of its 16K RAM; `$4000-$5FFF` was never written in any run (live, 8 runs).
- Cart RAM holds three kinds of thing: (1) **a game generated from a seed at Reset** (the complex's
  9x6 room grid, 172 "what is hidden here" bytes, 9 puzzle pictures, 36 piece records, 94 robot
  behaviours) and the state that persists between rooms; (2) **the current room**: its DLL and
  display lists (1,856 bytes, a ROM template copied in and poked) and a 40x25 character map
  (1,000 bytes) that is drawn by MARIA and read by the CPU as the collision map; (3) **bitmap work
  buffers** for the punch-card puzzle pieces, which are computed, flipped and recoloured at run time.
- Console RAM is full: `$1800-$1FFF` is a **character set kept in RAM** (CHARBASE `$18` in every
  scene), `$2000-$21FF` palette shadows and variables, `$2200-$27A2` the corridor's lists.
- **Code does run from cart RAM**: two 4-byte thunks at `$7270`/`$7274` (live). Lists and the DLL
  are in cart RAM while a room is shown (live). Interrupts call banked code (code).
- Banks: 0 and 1 are empty, **2 was never selected in any run**, 3 = title, 4 = corridor, pocket
  computer and the game generator, 5 = rooms, 6 = data (font, the room list template) and one
  more scene not reached. No sampled speech was found.

### Cart RAM map

Writers are `bank:PC` from the write taps (`runs/p2`, `runs/z3`); all **live** unless tagged.

| Range | Size | Use | Written by | Read by |
|---|---|---|---|---|
| `$4000-$5FFF` | 8,192 | never written (one dummy read at `$5F00-$5FEF` from `STA $5FFF,X`) | - | - |
| `$6000-$60AB` (cleared to `$60EF`) | 172 | search table: one byte per searchable object in the complex. `$FF` nothing, `$FC` snooze, `$FD` lift reset, `1-35` a puzzle piece, `$FE` searched and gone (poke-checked: `runs/k1`) | 4:`AE4E` clear, 4:`AE5B/AE63` and 4:`AA3D` place by rejection sampling | CPU (5:`9C82` at room build) |
| `$60F0-$65FF` | 1,296 | 9 puzzle pictures, 144 bytes each (48x24 pixels, 1 bit, column-major) | 4:`A9A9` (random tiles), 4:`A9D5-AA10` (border) | CPU |
| `$6600-$668F` | 144 | 36 piece records x 4: puzzle, mask A, mask B, flips and index | 4:`AA86-AAE7` | CPU |
| `$6740-$6763`, `$6770-$6793` | 36+36 | inventory: piece ids (`$FF` = none) and each piece's colour | 7:`C847`, pick-up code | CPU |
| `$67A0-$67A8` | 9 | the game's password (one of 8 nine-letter words at 7:`FD30`) | 4:`AA2D` | CPU |
| `$6812-$6DA1` | 6 x 144 | six piece buffers, one a page at offset `$12` (two list windows, work area); `$68A3-$68A8` their colours | 7:`C8A4-C8B3` clear, 4:`A8F3/A91F/A2C4`, flips through `$7274` | CPU only |
| `$6E12`, `$6E13-$6EA2` | 1+144 | piece count; the 144-byte scratch a piece is cut into | 4:`AB89` | CPU |
| `$6EA3-$6ECC` | 42 | player and game variables: `$6EAE` frame counter, `$6EBD-$6EC0` clock (BCD), `$6EC3/4` lift column and height, `$6ECB` side entered, `$6ECC` in-room flag | 7:`C9C9-CA39`, 7:`CD38-CD64`, many | CPU |
| `$6F12-$6F6F` | 94 | one behaviour byte per robot in the complex, drawn at Reset | 5:`8837` | CPU |
| `$6F70-$6FA8` | 57 | the room's four robots (state, x, y, frame), `$6FA1` frame handshake | 5:`88xx-8Bxx`, 5:`9B27-9B8F` | CPU |
| `$6FA9-$6FF4`, `$7012-$7037` | 114 | pocket computer map: 6 rows x 19 characters (`$F5` blank, `$F6` room visited, `$F8+` shaft pieces) | 7:`D952-D961` fill, 7:`DB5A`, 7:`DB7E` | **MARIA** (indirect) |
| `$7038-$706D` | 54 | the complex: room number at each of 9 columns x 6 rows (`$FF` none) | 7:`D945`, 7:`DABA` | CPU |
| `$706E-$70A3` | 54 | corridor and door bits for each grid cell | 7:`D948`, 7:`DACC/DADD`, 7:`DA5D` | CPU |
| `$70A4-$70C3` | 32 | room numbers 0-31 shuffled in four classes of 8 | 7:`D93B-D9B6` | CPU |
| `$70C6-$70CE` | 9 | pocket computer colours the DLI loads; `$70CE` its background | 7:`EF56`, 4:`8DD7`, 7:`CDE4` | CPU (DLI) |
| `$70CF-$70E7` | 25 | per-row flags of the room map | 5:`99E0` | CPU |
| `$7112-$713D` | 44 | two 22-character status lines ("Snoozes:0 Lift Inits:0", "Psw:... 12:00:01"), rebuilt every frame | 4:`8F57`, 4:`8F66`, 4:`901A` | **MARIA** (indirect) |
| `$713E-$719A` | 93 | every room's lift positions (persist between visits) | 5:`BF2C` at Reset, 5:`9925` on leaving | CPU |
| `$719B-$71D3` | 57 | the current room's lifts | 5:`9BDB-9C39` | CPU |
| `$7212-$7239`, `$723A-$7261` | 40+40 | palette now and palette wanted (the fade at 7:`EEB0-EF88`) | 7:`EED8`, 7:`EF27`, 7:`EF6A-EF88` | CPU |
| `$7270-$7277` | 8 | **code**: `LDA abs,X / RTS` and `STA abs,X / RTS`, operands patched | 4:`AD96`, 4:`AC72-AC7D` | CPU **executes** |
| `$728A-$72B1` | up to 40 | the room's furniture: (search slot, search time) pairs | 5:`9C9D`, 5:`9CB7` | CPU |
| `$7400-$7B3F` | 1,856 | room DLL (`$7400`, 33 zones) and its lists, 68 bytes a zone | 7:`EE93` copies 6:`8800-8F3F`; pokes 7:`FAxx-FDxx`, 5:`88xx-8Axx`, 5:`9D5D-9E3F` | **MARIA** (DLL and lists) and CPU (read-modify-write) |
| `$7812-$7911` | 256 | at Reset only: a 16x16 "mask pair used" matrix (inside the future list area) | 4:`AA47`, 4:`AB1B/AB21` | CPU |
| `$7C00-$7FE7` | 1,000 | room character map 40x25, also the collision map | 5:`9A2F-9A38` clear, 5:`9A4C/9A50/9AAA/9ADC/9E62`, 5:`9CE3` | **MARIA** (indirect) and CPU (7:`FC2E`, 7:`EAB9`) |

MARIA's reads of cart RAM: pages `$6F-$71` in the corridor (608+304+16 bytes a frame), pages
`$74-$7F` in a room (about 19,000 reads a frame, most of them list headers) (live, `mariar.txt`).

Console RAM: `$1800-$1FFF` RAM character set and sprite canvas (below); `$2000-$201F` palette
shadow in register order; `$2021-$203B`, `$2100-$2110` variables (`$2101/2` the interrupt vector,
`$2109-$210E` the block copier's arguments); `$2200-$27A2` title or corridor DLL and lists.

### The game is generated at Reset

Run once from 7:`C800` (live: frames 311-322 of `runs/p2`; formats from code, dumps checked).

- **Random numbers**: 7:`DB98`, a 40-bit state in `$80-$84` multiplied by `$20003` each call (two
  5-byte adds), low byte forced to `xx1xxxxx`; returns the top byte. Seeded at 7:`EE5C-EE62` from
  the frame counter `$6EAE` through 7:`DBCB/DBD9` and 7:`DB8D` (code). The title never touches
  `$6EAE`, which MAME starts at 0, so **the first game after power-on is always the same complex
  and password** (ALLIGATOR; live, runs `s1`, `p1`, `p2`, `p3` with different start frames). A
  later Reset seeds from the counter the last game left (code).
- **Search table**: `$6000-$60EF` = `$FF`; then 8 x `$FC` and 8 x `$FD`, then piece ids 35 down to
  1, each dropped into a random free slot below `$AC` (4:`AE4A`, 4:`AA37`, picker 4:`AE6A`). Piece 0
  is not placed by this loop (code; where it comes from was not determined).
- **Puzzle pictures**: 4:`A98D` fills `$60F0-$65FF` with 162 random 8-byte cells taken from 16
  patterns at 4:`9390` (128 bytes: a solid 8x8 tile with one 2-pixel hole in different places),
  then 4:`A9D1` draws a border on each of the 9 pictures (live: dump printed from `runs/p2`).
- **Pieces**: 4:`AA44`. A shuffled list of 16 mask numbers at `$7212`; puzzle p gets mask A =
  list[p]; its pieces 0-1 get a random mask B and pieces 2-3 another, both different from A and
  not used with A before (matrix at `$7812`, 4:`AAF3`). Record: `[puzzle, A, B, flips<<2 | index]`
  with two random flip bits.
- **Password**: 9 letters copied from one of 8 words at 7:`FD30` (SWORDFISH, ASPARAGUS, ARTICHOKE,
  CROCODILE, ALLIGATOR, ALBATROSS, BUTTERFLY, CORMORANT).
- **The complex**: 7:`D938-DA7F`. Room numbers 0-31 in four classes of 8 (by which side and
  height their doors are: 7:`DAE1`, 7:`DAF9`), each class shuffled by 16 swaps; rooms are then
  dealt into a 9x6 grid by 7:`DA8A` (it walks down a column from a random row to the first free
  cell and moves to the next column when full) and the door bits are added into `$706E`. 108 bytes
  describe the building (live: grid dumped from `runs/p2`).
- **Robots**: 5:`8816` gives each of the 94 robots one of 32 behaviour bytes from 5:`8B98` (8
  listed robots draw from a second 16). **Lifts**: 5:`BF18` copies the start positions.
- A dead branch at 7:`C85A` (`LDA #$FF / NOP / AND #$08`, once a console switch test) fills the
  inventory with all 36 pieces. Doing the same by pokes works: `tools/runpz.py` (live, `runs/z3`).

### Rooms

A room is a **compact record expanded into a character map and patched lists** (code 5:`99CF-9E75`,
checked against live dumps of rooms 30 and 3 with `tools/rooms.py`).

- All 32 records are in bank 5, pointer table 5:`A18F`, records 5:`A1CF-AFDD`: **3,599 bytes, 80 to
  185 a room, 112 on average**. The builder and the robots' and furniture's graphics are in bank 5
  too; the list template and the tile glyphs come from bank 6. Rooms are not banked one by one.
- Record, in order:
  1. 4 colour bytes: BACKGRND shadow `$2000`, palette 4 shadow `$2011-$2013`.
  2. floors `[row, column, length-1]` to `$FF`: character `$80` stored along the row.
  3. doors `[row, column]` to `$FF`: five cells cleared down the wall.
  4. 6 entry bytes: the player's x, y and facing for an entry from the left or the right.
  5. robots `[index, row, column]` to `$FF` (up to 4); the index picks the behaviour in `$6F12`.
  6. one optional `[kind, x, y]` (the ball), or `$FF`.
  7. lifts `[row, column, a, b, stops... $FF]` to `$FF`; positions come from `$713E`.
  8. furniture `[row, column, type, search slot]` to `$FF`.
- What it becomes (live: `runs/p2` frames 573-580):
  - the screen fades out (16 steps, 7:`EEB0`), DMA goes off (CTRL `$60`, 7:`FF63`);
  - 7:`DF03` copies the **list template 6:`8800-8F3F` to `$7400-$7B3F`** with the block copier
    7:`EE7B` (about 800 bytes a frame); 7:`DF2F` copies 128 glyphs into the RAM character set;
  - the map `$7C00-$7FFF` is cleared, wall characters `$82` go down both edges, then floors,
    doors, lifts (`$84`) and furniture footprints (`$87 + n`) are written; every odd column gets
    `code | 1`, so a tile is two 4-pixel characters (5:`9CDA`);
  - **furniture is prepended to a zone's list**: 5:`9DF7` subtracts 4 from the list pointer in
    the zone's DLL entry and writes a 4-byte header there, one for each 8-line slice of the
    object. The template leaves 18 spare bytes in front of each list. Type table 5:`B800`, 5 bytes
    a type: graphics low, high, zone rows, palette and width, search time; slices sit side by
    side in the sheet, so the next slice is `pointer + width` (live: the zone at line 45 of
    `dll_f00620.txt` starts 4 bytes early);
  - **each map row is trimmed** (5:`9CF5-9D8F`): the row is drawn by two indirect objects, and
    their widths are set so the left one ends at the right-most floor of the left 27 columns and
    the right one starts at the left-most floor of the last 13. A row without floors draws one
    wall character at each edge (width 1 and 1); a full row draws 27 + 13. The room's colour is
    BACKGRND, set by the top DLI, so empty cells cost no DMA;
  - DPP is pointed at `$7400` (5:`9813`), DMA comes back and the palette fades in. Display off
    for 7 frames.
- In play every zone list has fixed slots, parked at x 192 when unused (live lists): 2 map
  objects, a 3-byte object in palette 4 and a 6-byte one in palette 5 (not identified; the ball
  and a lift car, hint), 2 robot slots (160B, 4 bytes wide), 4 slots for the player's slices.
  The pokers read the headers back (`AND #$1F / ORA`), so the lists are read-write for the CPU.
- The CPU reads the character map for footing and searching (7:`FC2E`, 7:`EAB9`): the character
  under the player names the furniture (`$87 + n`), floor (`$80`) or lift (`$84`).
- Room state that persists: the search table byte of each object and the lifts' positions.
  Robots restart on entry.
- Robots and the lifts' logic run inside the bottom DLI (7:`CE00` calls 5:`8862`, 5:`8847`,
  5:`A0AD`, 5:`8DB0`); the main loop runs the player (code).

### Pictures and tiles built in RAM

- **A character set in RAM** (`$1800-$1FFF`, 8 line pages, CHARBASE `$18` everywhere) (live):
  - title: 3:`B9C0` copies eight 132-byte line strips from 3:`B4D1-B8F0` and a few more strips;
    the panels are direct objects into those RAM pages (a dotted background strip used twice a
    zone, panel faces and edges, 131-142 objects) plus character text;
  - corridor: 7:`CEFC` copies the 96-glyph 320A font from 6:`8000-82FF` (768 bytes, stored
    compactly, 32 bytes a line) to characters `$20-$7F`; 7:`FE70` adds 12 map glyphs at `$F4`;
  - rooms: 7:`DF2F` copies 128 glyphs (blocks of 8 characters, 8 bytes a line) and 5:`B8CD` the
    8 floor, wall and lift glyphs at `$80-$87`.
  - Nothing is packed: the copies only spread compact ROM strips over the 8 pages, so the ROM
    needs no 256-byte page layout and the scene's bank can hold anything at those addresses.
- **A glyph animated in place**: 5:`9958` rotates the bits of characters `$84/$85`, lines 0-3
  (12 `ROL`s on `$1884-$1B85`), from the top DLI every frame: every lift on screen animates for
  about 80 cycles and no list change (live: writes on every room frame).
- **The same pages are a sprite canvas**: `$1894-$18FF` of each page holds six 6-byte x 3-zone
  puzzle pieces, drawn as direct objects (table 4:`A012`). Slot 5 overlaps the map glyphs; the
  two screens are never up together and each is recopied when shown (live).
- **The cavern rock** is not tiles: each 8-line zone has two direct objects 17 bytes wide (left
  and right of the shaft) pointing into two strips at 4:`B000` and 4:`B020` at a different byte
  offset in every zone (`B00B, B002, B02B, B022, B005...`), so about 800 bytes of rock cover the
  screen without a visible repeat (live, `dll_f01300.txt`). A lift ride scrolls it 8 lines every
  2 frames by copying each zone's two headers to the next zone (4:`901F`, 4:`905D`, tables
  4:`92FA`, 4:`932A`); zone heights never change (live, `runs/p3`).
- **The 24 write-mode-1 objects of the corridor** are the pocket computer's two icon panels
  (4:`B075`, 12 bytes wide, and 4:`8000`, 23 bytes wide, ten zones) drawn under CTRL `$43`, so
  they are 320C, not 160B. In rooms the write-mode-1 objects are the robots (160B) (live lists).

### The pocket computer

- **Mode split** (live in `regs.txt`, code 7:`CBB9-CC1A`, 7:`CD96-CDE7`). Three DLIs a frame,
  chained through a RAM vector (`JMP ($2101)` at 7:`EE33`):
  - about line 39 (zone 4; the line is worked out from the DLL), 7:`CB8A`: reset check; in a room BACKGRND = room colour after 2 WSYNCs;
  - line 159 (first panel zone), 7:`CBB9`: 2 WSYNCs, BACKGRND = `$70CE`, **CTRL = `$43`**
    (320A/C, one-byte characters), then `P7C2..P2C2` from `$70CD..$70C8` and `P1C2` = frame/2 & 7
    (the hand flashes); then the TIA sound and the BCD clock;
  - line 239 (bottom), 7:`CD96`: WSYNC, BACKGRND = 0, `P1C2..P7C2` restored from the shadow,
    **CTRL = `$40`**.
  - In 320A only C2 of an object's palette shows, so the DLI changes one colour a palette: text
    lines, map, hand and each piece are 320A objects in their own palette, and the 320C panels
    pick P4-P7's C2 per pixel pair from their data (colour mapping by EricBall's chart, hint).
- **The map**: 114 character cells in cart RAM, 6 rows of 19 (`$6FA9, $6FBC, $6FCF, $6FE2, $7012,
  $7025`: the rows skip the page boundary). Entering a room stores `$F6` in its cell (7:`DB5D`);
  the lift stores the corridor piece `$F8 + door bits` as it passes a floor (7:`DB2B`) (live).
- **Puzzle pieces** (code 4:`AB2A-AD56`; live: `runs/z3`, a piece selected, flipped, recoloured):
  - a piece is never stored. 4:`AB6F` cuts it when shown: `piece = picture AND (maskA EOR i1) AND
    (maskB EOR i0)` over 144 bytes into `$6E13`, where i0, i1 are the piece's index bits spread to
    `$00/$FF`. Two masks and their complements split a picture into four exact pieces. The 16
    masks are at 4:`9410-9D0F` (144 bytes each, 2,304 in all);
  - the border is redrawn (4:`A9D1`), then the record's flip bits are applied;
  - **vertical flip** 4:`AC99`: swaps rows, 60 byte swaps (2 frames, live at frames 880-881);
    **horizontal flip** 4:`AD0A`: swaps columns and reverses each byte through the 256-byte
    table 4:`9D10`;
  - both swap two offsets of one buffer, so they call the **RAM thunks** `$7270` (`LDA abs,X`)
    and `$7274` (`STA abs,X`), copied from 4:`A04A` and patched with the buffer's address
    (4:`AC72`). PCs `$7270-$7277` ran 984 times in `runs/z3` (live);
  - the bitmap is column-major (cell = 8 consecutive bytes = one byte column of one zone), so
    4:`ABEE` copies it to the canvas with one page step a byte;
  - **recolour** costs no pixels: 4:`AC26` rewrites the palette bits of the piece's three
    headers (`colour + 4`, table 7:`EFD1`).
- ROM for the puzzle: 128 (tiles) + 2,304 (masks) + 256 (bit reverse) = 2,688 bytes, against
  5,184 for 36 stored pieces, and the pictures differ every game.

### Frame structure

- The NMI vector is `JMP ($2101)`; each DLI stores the next handler's address. The three handlers
  above do the display work, sound (7:`CC1A-CD36`), the clock (7:`CD38-CD94`), and in a room the
  robots and lifts (bottom DLI). DLI 1 and 3 call bank 5 code, so a room never switches banks.
- Main loop 7:`E800`: waits until the frame counter `$6EAE` (DLI 2) differs from `$6FA1`, copies
  it and runs one step; `$6EB0`, counted by the bottom DLI, is compared with 3 at 7:`E82B`
  (a frame-debt test, hint).
- Bank switches go through 7:`DEFF` (`STA $BFFF / RTS`), with no shadow of the bank number.
- Blocks are moved by one copier, 7:`EE7B` (source `$210D/E`, destination `$2109/A`, end
  `$210B/C`); DMA is turned off around scene builds (7:`FF63` CTRL `$60`, 7:`FF6B` CTRL `$40`).
- **Speech**: none found. A raw scan of all banks finds about 40 byte pairs that could be a
  store to AUDV0/AUDV1; the ones read (7:`CC1A-CD36`, 3:`83F2-8400`, 4:`A570-A57D`, 7:`EB5E`,
  7:`F82F`) set a tone and a volume, and none sits in a loop that fetches a sample. The rest
  were not read one by one (code).

### Why RAM, with 32K of ROM empty

- What the game needs is writable, not large: a generated game (about 2.1K), the room's lists and
  map (2.9K), the piece buffers (1.2K). Console RAM is already full with the RAM character set
  (2K), the corridor's lists (1.4K) and variables.
- The RAM replaced ROM in one place: 36 pieces as 9 pictures and masks.
- The ROM is 128K because that is the SuperGame board; the game fills 5 banks at most (hint).

### Dead ends and corrections

- "No code runs from cart RAM" (the first survey) is true only outside the puzzle screen.
- Piece record bytes 1 and 2 are mask numbers, not colours as first read; the colour is kept in
  the inventory (`$6770`) and the buffers' colour bytes (`$68A3`).
- `$6800-$6DA1` are CPU bitmaps, not MARIA's: she draws the pieces from console RAM.
- The reads of all of `$4000-$7FFF` logged at PCs 7:`FF5E/FF60/E80D` on snapshot frames are the
  dump itself, not the game.
- `tools/run.py` needs an absolute path for a Lua script outside `tools/`.

### Not determined

- What bank 2 holds (graphics by its look) and when it is selected; the scene at 6:`B2EE` (own
  list template 6:`B000`); the two rooms with 30 "furniture" records (17 and 27).
- How piece 0 is obtained; the title-to-game path in bank 3; robots' behaviour bytes.
- DMA and cycle costs were not measured; the figures in the techniques file are estimates.
- Whether `$4000-$5FFF` is used by the scenes not reached.

### Files and coverage

- `impossiblemission/runs/`: `s1` (first survey), `p2` (set-up, two rooms: the main run), `p3`
  (lift ride), `z3` (puzzle screen with all pieces: select, flip, recolour), `k1` (search-table
  poke); `p1`, `z1`, `z2` are earlier attempts.
- `impossiblemission/tools/`: `survey2.lua` (bank-tagged PCs, console RAM write tap), `ramuse.py`
  (RAM use by PC and range), `rooms.py` (room record decoder), `runpz.py` (all pieces by pokes),
  `mkannot.py` (trace entries from the logs, runs the toolkit's `disasm.py`), `lst.py` (compact
  view of a listing).
- `impossiblemission/disasm/`: traced listings from live PCs only, no labels or comments. Reached
  as code: bank 3 6%, bank 4 32%, bank 5 29%, bank 7 38%; banks 2 and 6 not traced.
  `rooms.txt` is the decoded room list.
