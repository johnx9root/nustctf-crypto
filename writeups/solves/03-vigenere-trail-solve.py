#!/usr/bin/env python3
"""Vigenère Trail: key = acronym of motto -> NAMIB."""
from __future__ import annotations

import sys
from pathlib import Path


def vigenere_decrypt(text: str, key: str) -> str:
    key = key.upper()
    out = []
    ki = 0
    for ch in text:
        if ch.isalpha():
            base = 65 if ch.isupper() else 97
            k = ord(key[ki % len(key)]) - 65
            out.append(chr((ord(ch) - base - k) % 26 + base))
            ki += 1
        else:
            out.append(ch)
    return "".join(out)


def find_ct() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    here = Path(__file__).resolve().parent
    candidates = [
        Path("ciphertext.txt"),
        here / "ciphertext.txt",
    ]
    for p in candidates:
        if p.is_file():
            return p
    raise SystemExit("usage: 03-vigenere-trail-solve.py [ciphertext.txt]")


def main() -> None:
    motto = "Never Assume Mist Is Benign"
    key = "".join(w[0] for w in motto.split())
    ct = find_ct().read_text().strip()
    print("key=", key)
    print(vigenere_decrypt(ct, key))


if __name__ == "__main__":
    main()
