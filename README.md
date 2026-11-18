# Five Atari 7800 carts with RAM at $4000: a survey

A survey of what the five retail carts with RAM at `$4000` use it for: *Tower Toppler* (`Tower Toppler.a78`, 64K), *Jinks* (`Jinks (NTSC) (Atari) (1989) (0818D8CD).a78`), *Impossible Mission* (`Impossible Mission (NTSC) (Atari) (1987) (3B1F2F47).a78`), *Summer Games* (`Summer Games (NTSC) (Atari) (1987) (65C6DF3F).a78`) and *Winter Games* (`Winter Games (NTSC) (Atari) (1987) (8981B531).a78`). Per-game write-ups are in `docs/parts/`, each game's run notes in its `NOTES.md`, the harness in `tools/HARNESS.md`.

## How this was made, and how far to trust it

This is the output of **one automated research pass** on 2026-11-18: a single AI agent
session (Claude, working through the a7800-toolkit and MAME) given a list of questions and
about half an hour, not a long-running hand disassembly like
[galaga-7800-disassembly](https://github.com/Miasmark/galaga-7800-disassembly) and its
siblings. A second session then checked the report's main tables and routines against the
ROM's bytes; they matched. Nothing here was checked on a console.

Treat a **live** tag as "one agent saw this in MAME once", a **code** tag as a reading, and
the coverage figures below as what the tracer reached, not what was understood.

## Effort: a survey of five games, two of them deeper

One coordinating agent, about 31 minutes, which ran a first survey of all five (every write
to and read of `$4000-$7FFF` by PC and frame, MARIA's own reads of cart RAM, the lists) and
then four parallel workers, one a game (Summer and Winter Games together). The coordinator
re-checked one headline claim itself (the tower packing decodes to the live dump, 752 of
752 cells); the rest is each worker's finding with the worker's own tag.

| Game | Depth | What was done |
|---|---|---|
| Tower Toppler | deep | traced listing (93.8% of the fixed bank reached, about a third read); frame cost measured; the rotation, the colours and the strip explained. Towers 2-8 not run; game logic and music not read |
| Summer Games, Winter Games | deep on loading and unpacking | all ten events reached live; the shell, the unpacker, three Summer events and the bobsled read in code. Swimming, biathlon, ski jump and skating from logs only |
| Jinks | survey plus a focused read | about 90% of the code bank traced; level load, scrolling, tile animation, samples. Frame cost not measured |
| Impossible Mission | survey plus a focused read | listings from live PCs only (6-38% a bank); generation, rooms, puzzle pieces. Bank 2 never selected in any run; costs are estimates |

## What is here, and what is not

- `annotations.json`: entry points, labels, RAM names, data blocks and comments, in the
  [a7800-toolkit](https://github.com/Miasmark/a7800-toolkit)'s format.
- `docs/FINDINGS.md`: what the code does, with addresses, record formats and an evidence
  tag on every claim: **live** (watched in MAME: a tap, a trace, a RAM model, a poke that
  changed behaviour), **code** (read from the listing only), **hint** (a guess). Dead ends
  and corrections are kept in it.
- `tools/`: the probes and scripts the findings were made with.

**No ROM is here, and no listing.** A listing is the game's machine code in readable form;
it is rebuilt from `annotations.json` and your own legally owned dump with the toolkit's
`disasm.py`, and checked byte for byte with its `verify.py`. Captures, memory dumps,
renders of the graphics and traces are left out for the same reason.

## Running the tools

The scripts look for three things in the environment:

| Variable | What | Default |
|---|---|---|
| `A7800_ROMS` | the folder with your ROM dumps, named as below | `roms` |
| `A7800_TOOLKIT` | the a7800-toolkit's `tools` folder | `a7800-toolkit/tools` |
| `A7800_MAME` | a MAME with the Atari 7800 driver | `a78.exe` |

The live runs were made on [Miasmark/mame-Atari8bit7800](https://github.com/Miasmark/mame-Atari8bit7800),
windowless (`-video none -sound none -nothrottle`).

## Licence

MIT (see `LICENSE`) for the annotations, the findings and the tools. It does not cover the
games, which belong to their owners; nothing of theirs is distributed here.
