## Tower Toppler (64K SuperGame + 16K RAM)

Survey of 2026-11-18. Tags: **live** (seen in MAME), **code** (read from the ROM), **hint** (a guess).
Addresses are `bank:address`; `f3` is the fixed bank at `$C000`, `b0`-`b2` the file banks the game
selects with the values 4, 5, 6. Runs and scripts are in `towertoppler/` (see `towertoppler/NOTES.md`).

In short: the play screen is **one-colour 320A throughout**. The tower is not tiles and not a
bitmap in the usual sense: it is a 24 x 18 character map shown through an **identity character set**
(character `c` draws the bit pattern `c`), so every map byte is eight pixels and the game "draws"
the rotating tower with byte masks into console RAM. Cart RAM holds the display lists (two sets),
an eight-line strip that sprites are copied into, the unpacked tower map and about 230 bytes of
variables: 6.2K of the 16K.

### Cart RAM map

| Range | Size | Use | Written by | Read by |
|---|---|---|---|---|
| `$4000-$5FFF` | 8,192 | never touched in any run (live for the scenes run) | - | - |
| `$6000-$647F` | 1,152 | display lists, set A: 18 zones x 64 bytes | f3:`E53E` (init), `E5DF`/`E637` (clear), `CA19`/`C9B1` (row headers), `DE98`/`D981` (sprite headers), `E71A` (last zone's pages), b2:`B448`-`B7xx` (intermission rows) | MARIA |
| `$6480-$64FF` | 128 | variables: enemy slots `$6498-$64BF`, the window's colour shadow `$64C0-$64C7`, sort keys, clip masks `$64D9-$64E4`, scores (BCD) `$64EC-$64FB`, flash mask `$64FF` | many | CPU; the DLI f3:`FF19` reads `$64C0-$64C7` |
| `$6500-$697F` | 1,152 | display lists, set B (same layout, five pages up) | as set A | MARIA |
| `$6980-$699F` | 32 | variables: intermission state `$6980-$698E`, flags `$698F-$6995`, six scroll positions `$6996-$699B`, collision bits `$699C` | f3, b2 | CPU |
| `$69A0-$69FF` | 96 | unused (zero in every dump) | - | - |
| `$6A00-$707F` | 1,664 | the tower's map, 16 bytes a row, row 0 at the bottom, up to 98 rows | f3:`C8CA` at a tower's load (bank value 4 in); f3:`D3FF` clears a cell when its enemy spawns | CPU: f3:`C690`, `C8A0` (drawing), `D5FF` (spawn scan), `E784`-`E854`, `F5xx` (collision) |
| `$7080-$70FF` | 128 | unused | - | - |
| `$7100-$78FF` | 2,048 | the sprite strip: 8 line pages x 256 byte columns; columns `$00-$7F` belong to list set A, `$80-$FF` to set B | f3:`C228` (clear), `DA08`+`D6D3`.. (player), `DECC`+`DC83`..`DE97` (enemies), `E149`/`E278`+`E1CF`.. and `E2A2`.. (other objects), `DB02` (door overlay) | MARIA only (the CPU never reads it back: every read PC there is a store's dummy read; live) |
| `$7900-$7FFF` | 1,792 | unused | - | - |

No code runs from cart RAM (live: no PC sampled there in 5 runs; code: nothing copies code).

**Why the lists are in cart RAM** (live for the occupancy, hint for the motive): console RAM is
full. `$1800-$1FFF` is the character set (2K, it must be RAM because it is generated and its eight
sea characters and the text font replace each other), `$2200-$22FF` the DLL (32 entries), the HUD's
lists and its digit rows, `$22F8-$2317` the high-score table, `$2318-$24C7` and `$24C8-$2677` the
two 24 x 18 character maps, `$2678-$2689` one fill pointer per zone. About 500 bytes are left
(`$2000-$203F`, `$2100-$213F`, `$268A-$27FF`); two list sets need 2,304.

**How the two sets are flipped** (code f3:`E68B`, live `runs/v1`, `runs/p1`): there is one DLL. The
flip swaps the two character-map pointers (`$5C/$5D` and `$5E/$5F`), toggles `$93` bit 7, and stores
the list page into the 18 window entries of the DLL (`$2219`, `$221C`, ... `$224C`: `$60,$60,$60,$60,
$61 x4, $62 x4, $63 x4, $64 x2` or the same from `$65`). Both sets keep the same low bytes
(`$00/$40/$80/$C0`), so only high bytes change: 18 `STY`, about 300 cycles with the scroll bytes.
It runs straight after the main loop's vblank wait, so it is done some 60 lines before the window's
first zone. The strip is double-buffered the same way: bit 7 of the column byte comes from `$93`.
The sets exist because one rebuild takes three frames (below).

### List and header formats (exact bytes)

Every header is 5 bytes: `lo, mode, hi, palette<<5 | (32-width)&31, x`. Mode is `$60` for indirect
(character) objects and `$40` for direct ones: write-mode bit 7 is clear everywhere, and bit 6 is
set in every header the game makes (live, all dumps; a data point for the display-recipes skill's
open question on bit 6: MAME draws them the same).

- Zone list, 64 bytes: `+0` the row's character object, `+5 .. +54` ten sprite slots, rest unused.
  `E53E` presets every slot's `hi` to `$71`; `E5DF` empties a set by storing 0 into byte 1 of each
  of the ten slots in each zone (180 stores: the "ten unrolled stores at `E5FE-E622`" of the first
  survey) and resets the fill pointers `$2678,X` to 5. A sprite then costs four stores (`DE98`:
  lo, `$40`, palette|width, x).
- Tower row: `lo, $60, hi, $08, $20` = palette 0, 24 characters, x 32 (template b2:`A4D8`).
- Sea row: `lo, $60, $C0, $20, $10` = palette 1, 32 characters (width field 0), x 16; the map is
  ROM, f3:`C000+32k`.
- Enemy cell: `col, $40, $71, $7D + slot*$20, x` = 3 bytes wide, palettes 3-6 by slot.
- Player: two headers per zone at x `$4A`: `$FD` (palette 7, 3 bytes) then `$5D` (palette 2).
- HUD rows (console RAM `$2286-$22CA`, copied from b2:`9D00`): five objects a row, e.g.
  `D25B $60 .. pal2 w6 x0`, `D261 pal2 w6 x128`, `22CD pal2 w9 x62`, `D267 pal0 w3 x36`,
  `D26A pal0 w3 x160`; CHARBASE `$80`.

### How the 320-mode screen gets its colours

- **One mode.** CTRL is `$43` everywhere except the intermission's window (`$40`). No header sets
  the write-mode bit, so everything is **320A**: one bit a pixel, lit pixels take the object's
  palette entry **C2**. The game only ever writes `BACKGRND` and `P0C2..P7C2` in play (code: the
  traced listing's equates hold no C1 or C3; live: `pal.txt` of every run). No 320B/C/D.
- **A colour is an object's palette.** Eight palettes = eight colours in a band, and a line shows
  as many colours as it has objects with different palette bits.
- **Two bands, each with its own eight.** The bottom DLI (f3:`FE8A`, the 3-line zone at line 240)
  loads the HUD's eight from ROM f3:`D27D` (`88 68 C8 28 38 48 08 00`). The DLI on the window's
  first zone (f3:`FF19`, line 63) loads the window's eight from the shadow `$64C0-$64C7` and sets
  CTRL from `$66`. Eight `LDA abs / STA zp` = 56 cycles each time. The shadow is filled from four
  sets at b2:`A5E8` (f3:`C36E`): play, text, all black, intermission. Loading the all-black set and
  waiting a frame is how the game hides the window while it builds a scene (f3:`FC80`, b2:`B307`).
- **Play window** (live, `runs/w1`, `runs/k1`): P0 the tower (per tower, b0:`AD28,X`), P1 the sea,
  P2 the player's colour plane, P3-P6 the four enemy slots (b2:`A608`, swapped with the slots),
  P7 black: the player's first plane, drawn before the green one so that it blots out the bricks
  behind him (poking `$64C7` = `$46` turns that plane red; poking `$64C1` recolours the sea).
  So a tower line has 2-4 colours, the screen at most 7 + 7 and black; tower 1 uses 5 in the
  window.
- **Bricks** are not coloured at all: one palette, and the texture is the bit pattern (every other
  pixel lit, the joints three dark pixels).
- **The sea's gradient is dither, not colour**: eight characters `$D7-$DE` of rising density
  (about 12% lit to 100%; b2:`A458`, 64 bytes) and one row of 32 of the same character per zone.
- **Text screens** (title, high scores, "entering"): one indirect object per text line, each with
  its own width, x and palette, so one colour a line and up to eight in the window; the maps are
  packed end to end in `$2318..` and empty lines point at a 2-character blank.
- **The HUD** is the only place with several colours on a text line: a line is cut into objects
  (score, label, timer digits, icons) and each takes a palette: 3 palettes on a line, 4 in the band.
- **The intermission** runs its window in 160A (CTRL `$40`, one-byte characters) under the same
  320A HUD. The HUD needs only C2, and the two DLIs swap only the C2s, so the window's C1 and C3
  are written once (b2:`B36C-B390`) and stay.

### The tower and its rotation

**The picture is a character map of bit patterns** (live: `mem_f00700.bin` of `runs/w1`; code
f3:`C1BF`). At a tower's load `C1BF` builds the character set in `$1800-$1FFF`: page `$18` = 0 and
pages `$19-$1F` = the character's own code, so character `c` shows `c` as eight pixels on seven
lines and a blank eighth (the mortar line). The loop is 32 bytes. Characters `$D7-$DE` are then
overwritten with the sea's dither. A row of the window is therefore 24 bytes = 192 pixels at full
320 resolution, 8 lines tall.

**Everything is redrawn every tick, moving or not** (live, `runs/p1`: the same cycles standing and
walking). Into the hidden map, in this order:

1. f3:`C391` clears the 4 bytes at each end of the 18 rows; f3:`C4AA` fills the 16 middle bytes
   of every row from b2:`A200` (8 rotation phases x 16 bytes; phase = view angle AND 7), even rows
   with one phase and odd rows with the phase 4 on (the half-brick stagger). 128 bytes of ROM are
   the whole wall, perspective included: the joints are 10 pixels apart in the middle, 6 at the rim.
2. f3:`C7A9` then `C7C8` draw the map's elements at 14 of the 16 angular columns, back ones
   first, then the front from the rim to the middle (so nearer ones overwrite). For each column
   and each of the 18 visible rows: read the cell from `$6A00`, and if it is an element, AND a mask
   and OR a shape into 4 or 5 bytes of the row (`LDA (mask),Y / AND (row),Y / ORA (shape),Y /
   STA (row),Y`, f3:`C6F7`, `C71B`, `C748`, `C769`).
   - **x**: b2:`A2D8`, 128 bytes: relative angle -> x in 2-pixel units, bit 7 = hidden.
     `x/4` is the byte column and `x AND 3` picks one of **four pre-shifted copies** of the shape.
   - **shapes**: b2:`A100-A1FF`: 4 element types x 4 shifts x 8 bytes, masks then data at `+$80`.
     Steps keep their width all the way round; only x follows the cylinder.
   - Cell codes (code): `$80/$84/$8C`, `$85/$89/$8D`, `$81` (the step), `$82` (ORed through the
     flash mask `$64FF`, pattern f3:`C479`), `$83` (the door). Bit 7 clear and non-zero = an enemy
     to spawn there (type in bits 4-6).
3. f3:`C630` draws doors (`$83`) on the front half only, with **one shape per angle**: x from
   b2:`A298` (64 bytes), mask b2:`9F00+4n`, data b2:`A000+4n` (64 x 4 bytes each). A door is 2
   pixels wide at the rim and 26 in the middle: real foreshortening, paid for with 512 bytes.

Rotation tables in all: 128 + 128 + 256 + 64 + 512 = 1,088 bytes, plus 128 for sprite x.

**Sprites round the cylinder** (code f3:`E020`): x = b2:`A358`[(angle - view + 12) AND 127] + `$21`,
bit 7 = behind the tower; enemies are sorted by angular distance from the front (f3:`D62A`) and
drawn far to near. The player never moves sideways (x `$4A`): the tower turns under him.
Collision reads the map cells, not the picture (f3:`E784`).

**Live check**: poking `$6A60-$6A63` = `$81` in play put a four-step platform on the tower
(`runs/k1/cmp_f700.png`).

**The tower data in ROM** (code f3:`C8CA`-`C974`; live: the writes at `C951`). Per tower (b0:`AD00`
table: pointers, rows, colour): a 2-byte bitmap for each 16-cell row, LSB first, and one data byte
for each set bit; clear bits leave 0. Eight towers, 569 rows = 9,104 cells, stored as 1,138 bytes
of bitmap + 1,349 of cells = **2,487 bytes, 27%** (by tower 25-31%). The unpacker is 65 bytes
(`C934`) plus 74 of setup; with the 1,664-byte clear it takes about 35,000 cycles (estimate from
the loop; live it spans two frames). Quirk: the loop runs one row more than the table says and
reads the next tower's first bitmap bytes, which are zero.

### Vertical scroll

The window is always 18 zones and 137 lines: a first zone 1, 3, 5 or 7 lines tall, 16 of 8, and a
last zone of 8, 6, 4 or 2 (code f3:`E6FF`; live `runs/v1`: `$2218` = `$84`, `$224B` = `$83` at
camera y `$2E`). A short first zone shows the bottom of its characters by itself. The short last
zone must show the top, so the DLI on it (f3:`FEEB`) sets CHARBASE to `$18` + (first height - 1)
(seen `$18, $1A, $1C, $1E`: this is the "stepping CHARBASE" of the first survey), and `E71A` raises
the page of that zone's ten sprite slots by the same amount (`$71..$77`). That DLI then burns 9
WSYNCs before setting CHARBASE `$80` for the HUD's font.

### The sea

Static (live: nothing writes `$18D7-$1FDE` or the sea's colour after a load). f3:`C975` gives the
bottom-most zones sea rows when the camera is low: zone k from the top of the sea gets the map row
f3:`C000 + 32k`, i.e. character `$D7+k`, so depth is the dither's density. 5 rows show at the
tower's foot (6 seen with the camera poked lower; the ROM map has 8). No reflection and no wave animation in this port. The splash and the submarine are
strip sprites.

### The sprite strip (`$7100-$78FF`)

Each actor owns fixed 3-byte columns: the player's two planes at `$00-$0B` and `$60-$6B`, the door
overlay `$0C-$11` and `$6C-$71`, the four enemy slots from `$12, $1E, $2A, $36` (f3:`DF11`), one
more object at `$42-$43` (f3:`E105`; the snowball: hint). A sprite's cells are stacked at descending columns (cell below = column - 3), every
list entry's page is `$71`, and MARIA's zone offset picks the line page.

- Source art sits in the switched banks **stored the way MARIA would read it** (3 bytes a line,
  the next line a page on: b0/b1:`$88xx` the player, with plane 2 at `+$80`; b0:`$9Dxx` enemies).
  The copy is `LDA (src),Y / STA (dst),Y` three times, then `INC` both high bytes.
- **Vertical position in 2-line steps**: `y AND 3` picks one of four routines (f3:`DAAD`, `E018`
  tables) that clear, copy part of the sprite, step to the next cell (`D7E5`) and copy the rest, by
  entering unrolled copy code at different points. One header per zone, no holes, no padding.
- **Clipping**: enemies are copied through three per-cell byte masks (`AND $64E2-$64E4`, set from
  `$64D9-$64E1`) so they can slide behind the tower's edge.
- The door overlay (f3:`DB02`) is two more planes drawn over the player, so he walks "into" a door.
- The art's bank is in only during the copy (f3:`DA0C`, `DEDB`), which is why MARIA never needs it.
- Nothing is ORed into the strip, so the CPU never reads it.

Cost (live, `runs/p1`): the player's blit 2,470 cycles a tick, his headers 580; two enemies with
sort about 3,000-5,000.

### Banks, scenes and sound

- b0: tower table and packed towers (`AD00-B6E6`), sprite art. b1: the 2K text/intermission
  character set (`9D00`, copied to `$1800` by f3:`C37D`), music. b2: code for the intermission and
  the tower's arrival sequence, the rotation tables, the DLL/HUD image (`9D00-9EFF` -> `$2200`),
  the intermission's maps (`B9AB`..), effect streams. b0 and b1 hold no code (traced: 0).
- **`$8000-$87FF` is byte-identical in the three banks** (checked): the HUD font at CHARBASE `$80`
  is there whichever bank is in.
- **Each bank ends with its own number** (`$BFFF` = 4, 5, 6). Code that must switch reads it,
  pushes it, switches, and stores it back (f3:`FA22`, and the NMI at `FECD`): no RAM shadow.
  Live: the NMI's restore wrote 4 in 338 frames and 5 in 18, i.e. it interrupted blits and put
  their bank back.
- Sound is TIA only, once a frame from the bottom DLI: effects f3:`FB82` (2-byte steps from b2),
  music f3:`FB10` (b1, tables at `A500`). No sampled sound.
- (code, not tried) f3:`FE48`: a change of the difficulty switches with the right one at B skips
  to the next tower and clears the score.

### The intermission ("catch some fish for bonuses")

Reached by poking the tick result `$B1` = 2 in play (live, `runs/i1`). b2:`B2AF`: loads the black
set, copies the 2K character set from b1, sets CTRL `$40` for the window, writes six palettes' C1
and C3 once. The scene is 18 zones of **two character objects a row** (32 + 8..24 characters, to
get past 32) pointing into ROM maps b2:`B9AB`.., scrolled by the low byte and x of each header,
with **six bands at their own speeds** (`$6996-$699B`; b2:`B4A1`). Sprites use the same strip and
slots (`E637` leaves slot 0 to the second row object). 30 Hz. The technique is the one in the
pseudo-3D skill ("Character backgrounds scrolled through header bytes only"), with parallax.

### What a frame costs

- **Structure.** Main loop f3:`FCBC`: pause check, one wait for vblank's end (`FD94`), then 23
  routines in a row (`FD07-FD49`). In play that body takes about 2.6 frames, so a tick is **three
  frames, 20 Hz**, always (live: 44 ticks in `runs/p1`, standing and walking). The flip is the
  tick's first act. Interrupts: `NMI -> JMP ($0060)`, a three-stage chain that re-arms itself
  (window top `FF19`, last zone `FEEB`, bottom `FE8A`); the bottom stage counts frames, loads the
  HUD's colours and runs both sound drivers with bank switches.
- **Measured** (`tools/prof.lua`, NTSC frame 29,850 cycles):

| Scene | CPU cycles run a frame (waits included) | of which NMI code | WSYNCs / cycles stalled | MARIA's DMA |
|---|---|---|---|---|
| play, tower 1 | 20,520 | 400-510 | 12 / 1,040-1,160 | 8,170 (27%) |
| intermission | 15,880 | 403 | 12 / 1,100 | 12,870 (43%) |
| title | 23,030 | 405 | 12 / 1,250 | 5,570 |

- **A play tick** (61,560 cycles available, about 53,000 used, 8,500 spent waiting): wall and back
  elements 10,900; doors 7,370; front elements 12,800; sea and row headers 1,140; slot clear
  2,010; enemy logic 1,520; enemy sort and blits 3,000-7,000; spawn scan of the map 5,650; player
  2,470 + 580; HUD 740; flip 300. Walking changes none of it by more than 2%.
- An intermission tick is two frames: about 19,200 cycles of work.

### Dead ends and corrections

- The CHARBASE values `$18-$1E` at the last zone are scroll compensation, not an animation.
- `$6947`, `$694C` (first survey: "variables") are list bytes: the last zone's slot pages.
- The "ten unrolled stores at `E5FE`" clear the slots; they do not write the lists. The eight
  parallel stores at `C22B` clear the strip; the drawers are elsewhere (above).
- I expected the sea to animate and looked for writers of its characters and colour: none.
- My first DMA figures included the WSYNC stalls; `prof.lua` now times them (`emu.time()` between
  the WSYNC write and the next opcode fetch).
- Lua read taps do see opcode fetches on this build (a tap on `$0000-$FFFF` with address = PC):
  the cycle counter depends on it and gave steady totals. HARNESS.md says otherwise.

### Not determined

- Game logic `F28E-F9FF`, most of b2, the music and effect formats, the high-score entry, the
  game's end, two-player play: not read.
- Towers 2-8, lifts, the snowball, a demo mode (none appeared in 3,000 idle frames): not run.
  The packing figures for all eight towers are from the ROM, not from eight loads.
- How the 320A pair rule (a lit pixel draws its partner as background) shapes the art: not studied.
- DMA was measured as a remainder, not compared with `dmabudget.py`.
- The traced listing (`towertoppler/disasm/`) reaches 93.8% of f3 and 15% of b2 as code; about a
  third of f3 was actually read and is named in `annotations.json`.
