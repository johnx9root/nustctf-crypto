#!/usr/bin/env python3
"""XOR at Dusk: recover short repeating key via crib nustCTF{."""
from __future__ import annotations

import sys
from pathlib import Path


def find_hex() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    here = Path(__file__).resolve().parent
    candidates = [
        Path("ciphertext.hex"),
        here / "ciphertext.hex",
    ]
    for p in candidates:
        if p.is_file():
            return p
    raise SystemExit("usage: 05-xor-at-dusk-solve.py [ciphertext.hex]")


def main() -> None:
    ct = bytes.fromhex(find_hex().read_text().strip())
    crib = b"nustCTF{"

    for period in range(2, 5):
        for offset in range(0, len(ct) - len(crib) + 1):
            ks = bytes(ct[offset + i] ^ crib[i] for i in range(len(crib)))
            if not all(ks[i] == ks[i % period] for i in range(len(ks))):
                continue
            pt = bytes(ct[i] ^ ks[(i - offset) % period] for i in range(len(ct)))
            try:
                s = pt.decode("ascii")
            except UnicodeDecodeError:
                continue
            if "nustCTF{" in s and "}" in s:
                key0 = bytes(ct[i] ^ pt[i] for i in range(period))
                print(f"period={period} key={key0!r}")
                print(s)
                return
    raise SystemExit("no solution")


if __name__ == "__main__":
    main()
