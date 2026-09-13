#!/usr/bin/env python3
"""Petite Modulus: factor ~40-bit n (Pollard Rho), decrypt multi-block RSA."""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path


def pollard_rho(n: int) -> int:
    if n % 2 == 0:
        return 2
    while True:
        x = random.randrange(2, n - 1)
        y = x
        c = random.randrange(1, n - 1)
        d = 1
        while d == 1:
            x = (x * x + c) % n
            y = (y * y + c) % n
            y = (y * y + c) % n
            d = math.gcd(abs(x - y), n)
        if d != n:
            return d


def factor(n: int) -> tuple[int, int]:
    if n % 2 == 0:
        return 2, n // 2
    for i in range(3, 100_000, 2):
        if i * i > n:
            break
        if n % i == 0:
            return i, n // i
    p = pollard_rho(n)
    return p, n // p


def find_files_dir() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    here = Path(__file__).resolve().parent
    candidates = [
        Path("."),
        here,
    ]
    for d in candidates:
        if (d / "n.txt").is_file() and (d / "c.txt").is_file():
            return d
    raise SystemExit("usage: 04-petite-modulus-solve.py [dir with n.txt e.txt c.txt]")


def main() -> None:
    base = find_files_dir()
    n = int((base / "n.txt").read_text())
    e = int((base / "e.txt").read_text())
    blocks = [
        int(line)
        for line in (base / "c.txt").read_text().splitlines()
        if line.strip()
    ]
    p, q = factor(n)
    d = pow(e, -1, (p - 1) * (q - 1))
    out = b""
    for c in blocks:
        m = pow(c, d, n)
        if m == 0:
            continue
        out += m.to_bytes((m.bit_length() + 7) // 8, "big")
    print(f"p={p} q={q}")
    print(out.decode())


if __name__ == "__main__":
    main()
