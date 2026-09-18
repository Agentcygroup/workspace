import sys
from core import sha256_hex

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("usage: agentcy hash <text>")
        return 2
    if argv[0] == "hash" and len(argv) == 2:
        print(sha256_hex(argv[1].encode()))
        return 0
    print("unknown command", file=sys.stderr)
    return 2

if __name__ == "__main__":
    sys.exit(main())
