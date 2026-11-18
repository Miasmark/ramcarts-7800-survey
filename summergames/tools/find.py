"""find.py GAME HEX [HEX ...]: every place a byte pattern occurs in the ROM, as bank:addr.
HEX like "20 63 FE" (?? matches any byte).  With --ctx N prints N bytes before each hit."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import dis  # noqa: E402


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ctx = 0
    for i, a in enumerate(sys.argv):
        if a == "--ctx":
            ctx = int(sys.argv[i + 1])
            args.remove(sys.argv[i + 1])
    game = args[0]
    raw, nb = dis.load(game)
    for pat in args[1:]:
        p = [None if x == "??" else int(x, 16) for x in pat.split()]
        hits = []
        for o in range(len(raw) - len(p)):
            if all(q is None or raw[o + i] == q for i, q in enumerate(p)):
                b = o // 0x4000
                a = (0xC000 if b == nb - 1 else 0x8000) + o % 0x4000
                s = "%d:%04X" % (b, a)
                if ctx:
                    s += " [" + " ".join("%02X" % x for x in raw[max(0, o - ctx):o]) + "]"
                hits.append(s)
        print(pat, "->", len(hits))
        print(("\n" if ctx else "  ").join(hits))


if __name__ == "__main__":
    main()
