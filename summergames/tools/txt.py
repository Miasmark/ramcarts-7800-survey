"""txt.py GAME BANK ADDR N: show N bytes from a bank as text, control bytes as <xx>."""
import sys

sys.path.insert(0, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "..", "..", "tools"))
import dis  # noqa: E402


def main():
    game, bank, addr, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3], 16), int(sys.argv[4])
    raw, nb = dis.load(game)
    s = ""
    for i in range(n):
        b = dis.peek(raw, nb, bank, addr + i)
        s += chr(b) if 32 <= b < 127 else "<%02X>" % b
    print(s)


if __name__ == "__main__":
    main()
