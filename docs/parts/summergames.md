## Summer Games (Epyx / Atari 1987, 128K SuperGame + 16K RAM)

Evidence tags: **live** (seen in MAME: write logs, list dumps, memory dumps compared with a decode),
**code** (read from the listing only), **hint** (a guess). Addresses are `bank:address`; `f7` is the
fixed bank. Runs are in `summergames/runs/`, tools in `summergames/tools/`, listings in
`summergames/disasm/` (traced from each bank's `$8000`/`$8003`: 22-33% of each code bank reached).

**In one line:** the 7800 version is the Commodore 64 game's data kept in C64 shapes (63-byte
sprites, 8-byte characters, 40-column character screens, run-length pictures) and converted at each
scene's load into MARIA's line-per-page layout in cart RAM. Cart RAM is scene workspace: nothing in
it survives an event.

### Coverage

- Live: boot, opening picture, main menu, name entry, the country (flags) screen, and all six
  events through "Practice one event" (diving, 4x400m relay, 100m dash, gymnastics, freestyle relay,
  100m freestyle). The track and swim runs false-start (the script wiggles the stick before the gun),
  so the race itself was seen only for a few strokes; diving and the vault ran whole, with score
  screens. Not seen: opening ceremonies beyond the first picture, medal and world-record screens,
  a full competition.
- Code read: the shell (`f7:$D0F8-$D9F6`), its services (`f7:$FC20-$FEDA`), the title loader
  (`b3:$8006-$81F0`), the diving loader (`b3:$A800-$A92E`), the track loader and sprite engine
  (`b1:$9CB9-$9E96`, `$8007-$807D`, NMI `$9173`), the gymnastics sprite path (`b0:$8A94-$8D61`), the
  diving sprite drawer (`b4:$8835-$88FC`). Swimming is described from logs and list dumps only.

### Banks and how an event is loaded

| Bank | Holds | Entry / NMI at `$8000` / `$8003` |
|---|---|---|
| 0 | gymnastics (vault): code, background strips, mirror table | `JMP $8007` / `JMP $9005` |
| 1 | 4x400m relay and 100m dash: code, 44 runner sprites, character screen and its font | `JMP $8007` / `JMP $9173` |
| 2 | data only: the gymnast's frames (8K), copied whole into cart RAM | none (never in with DMA on) |
| 3 | opening picture; at `$A800` the diving loader and diving's text-screen lists | `JMP $8006` / `JMP $80EC` |
| 4 | platform diving | `JMP $8007` / `JMP $8C73` |
| 5 | freestyle relay and 100m freestyle | `JMP $8006` / `JMP $83C8` |
| 6 | data only: packed font, six packed flag blocks, packed swim picture and font, the shell's list block at `$BC00` | none |
| 7 | fixed: shell, text services, unpacker, TIA sound driver | `$C000: JMP $D0F8`, `$C003: JMP $D000` |

- **The NMI vector is `$8003`, inside the switched window** (code, live). Every code bank starts
  with `JMP entry` / `JMP nmi`. The fixed bank starts the same way at `$C000`/`$C003`, and the shell
  runs with **bank 7 switched into the window as well** (a second copy of the fixed bank at
  `$8000`), so its own NMI (`$D000`) is reached through `$8003` (live: bank register 7 in every menu
  frame). Each event therefore owns its whole interrupt handler with no dispatch in the fixed bank.
- The two data banks (2 and 6) have no entry at `$8003`. The rule that makes this safe: **every
  visit to them is made with DMA off.** `f7:$DCD4` waits for vblank and writes CTRL = `$60`, and is
  called before the unpacker or a copy switches to bank 6 or 2 (live: `3C=60@258` in the frame
  before each unpack, bank 6 in for frames 296-324 of run `n1`). The screen is blank for the 5 to 29
  frames a load takes.
- One bank-switch routine, `f7:$FDDA` (`STA $BFFF; RTS`), 12 callers, all in the fixed bank (code:
  byte search for `20 DA FD`). No shadow of the bank number is kept; callers pass the bank to
  restore in X (`f7:$FE63`) or hard-code it (`f7:$FD48`: bank 3, `JSR $A8FE`, bank 4).
- **Entering an event** (`f7:$D972`, code; live in runs `e0`-`e5`): the event number indexes
  `f7:$D871` (`03 01 01 00 05 05`), the font is unpacked to `$1800`, DMA is turned off, the bank is
  switched and the shell jumps to `$8000` (bank 3: to `$A800`, the diving loader, which ends in
  `f7:$FDD2`: bank 4, `JMP $8000`). Two events share a bank where they share art: bank 1 tests
  `$2702` at `$800A` to pick relay or dash.
- **An event is a program, not a subroutine.** It resets the stack (`b1:$8024`), clears zero page
  `$40-$FF` (`b1:$8080`) and cart RAM `$4000-$5FFF`, and leaves by `JMP $C000` after turning DMA off
  (`b1:$9166`). The shell's entry (`f7:$D0F8`) resets the stack again and decides what to do next
  from console RAM (`$2702` = next event, `$AA` = fresh start, `$BB` = aborted).
- **What survives between events is all in console RAM `$2600-$27FF`** (code): eight player records
  of `$20` bytes at `$2600` (name first; `$7F` marks an unused record, `f7:$FF05`), `$2700` number
  of joysticks, `$2702` event counter, `$2703-$2708` the events chosen, `$2713-$2715` menu cursors,
  `$2718` tune request. Cart RAM holds nothing lasting: each loader clears `$4000-$5FFF`.
- **The fixed bank's interface** (code): a jump table at `$C000` (`$C000` shell, `$C003` shell NMI,
  `$C006`/`$C009` start a tune, `$C00C` wait for the tune, `$C00F` sound tick, `$C012`), thunks at
  `$FED1/$FED4/$FED7`, and `f7:$FD73`, which every event's NMI calls once a frame: sound tick, then
  if Reset or Select is down set `$2702 = $BB` and jump to the shell **from inside the NMI** (the
  shell resets the stack, so the interrupt never returns).

### Cart RAM map

Shell (bank 7 in the window):

| Range | Size | Use | Writer | Reader |
|---|---|---|---|---|
| `$4000-$43BF` | 960 | text screen, 24 rows of 40 one-byte characters | `f7:$FC30` clear, `$FC5D` put character, `$FC99` print script (live) | MARIA (indirect, 320 mode, font in console RAM `$1800`) |
| `$5805-$580F` | 11 | the player's name for the flags screen | `f7:$D2A9` (live) | MARIA (character map) |
| `$58E6`, `$5964`, `$5990-$5995` | 8 | NMI phase, screen mode, cursor blink, text cursor column and row | `f7:$D000-$D085`, `$FC5D` (live) | CPU |
| `$4000-$57DF`, `$6000-$77DF` | 12,192 | flags screen: nine flags as a two-layer 160A bitmap, three 2K blocks a layer | unpacker `f7:$FE91`, six streams from bank 6 (live) | MARIA |

Opening picture (bank 3): lists in **cart RAM**.

| Range | Size | Use | Writer | Reader |
|---|---|---|---|---|
| `$6000-$65FF` | 1,536 | the display lists (292 objects), copied from `b3:$8777`; the runner's and flame's entries are rewritten in place each frame | `b3:$8016-$8034`, `$827F-$82BF` (live) | MARIA, CPU |
| `$6800-$6FC5` | 8 pages x 198 | background cells of 8 lines, stored cell after cell in ROM (`b3:$8CE5`, widths `$8CC0`) and spread a line a page | `b3:$80EF` (live) | MARIA |
| `$4500-$59BF` | 21 pages x 192 | 64 sprites of 3 x 21 bytes from `b3:$9315`, a line a page | `b3:$814D` (live) | MARIA |

Events (lists and DLL always in console RAM `$1800-$1DFF`, `$1E00`):

| Event | Cart RAM | Writer | Reader |
|---|---|---|---|
| Track (b1) | `$4000-$47FF` font for the character screen (96 characters x 8 bytes from `b1:$A392`, transposed); `$4800-$58FF` + `$5400-$5FFF` 44 runner sprites from `b1:$AA80` (two copies, see below); `$6000-$65FF` the 40-column character screen, a raw copy of `b1:$95DD`, with the clock's big digits and the lane marks written into it each frame; `$6C00-$6CFF` a table copied from `b1:$8A88` | `$9E7C`, `$9CCF`/`$9D26`, `$912C`, `$88EC`/`$8997`, `$9CA1` (live) | MARIA; CPU reads `$6C00` |
| Gymnastics (b0) | `$4400-$58FF` the gymnast, redrawn from a zero-page buffer every frame; `$5080-$57FF` font; `$5830-$5FFF` cell strips from `b0:$9808`; **`$6000-$7FFF` bank 2's first 8K copied whole** | `$8CCA`/`$8D1E`, `$8EFF`, `$8FBD`, `f7:$FD8D` (live) | MARIA; **CPU reads `$6000-$7FFF` as sprite data** (`b0:$8B70`, 62,332 reads in run `e3`) |
| Diving (b3 loader, b4) | `$4300-$58FF` the diver, redrawn each frame and shifted through the pages; `$5080-$57FF` font copied from console RAM `$1800`; `$5830-$5FD7` cell strips from `b3:$B2CA`; `$7800-$78FF` a bit-reversal table made by code | `b4:$8835`, `$8540`, `b3:$A82F`, `$A8B6`, `b4:$88EA` (live) | MARIA; CPU reads back `$4000-$5929` and `$7800` |
| Swimming (b5) | `$4000-$57FF` swimmer sprites, transposed when a frame changes (`b5:$A805`, 218 bytes a time); `$5800-$5FFF` font, unpacked from `b6:$B190`; **`$6000-$7F1F` the pool picture, unpacked from `b6:$A600`** | `$94E5` clear, `$9549`, `$A805`, `f7:$FE91` (live) | MARIA |

**Which screens put lists in cart RAM, and why** (live for where, hint for why): only the opening
picture. There the font sits in console RAM `$1800-$1FFF`, the shell's list block sits at
`$2200-$25FF` and the picture needs 1.5K of lists. Events move the font out to cart RAM (CHARBASE
`$40`, `$50` or `$58`) and so free `$1800-$1DFF` for lists and `$1E00` for the DLL.

No code runs from cart RAM (live: no PC sampled there in any run).

### Unpacking

**One run-length scheme, in the fixed bank** (`f7:$FE63-$FE9B` plus pointer helpers
`$FE9C-$FEC2`, about 70 bytes; code, and live: `tools/verify.py` decodes five streams; three equal
the dumps byte for byte, the swim font but for 4 bytes and the first flag block but for 10, which
lie in the 16 bytes the next block overlaps). A non-zero byte is a literal. `00 v n` writes `n` copies of `v`.
`00 v 00` ends. Call with source in `$40/$41`, destination in `$42/$43`, A = source bank, X = bank
to restore. Weakness: a lone zero costs three bytes.

| Stream (bank 6) | Packed | Unpacked | Ratio | To |
|---|---|---|---|---|
| font `$8000` | 773 | 2,048 | 0.38 | console RAM `$1800` |
| six flag blocks `$830C-$A5C8` | 8,863 | 12,288 | 0.72 | `$4000`, `$47F0`, `$4FE0`, `$6000`, `$67F0`, `$6FE0` |
| swim picture `$A600` | 2,950 | 7,968 | 0.37 | `$6000` |
| swim font `$B190` | 711 | 2,048 | 0.35 | `$5800` |

- **Speed** (live): 410-450 bytes a frame with DMA off, about 69 cycles a byte: every byte goes
  through three subroutine calls. The flags take 29 frames (run `n1`, frames 296-324), the swim
  picture and font 19 (run `e4`, 373-392).
- The table-driven caller `f7:$D2B9` (sources `$D202`, destinations `$D20E`, banks `$D21A`) gives
  each stream its own bank byte (code).
- The pictures are stored already in MARIA's layout: a 40-byte-wide 160A bitmap in 2K blocks of 8
  line pages x 240 bytes (six zone rows of 40 bytes), blocks `$7F0` apart so the low byte keeps
  counting on. Runs are therefore horizontal runs within a scan line.

**Not packed, only re-shaped** (code, live writers):
- Sprites sit in ROM as C64 sprite blocks (3 bytes x 21 rows, 63 or 64 bytes a frame) and are
  spread into a line a page: `b3:$814D` (64 sprites, 4,032 bytes, 5 frames), `b1:$9CCF` (44 sprites).
- Fonts sit as 8 bytes a character and are spread over 8 line pages (`b1:$9E7C`, 768 bytes).
- Cell strips of any width sit cell after cell with a width table (`b3:$80EF`, `b3:$A8B6`,
  `b0:$8FBD`: the same 70-byte routine three times).
- The track's character screen (`b1:$95DD`, 1,536 bytes) and the list templates are raw copies.

### Pictures and sprites composed in RAM

- **The gymnast: one stored pose, four orientations** (`b0:$8B41-$8D61`; code, live: both
  transposers ran in run `e3`, `$8CFD` in 582 frames and `$8D51` in 112). A frame is stored as a
  count of leading zero bytes followed by the rest of its 63 bytes (`$8B5E`). It is expanded into
  zero page `$80-$BE`. If bit 7 of `$C4` is set the buffer is mirrored left to right: bytes 0 and 2
  of each row swapped through a 256-byte bit-reversal table (`b0:$8A94`, table `b0:$9108`). Then it
  is written a row a page into `$44xx-$58xx`, counting the pages **up** (`$8CCA`) or **down**
  (`$8D1E`, when bit 6 is set): the upside-down gymnast costs no data and no extra time.
- **Plain bit reversal mirrors a 160A sprite here because the sprite palettes hold one colour three
  times** (live: P6 = `37 37 37`, P7 = `0F 0F 0F` in the diving dump): either bit of a pixel pair
  lights it, so swapping the bits in a pair changes nothing. More colours come from laying
  one-colour sprites over each other, as the C64 version did.
- **The diver** (`b4:$8835`; code, live): the same drawing, with the mirror table **generated at
  load** into cart RAM `$7800` by 18 bytes of code (`b4:$88EA`; live: the dump holds the bit
  reversal of 0-255). The drawer then copies the sprite's top rows to a second place 48 columns on
  (`$88D3`), reading cart RAM back.
- **The straddle copy** (code, track `b1:$9D26`, lists live): a sprite crosses up to four 8-line
  zones, and holey DMA does not blank RAM. So each sprite is stored twice: rows 0-16 in pages
  `$58-$48`, and rows 9-20 again in pages `$5F-$54` at column +`$84`. The zone that holds the
  sprite's foot points at the second copy (`b1:$9E25`: add `$10` to the page, `$84` to the column),
  whose neighbours are blank pages.
- **Eight C64 sprites as eight fixed list slots a zone** (`b1:$9DA0-$9E7B`; code, lists live).
  Showing a sprite writes three bytes (low, high, x) into its slot in each zone it crosses. Hiding it
  writes high byte `$90` (`b1:$9D7E`): every zone has holey DMA on, so `$9000` reads as zeros.
- The clock is big digits written as characters into three rows of the character screen
  (`b1:$88EC`, `$624F/$6277/$629F`; live). The flags are not drawn per country: all nine are one
  two-layer picture and a cursor.

### Text

`f7:$FC99` prints a script into the 40x24 map (code; live for the writes): `00` end, `02 x y` set
the cursor, `05 lo hi` continue at another address, `06 lo hi` print the byte at an address as a
decimal number, `0D` new line, anything else a character (lower case folded to upper). The jump lets
three prompts ("Practice which event?", "Compete in which event?", "Select the events...") share
one 137-byte event list at `f7:$D761`. `f7:$D877` is the menu: a table of row addresses, the
selection arrow printed as characters, a move accepted after the stick is held 5 of 8 frames.

### Frame structure

- **Shell** (code, live): the main program waits on MSTAT (`f7:$FDDE`) and is 60 Hz. Its NMI
  (`$D000`) is two DLIs told apart by a flag in cart RAM (`$5991`): the first sets CHARBASE, CTRL
  `$43` and the blinking cursor colour; the second calls the sound tick and reads the stick into
  `$88`. Screen mode `$5964` = 1 (flags) makes them set CTRL `$40` for the picture and `$43` for the
  text line.
- **Track** (code, live `regs.txt`): the NMI (`b1:$9173`) counts its DLIs in `$83`. Stage 0 (line
  16): palettes, CTRL `$40`, `f7:$FD73` (sound, Reset/Select). Stage 1 (line 140): palettes, and
  `SEC; ROR $4A` sets the frame flag. Stage 3 (line 222): CTRL `$43` for the 320-mode text line.
  The main loop (`b1:$803B`) waits for bit 7 of `$4A` and clears it with `LSR`: one tick a frame,
  started from the middle of the screen, with a slower task every fifth tick (`$4C`). Palettes are
  reloaded at each DLI, so each band of the screen has its own colours.

### Sound

TIA only. Every store to AUDV0/AUDV1 is in the fixed bank's driver (`f7:$F840-$F917`) or the
silence at `f7:$D99A` (code: byte search). No sampled sound.

### Dead ends and corrections

- The first survey read `f7:$FC44-$FC56` as a scroll: it is the clear of the text screen (seven
  overlapping 160-byte stores of `$20`).
- The font at `$1800` is not a plain copy: it is the run-length stream at `b6:$8000`.
- `f7:$FE63` was first taken for a bank-to-RAM copy with a page count in X: X is the bank to
  restore.
- CPU "reads" of all of `$4000-$7FFF` at PCs like `$FDE4`/`$80C4` in snapshot frames are the
  survey's own memory dump, not the game.

### Not determined

- What the swim lists' four one-byte objects at x = 168 pointing at `$E7F0...` are for (off screen;
  a hint: an unused second layer whose addresses are the picture's plus `$8000`).
- The diver's page shifting (`b4:$8540-$8588`) in detail, and how the splash is drawn.
- Swimming's and diving's NMIs, the opening ceremony after the first picture, medals and records.
- Whether anything reads `$C012` (`f7:$DE76`).
