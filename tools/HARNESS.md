# The survey harness, and the rules every run here follows

Project: `ramcarts-7800-survey`. A survey of the
five retail 7800 carts with RAM at `$4000` (Tower Toppler, Jinks, Impossible Mission, Summer Games,
Winter Games): what they keep in cart RAM and which techniques a homebrew could borrow.

## Rules (all of them are hard)

- **MAME never opens a window or a dialog.** Only the fork `mame-fork/a78.exe`,
  always `-video none -sound none -nothrottle`, a `ui.ini` with `skip_warnings 1` in the run folder,
  each run in its own folder with its own `-cfg_directory`, `-nvram_directory`, `-snapshot_directory`.
  `tools/run.py` does all of that; use it (or copy it) for every run. Other agents run MAME at the
  same time. **Do not use the `a7800-mame` MCP tools** (one shared instance, taken).
- **Everything you write goes inside this project**, in your game's folder (`<game>/`: `runs/`,
  `tools/` for your own scripts, `disasm/`, notes) or `docs/parts/`. Nothing on `Z:\TEMP`. Read-only
  everywhere else: the toolkit (`a7800-toolkit`), the ROM library,
  the skills, the other games' folders, and the shared `tools/` here (copy a tool into
  `<game>/tools/` before changing it).
- **No git** anywhere (no init, commit, push).
- **Python scripts are written to files with the Write tool**, not shell heredocs (backslashes get
  mangled). Run Python that reads a ROM with `-I`.
- **Tag every claim**: **live** (seen in MAME: a write log, a list dump, a watchpoint, a poke that
  changed behaviour), **code** (read from a disassembly only), **hint** (a guess). Dead ends and
  corrections are findings too: write them down.
- If a tool fails, diagnose and work round it.
- Keep what you print small: these tools write files; read digests, not dumps.

## Tools (in `tools/`)

- `python -I tools/run.py GAME RUN LUA [KEY=VALUE ...]`: one windowless run in `<GAME>/runs/<RUN>/`
  (wiped first), boots with `-bios skip`. GAME is `towertoppler`, `jinks`, `impossiblemission`,
  `summergames` or `wintergames`. LUA is a script name in `tools/` or an absolute path (a relative path outside `tools/` is not found). KEY=VALUE become
  environment variables for the script. `DEBUG=1` adds `-debug -debugger script` (the fork's
  windowless debugger: toolkit `docs/emulation.md`, "Breakpoints, watchpoints, stepping and tracing").
  About 350% speed with survey.lua's taps: 3,000 frames take 15 s.
- `tools/survey.lua`: the survey probe. `SCRIPT="frames:stick:button;..."` (stick letters `l r u d`
  or `-`; button 0 none, 1 fire, 2 second button, +4 Pause, +8 Select, +16 Reset), `SNAPS="a,b,c"`
  (frames: a screenshot, `mem_fNNNNN.bin` = `$0000-$7FFF`, `regs_fNNNNN.txt` = last value written to
  each MARIA register and the bank), `END=frame`, `POKES="frame:addr=val,addr=val;..."` (hex).
  Logs: `cpuw.txt` / `cpur.txt` (CPU writes / reads of `$4000-$7FFF` per frame, by PC with address
  range), `mariar.txt` (MARIA's reads of `$4000-$7FFF` per frame by page, from her own `dma` address
  space, so they are hers and not the CPU's), `regs.txt` (CTRL `$3C`, CHARBASE `$34`, DPPH `$2C`,
  DPPL `$30` writes with line and PC, logged when a frame's sequence changes), `bank.txt` (bank
  register writes), `summary.txt` (totals by PC, MARIA's pages, any PC seen inside cart RAM).
- `python tools/digest.py RUNDIR [--top N] [--segs N]`: the short digest of those logs (pipe it
  through `cut -c1-250`).
- `python tools/dll.py RUNDIR [FRAME ...] [-v]`: decodes the DLL and every list from a dump; writes
  `dll_fNNNNN.txt` and prints where the lists, graphics and character maps live (console RAM, cart
  RAM, ROM). Give frames, or the output is long.
- `python tools/sheet.py RUNDIR [cols]`: contact sheet `sheet.png` of a run's screenshots, labelled
  by frame. Read it with the Read tool to see where a script got to.
- `python -I tools/dis.py GAME BANK ADDR [COUNT]` / `... N --hex`: linear disassembly or hex dump
  from a ROM address in a bank (pipe through `paste - - -` to save lines).
- The toolkit's own tools and probes may be run read-only with outputs directed here (its
  `README.md`, `docs/method.md`, `docs/pitfalls.md`, `docs/emulation.md`, `docs/cartridges.md`,
  `docs/graphics.md`, `docs/hardware.md`). `tools/disasm.py` with an `annotations.json` in your
  folder gives a traced listing; `probes/cyclebudget.lua`, `rendersurvey.lua`, `pcprof.lua`,
  `dlitimes.lua` measure a frame (each probe's header lists its `A7800_*` variables; run them through
  `run.py` so they stay windowless and write into your run folder).

## What works in Lua on this MAME (checked 2026-11-18)

- `manager.machine.devices[":maincpu"].spaces["program"]` is the CPU's view;
  `manager.machine.devices[":maria"].spaces["dma"]` is MARIA's own space: a read tap there sees only
  her fetches. `cpu.state["CURPC"].value` is the instruction's address (state keys: PC, CURPC, A, X,
  Y, P, SP).
- **Keep every tap and callback in a global**, or it is garbage-collected and stops silently.
- Correction (Tower Toppler's worker, 2026-11-18): a read tap over the whole of `$0000-$FFFF` does
  see opcode fetches on this build (`towertoppler/tools/prof.lua` counts cycles that way). survey.lua
  taps only `$4000-$7FFF` and samples the PC at each tapped access and at frame end. That found no
  code in cart RAM at any title screen; Impossible Mission does run two 4-byte thunks at
  `$7270/$7274` on its puzzle screen (`impossiblemission/runs/z3`).
- A write through `STA (zp),Y` also shows as a read of the same address (the 6502's dummy read):
  reads and writes with the same PC and count are one store.
- Ports: `:JOYSTICKS` (P1 Left/Right/Up/Down), `:BUTTONS` (P1 Button 1/2), `:CONSOLE` (Pause, Select,
  Reset, Left/Right Difficulty Switch). There is no `screen:vpos()`; survey.lua's `line()` works the
  line out from `time_until_pos`.
- Screenshots under `-video none` are good enough to see which screen a script reached (toolkit
  pitfalls.md warns about single stray pixels).

## The carts

All are plain SuperGame with 16K RAM at `$4000-$7FFF` that both chips see (one RAM, unlike BankSet):
the last 16K bank is fixed at `$C000`, `$8000-$BFFF` is switched by writing the bank number anywhere
in `$8000-$FFFF` (value modulo the bank count: Tower Toppler has 4 banks and writes 4, 5, 6 for file
banks 0, 1, 2). ROMs are in
`roms/`
(128-byte header). `<game>/survey.txt` has the header, per-bank entropy and strings;
`<game>/runs/s1/` is the first survey run (3,000 frames, fire pulsed).

## The questions, in order of value

1. What the game keeps in cart RAM, by region and size: unpacked or composed graphics, character
   maps, display lists, game state, code copied to RAM, buffers. Which of it MARIA reads.
2. Unpacking: if graphics, maps or text are packed in ROM and unpacked to RAM, the scheme (RLE, LZ,
   bit-plane tricks, dictionary), the routine's address and size, the ratio on real data, the time.
3. Pictures built in RAM at run time (drawn, scaled, rotated, mirrored, recoloured): how, and what it
   saves in ROM.
4. Per-scene data (events, rooms, levels): how a scene's code, art and data are banked and loaded;
   content generated from small seeds.
5. Anything else clever; sampled sound playback if met (just note where).

## What each game's worker leaves

- `<game>/`: the runs worth keeping, scripts, any disassembly or annotations (state the coverage
  honestly), and working notes.
- `docs/parts/<game>.md`: the game's findings: the cart RAM map by use (address range, size, who
  writes it by bank:address, whether MARIA or the CPU reads it), the answers to the questions with
  bank:addresses, formats and evidence tags, the frame structure in a few lines, dead ends, and what
  was not determined. Plain Markdown, `##` for the game's title, `###` below it.
- `docs/parts/<game>_techniques.md`: at most 60 lines: each technique worth borrowing (what it is in
  two or three sentences, where to read it, evidence tag, an estimate of what it costs and saves in
  bytes, RAM and cycles, labelled as an estimate, any BankSet obstacle), then the ones judged not
  worth borrowing and why, then anything that only duplicates a skill (name the skill section).

## After the survey

The per-game write-ups are `docs/parts/<game>.md` and `docs/parts/<game>_techniques.md`; each game
folder has a `NOTES.md` listing its runs, scripts and listings. Two readings of the first survey run
(`runs/s1`) were wrong and are corrected in the parts: Jinks' `$FD3F` copies samples into cart RAM
(not a clear), and reads of all of `$4000-$7FFF` on snapshot frames in the `s1` logs are this
probe's own dump (fixed in survey.lua afterwards).
