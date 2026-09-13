#!/usr/bin/env python3
"""Desert Shift: extract [[[...]]] segment, brute Caesar shifts."""
from __future__ import annotations

import re
import sys
from pathlib import Path


def caesar(text: str, shift: int) -> str:
    out = []
    for ch in text:
        if "a" <= ch <= "z":
            out.append(chr((ord(ch) - 97 + shift) % 26 + 97))
        elif "A" <= ch <= "Z":
            out.append(chr((ord(ch) - 65 + shift) % 26 + 65))
        else:
            out.append(ch)
    return "".join(out)


def find_scroll() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    here = Path(__file__).resolve().parent
    candidates = [
        Path("scroll.txt"),
        here / "scroll.txt",
    ]
    for p in candidates:
        if p.is_file():
            return p
    raise SystemExit("usage: 01-desert-shift-solve.py [scroll.txt]")


def main() -> None:
    text = find_scroll().read_text()
    m = re.search(r"\[\[\[(.*?)\]\]\]", text, re.S)
    if not m:
        raise SystemExit("sealed [[[...]]] segment not found")
    seg = m.group(1)
    for s in range(26):
        pt = caesar(seg, -s)
        if "nustCTF{" in pt:
            print(f"shift={s}: {pt}")
            return
    raise SystemExit("no shift found")


if __name__ == "__main__":
    main()
