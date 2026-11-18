## Jinks (Atari / Softgold 1989, 128K SuperGame + RAM)

Survey plus a focused read, 2026-11-18. Tags: **live** (seen in MAME), **code** (read only),
**hint** (guess). Addresses are `bank:address`; all code is in bank 7 (`f7`), banks 0-6 are data.

### In one paragraph

Jinks uses cart RAM as **a second bank window**, not as an unpacking buffer. Nothing in the ROM is
packed. Whatever must stay visible or readable while a different ROM bank is switched in is copied
to RAM first: sampled sound (so the title picture's or the menu font's bank can be in), and in play
the level's character map and character set (so the sprite bank can be in). Because the map and the
character set are then in RAM, the game also edits them: a destroyed brick is two map stores, and
one character's graphics are rotated in place to animate every cell that shows it. The playfield
scrolls by one header byte and one x per row object. Only `$6000-$7FFF` is ever touched; the lower
8K is unused.

### Cart RAM map

| Range | Size | Use | Written by | Read by |
|---|---|---|---|---|
| `$4000-$5FFF` | 8,192 | never read or written in any run (live) | - | - |
| `$6000-$7EFF` | 7,936 | title: sample image 1, from `b0:$9900-$B7FF` (one clip, 3.0 s) | `f7:$FD3F` (`Sample_CopyToRam` `$FD2E`, called `$C053`) | CPU `$FCB2`/`$FCF8` (`Sample_Play` `$FC91`) (live) |
| `$6000-$78FF` | 6,400 | menu and game over: sample image 2, from `b0:$8000-$98FF` (two clips at `$6000` and `$6C5E`, 1.2 s each) | `$FD3F` (called `$C07C`, `$C27C`, `$C330`, `$C50D`, `$C6CA`) | CPU, same player (live) |
| `$6000-$74FF` | 5,376 | play: the level's character map, 21 rows x 256 columns, **a row a page** | `$CB79` at the load; `$E7E6`/`$E7E9` when a brick goes (live) | MARIA (42 indirect objects); CPU `$E719` (ball against the map), `$E3AB`, `$E42E` (live) |
| `$6000-$63FF` | 1,024 (840 used) | interlude: a 21 x 40 map from `b6:$B500` | `$D0D7` (live, forced) | MARIA |
| `$7500-$7CFF` | 2,048 | play: character set, 256 one-byte characters x 8 line pages, CHARBASE `$75` | `$CB9B` at the load; `$DF87` rotates character `$FA` (live) | MARIA; CPU `$DF7D` reads back what it rotates |
| `$7D00-$7DFF` | 256 | the level's object records (templates from the play bank, then changed in place) | `$CC8C`, `$D11D` (interlude), `$D992-$D9E2`, `$EF8F`, `$F025` (live) | CPU `$D8A7-$D9DB`, `$EF32-$F5A5` |
| `$7E00-$7EFF` | 256 | nothing after the title (tail of sample image 1) | - | - |
| `$7F2F-$7F82` | 84 | high-score table, seeded from `f7:$FA4A` | `$FA43` (live) | CPU `$FB7D-$FBC3` |
| `$7F83-$7FF2` | 112 | menu text lines built from the table | `$FB9B-$FC00` (live) | MARIA (indirect, e.g. `$7F83` w8) |
| `$7FF3-$7FFA` | 8 | the score as characters | `$FC41-$FC83`, every game frame (live) | MARIA (HUD line, 320A) |
| `$7FFB-$7FFE` | 4 | score just earned, waiting to be added | `$E7ED-$E7F8`, `$F011-$F019` | CPU `$F6AB` (code) |

No display list and no code is in cart RAM (live: lists are at `$1800-$1E3F` and `$2200-$27C8`
in console RAM; no PC was sampled in `$4000-$7FFF`). Console RAM is nearly all lists (two full
sets), which is why the game's records and text buffers sit in cart RAM.

### Banks

| Bank | Holds | Evidence |
|---|---|---|
| 0 | samples only: image 2 `$8000-$98FF`, image 1 `$9900-$B7FF` (14,336 bytes) | live |
| 1 | the title picture: 160B, 125 direct objects of 16 bytes, 25 zones x 8 lines = 16,000 bytes, **unpacked**, in eight 8-page blocks `$8000-$BFFF` (object n at block n/16, column 16 x (n mod 16)); 384 bytes of the bank are left | live (list dump) |
| 2 | 320-mode font at `$8100-$88FF` (CHARBASE `$81`: menu and the HUD line), the menu's character maps from `$8900` (rows of 40), the "get ready" sample `$9000-$B604` (9,731 bytes, 3.7 s) | live for font and maps, code for the sample (`$C1FA`), its length matches the 226 frames the screen lasts |
| 3, 4 | play banks for levels 3-4 and 1-2: sprites in H8 holey blocks `$80-$87`, `$90-$97`, `$A0-$A7`, `$B0-$B7`, pointers to object lists at `$8000`, sound-effect table at `$8117` | live (bank log, list dump), code for the tables |
| 5, 6 | level data for levels 3-4 and 1-2: map A `$8000-$94FF`, character set `$9500-$9CFF`, map B `$A000-$B4FF`; bank 6 also the interlude map `$B500-$B8FF` | live |
| 7 | all the code (90.3% of the bank reached by the tracer) | - |

Each bank 1-6 has **its own number in its last byte, `$BFFF`** (bank 0 has `$FF`). The NMI saves the
current bank with `LDA $BFFF` (`$D77D`) instead of keeping a shadow.

### The level load (question 2)

`Level_Load`, `f7:$CB47-$CCC4` (code and live). **A plain copy, nothing is unpacked.**

1. Display off (CTRL `$78`), NMI handler set to a bare `RTI`.
2. Bank = `dat_FD63[(level AND 3) >> 1]` = 6, 6, 5, 5. Source page `$80 EOR ram_0050` (`$80` or `$A0`).
3. `$CB73-$CB83`: 21 pages to `$6000-$74FF`, `LDA (zp),Y / STA (zp),Y`, about 16 cycles a byte.
4. `$CB85-$CBA5`: 8 pages `$9500-$9CFF` to `$7500-$7CFF`.
5. `$CBA7-$CC2E`: the 21 row lists in both list sets get their two headers' addresses.
6. Palettes P0/P1 from `dat_FD73`/`dat_FD76` indexed through `dat_FD65` (6 bytes a level); the
   background colour comes per level too (`ram_0048`: `$46`, `$51`, `$04`, `$74`, live).
7. Bank = level bank - 2 (4 or 3): the play bank. `$CC5E-$CC92` copies 256 bytes of object records
   to `$7D00` from a pointer at `$8000,X` of that bank (the loop runs twice over the same page: a
   harmless slip).

Time: 5 frames with the display off (live: frames 530-534 in `runs/s1`, about 1,858 bytes a frame).

Sizes: 2 maps x 5,376 + 2,048 = 12,800 bytes of each 16K level bank. What packing would have done
(`jinks/tools/romstats.py`, offline, on the four real maps): literal/run RLE 3,128-4,610 bytes
(58-86%), 2x2 block dictionary 3,844-4,984, **zlib 1,215-1,741 (23-32%)**. The maps have 79-154
distinct characters and little run structure: only an LZ-class packer would have paid. The two
character sets in banks 5 and 6 are **byte-identical** (2K stored twice); one 256-character set
serves all four levels (levels 1 and 3 share 66 characters; the pair in bank 5 uses 217 in all).

Why the character set is in RAM (code, with the live facts above): (a) the level bank is not in
during play, the sprite bank is; (b) character `$FA` is animated in place. Not for per-level sets
and not for de-interleaving: the ROM copy is already in MARIA's line-page layout.

### Scrolling (question 3)

Horizontal only, live (`runs/s2_move`, list dumps at five scroll positions) and code
(`Scroll_WriteRowHeaders` `f7:$D7E8-$D845`).

- 21 zones of 8 lines, CTRL `$40` (160A, one-byte characters: a character is 4 pixels wide). Each
  row is **two indirect objects**, widths 32 and 10 (42 characters: 40 on screen, 2 for the fine
  scroll), because an object is at most 32 wide. The second object's address is the first + `$20`
  and its x is the first's `EOR #$80`.
- Scroll position is 16-bit pixels in `ram_0056/57` (at most (256 - 42) x 4 = 856 by arithmetic; `$0114` was the furthest seen). Coarse = position >> 2 goes to the
  header's **low address byte**; fine = -(position AND 3) goes to x. A row is a page, so the high
  byte never changes and no carry is needed. Four stores a row, about 67 cycles x 21 = 1,400 cycles a
  game frame (counted from the listing, an estimate). The map is never rewritten to scroll.
- Lists are double-buffered: two complete sets (`$1800` and `$2200`), DPPH flipped by
  `EOR #$3A` at the top of each game frame (`$C2C7`), the back set rewritten. Each row list is 60
  bytes: 2 five-byte headers, room for 12 sprite headers, terminator. `Lists_ResetSpriteFill`
  (`$D846`) resets 21 fill pointers each frame; `Objects_Walk` (`$D882`) culls records by
  x - scroll and appends sprites.
- Sprites are placed across two zones with **H8 holey DMA** (DLL entries of the 21 rows have the H8
  bit, live; e.g. objects `$B436` in one zone and `$AC36` in the next). A 16-line sprite is two
  8-line slices in consecutive even blocks (`$B0-$B7` then `$A0-$A7`).
- The DLL: 31 entries: 3 blank zones, 21 rows, blank, HUD line, blank, 3 blank, and one **3-line
  zone** that only pads the frame to 243 lines.
- The 5 DLIs (`Nmi_Play` `f7:$D759`, a counter in `ram_0046`; code, with CTRL/CHARBASE/bank writes
  live at lines 210 and 225):
  0. top of frame: `INC ram_00EA`, the frame counter the main loop uses to hold 30 Hz;
  1. first map row: BACKGRND = the level's colour;
  2. last map row: BACKGRND = 0;
  3. above the HUD line: saves the bank from `$BFFF`, CTRL `$43` (320A), bank 2, CHARBASE `$81`,
     then **spins inside the NMI** until the next DLI;
  4. below the HUD line: CTRL `$40`, the saved bank back, CHARBASE `$75`, then the sound tick
     (`Sound_Tick` `$E4C7`, two TIA voices), counters cleared.
  No palette is changed per zone. Colours on screen in play: background + P0 (3) for the tiles,
  P1 for the two border rows, P2-P5 for sprites, one HUD colour: about 10 in level 1.

### Tile animation and bricks (question 4)

- `Tile_RotateCharFA`, `f7:$DF69-$DF99` (live and code). Every third game frame (every 6th video
  frame: 355 frames of 2,125 in `runs/s1`) it rotates the byte of character `$FA` right by two bits
  (one 160A pixel) in each of the eight line pages: `$75FA`, `$76FA` ... `$7CFA`. Eight reads, eight
  writes, about 470 cycles (estimate from the listing). `$FA` is a chevron (`40 10 04 01 01 04 10
  40`); level 1 shows it in 32 cells (two columns of 16), so 8 stores move 32 tiles and would move
  any number. Only this one character animates.
- Bricks are a map store (live: `runs/s4_brick`, the ball poked onto a brick; and code
  `Ball_MapCollide` `$E719`, `Brick_Erase` `$E7E4`). The ball's cell is read from the map
  (`row page = $60 + y/8`, `Y = x/4`). Character codes are ordered by meaning: bit 7 set, `>= $76`,
  `$41`, `$47`, `$5F-$6B` are open floor; ranges pick the bounce (`$15-$16`, `$17-$1A`, `$1E-$1F`,
  `$22-$23`); `$2F-$36` and `$6C-$6D` are bricks, two cells wide, the code's low bit saying which
  half was hit. Erasing writes `$FD` (floor) to both cells and puts 5 in the score-delta bytes.

### Samples (question 5)

`Sample_Play`, `f7:$FC91-$FD19` (live for the RAM images, code for the ROM one).

- Format: a big-endian length word, then bytes of **two 4-bit samples**, high nibble first. Both
  AUDV0 and AUDV1 get each nibble. One nibble every 3 scan lines, clocked by `STA WSYNC`:
  15,734 / 3 = **5,245 Hz**, 2,622 bytes a second (live: 43 bytes read a frame).
- It is a foreground loop: the CPU does nothing else, the picture stays up because the lists are
  static and DMA stays on, and the NMI handler is a bare `RTI`. Once a page of data (about 6
  frames) it polls the stick, the buttons and the console switches when `ram_2137` is set.
- Three places hold samples: bank 0's two images, copied to cart RAM because bank 1 (title art) or
  bank 2 (menu font and maps) must be in while they play; and bank 2's `$9000` clip, played
  straight from ROM under the "get ready" text, whose font is in the same bank.
- No sample is played during play: every caller is between scenes (code: `$C069`, `$C0BC-$C191`,
  `$C202`, `$C440`, `$C68E`, `$C6B2`). ROM spent on samples: 24,069 bytes for 9.2 seconds.

### Frame structure

`Play_MainLoop` `f7:$C2C7`: flip DPPH, wait for vblank (`BIT MSTAT`), read the console switches,
then input, ball, scroll, sprite lists, objects, tile animation, score; if fewer than 2 frames have
passed (`ram_00EA`, counted by DLI 0) wait one more. So the game runs at 30 Hz and slips to 20
rather than tearing. Sound is ticked from the last DLI.

### Other things seen

- **Level skip:** in play, hold Pause, press Select, release both (`$C2E3`/`$C345`): the next
  level loads. Not in the first ~340 frames of a level, where Select returns to the menu
  (`Play_StartPhaseLoop` `$C221`). Used for `runs/s3_levels`.
- The interlude ("GET READY FOR THE INTERLUDE", `Interlude_Load` `$CECC`, `$D0BC-$D120`) reuses
  the character set left in RAM by the level and loads only an 840-byte map. Seen by forcing
  `ram_2130` (`runs/s5_bonus`).
- The menu is 320D (CTRL `$42`) from ROM maps in bank 2, with the text lines that change read from
  cart RAM.

### Corrections to the first survey's reading

- "Boot clears `$6000-$7EFF` (`$FD3F`)": it is a copy of sample data from bank 0, not a clear.
- "Bank 2 then 4 inside each frame: music or sound in bank 2?": it is the HUD line's font. The sound
  tick runs after the play bank is back.
- "`$7D07`/`$7D08` are counters": they are the first object record's animation frame index and
  timer.
- The 16,384-byte "reads" by `$E4B9`/`$E4BB`/`$FCC3` are the probe's own memory dumps.

### Dead ends

- Looked for an unpacker behind the 4-frame load: there is none; the source pages are the map.
- A first level tour pressed Select alone: it returns to the menu. Pause + Select too early in a
  level leaves the game paused. Third script worked.
- `$E49F` stores through a pointer that looked like a map write: it toggles a byte of a menu list.

### Not determined

- Whether the cart's RAM chip is 8K (the game never touches `$4000-$5FFF`: hint).
- What `$E3AB` (reads row 19, `$7300-$739C`) and `$E42E` test: paddle or enemy against the map
  (hint).
- The frame's cost in cycles was not measured; the cycle figures above are counted from listings.
- Whether there is music in play (the driver is an effects driver with two streams; not followed).
- H8 holes are shown working in MAME only.
- The ending and the game-over path were read only as far as their sample calls.

### Coverage

Traced listing of bank 7: 90.3% of its bytes as code (`jinks/disasm/src/f7.asm`, from
`annotations.json` with 31 labels). Read closely: boot, menu sample loops, both NMI handlers, the
level and interlude loads, the scroll writer, the head of the object walker, the ball's map test and
brick erase, the tile rotation, the sample player, the sound tick and request. Not read: sprite
placers `$DA26-$DF68`, paddle and ball physics `$E0D1-$E3FF`, enemy logic `$EF32-$F5BB`, the title
and menu builders, the score routines.

### Files

- `jinks/runs/`: `s1` (first survey), `s2_move` (scroll in four directions, `map_level1.png`),
  `s3_levels` (all four levels, maps rendered), `s4_brick` (ball poked onto bricks), `s5_bonus`
  (interlude forced).
- `jinks/tools/`: `romstats.py` (bank use, packing estimates, sample lengths; output
  `jinks/romstats.txt`), `mapinfo.py` (map facts, diffs and a render from a dump), `show.py`,
  `regen.py`, `annotate.py` (listing helpers).
- `jinks/disasm/annotations.json`, `jinks/disasm/src/`. `jinks/NOTES.md` has the run scripts.
