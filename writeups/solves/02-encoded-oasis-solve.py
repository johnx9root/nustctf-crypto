#!/usr/bin/env python3
"""Encoded Oasis: base64 -> ascii hex -> base64 -> zlib."""
from __future__ import annotations

import base64
import sys
import zlib
from pathlib import Path


def find_note() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    here = Path(__file__).resolve().parent
    candidates = [
        Path("note.b32"),
        here / "note.b32",
    ]
    for p in candidates:
        if p.is_file():
            return p
    raise SystemExit("usage: 02-encoded-oasis-solve.py [note.b32]")


def main() -> None:
    data = find_note().read_text().strip()
    step1 = base64.b64decode(data)  # ASCII hex string
    step2 = bytes.fromhex(step1.decode())  # inner base64 bytes
    step3 = base64.b64decode(step2)  # zlib blob
    plain = zlib.decompress(step3)
    print(plain.decode())


if __name__ == "__main__":
    main()
