# Petite Modulus: Tiny RSA in a NUST Lab Demo

**Author:** John_x9  
**Difficulty:** Beginner  
**Attachments:** `n.txt`, `e.txt`, `c.txt`, `params.txt`  
**Theme:** Coast & Campus (Blind solves from Windhoek labs to the Skeleton Coast)

A NUST lab RSA demo went wrong the way desert roads go soft after rain: the modulus looks serious until you count the bits. About forty bits of `n` will not hide a flag from a short script, and the message was too long for one block anyway.

## Blind solve path

You get four files. `params.txt` restates the same public values for convenience.

Typical contents:

- `n.txt`: `10076212377367` (here about 44 bits; still trivial to factor)
- `e.txt`: `65537`
- `c.txt`: one ciphertext integer per line (six blocks)
- `params.txt`: the same `n`, `e`, and `c` list annotated

Steps a player can follow without organizer notes:

1. Read `n`, `e`, and every line of `c` as integers.
2. Factor `n = p * q`. Options that work on a laptop: trial division, Pollard's Rho, sympy/`factorint`, or paste `n` into FactorDB. You should get factors on the order of millions (this instance: `p = 2766487`, `q = 3642241`).
3. Compute `phi = (p - 1) * (q - 1)` and `d = inverse(e mod phi)`. In Python 3.8+: `d = pow(e, -1, phi)`.
4. For each ciphertext block `c_i`, compute `m_i = pow(c_i, d, n)`.
5. Convert each nonzero `m_i` to big-endian bytes (`m.to_bytes((m.bit_length() + 7) // 8, "big")`) and concatenate. The joined plaintext is the flag string.

You should recover:

```text
nustCTF{f4ct0r_th3n_d3crypt}
```

Single-block “RSA decrypt” gadgets without factors will stall. Factor first, then decrypt every line.

### Solve script

Save as `04-petite-modulus-solve.py` (also under `writeups/solves/`). Point it at the directory that holds `n.txt`, `e.txt`, and `c.txt`.

```python
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
```

Run:

```bash
python3 04-petite-modulus-solve.py /path/to/files
```

## Flag

`nustCTF{f4ct0r_th3n_d3crypt}`

## After the event: vulnerable construction and how to fix

**Learning only.** Not required for the blind solve.

### How this was built

Two small primes (`p ≈ 2.77e6`, `q ≈ 3.64e6`) were multiplied to form `n ≈ 1.01e13`. Public exponent `e = 65537`. The flag bytes were split into chunks that fit under `n` as big-endian integers (max about 5 bytes per block here), each encrypted as `c = m^e mod n`, and written one integer per line in `c.txt`. No padding scheme: textbook RSA on raw message chunks.

### Why it is weak

- Tiny moduli factor in milliseconds. Modern RSA needs large primes (2048-bit `n` as a historical minimum; prefer 3072+ where policy still allows RSA).
- Textbook RSA without padding is malleable and unsafe even with a large `n`.
- Multi-block raw RSA without a proper mode still leaks structure and invites foot-guns.

### Secure coding / crypto hygiene

- Generate RSA keys with a vetted library (`cryptography`, OpenSSL) and reject toy bit lengths in config.
- Use OAEP for encryption and PSS for signatures; never raw `m^e mod n` on application data.
- Prefer modern KEMs and AEAD (for example X25519 + ChaCha20-Poly1305, or libsodium secretbox) unless you must speak RSA for interoperability.
- Never commit private primes or `d` next to public challenge files in real systems; this lab kept secrets only in organizer-side notes.
- If a demo must use a small `n`, label it “breakable on purpose” and keep it off production networks.
