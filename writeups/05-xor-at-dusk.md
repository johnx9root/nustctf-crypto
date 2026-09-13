# XOR at Dusk: Repeating Key Over the Dunes

**Author:** John_x9  
**Difficulty:** Beginner  
**Attachments:** `ciphertext.hex`  
**Theme:** Coast & Campus (Blind solves from Windhoek labs to the Skeleton Coast)

As the sun drops toward the Skeleton Coast, a sticky note on a Swakopmund-bound laptop shows only hex. Rumour on campus says a short repeating key (a few bytes) mixed the bytes, and the plaintext still carries the usual `nustCTF{` prefix like a lantern in the dusk.

## Blind solve path

You only have `ciphertext.hex`. Decode hex to raw bytes first.

```text
0006180f53050b070e5e530511001f27272d1f015814405f102c1354013407015a060e
```

1. `ct = bytes.fromhex(...)`.
2. This is **not** single-byte XOR. Brute-forcing one key byte will not clean the whole string. Expect a repeating key of length 2, 3, or 4.
3. Use the known crib `nustCTF{`. Slide it across every offset in the ciphertext. At offset `o`, compute a candidate keystream fragment:
   `ks[i] = ct[o + i] XOR crib[i]` for `i` in `0 .. len(crib)-1`.
4. Keep a fragment only if it is consistent with a repeating key of your guessed period `p`: `ks[i] == ks[i % p]` for all `i` in the fragment.
5. Extend that phased keystream across the full ciphertext, XOR, and check for printable ASCII containing `nustCTF{` and a closing `}`.

Recovered parameters for this attachment:

- period `3`
- key aligned to index 0: `dsk` (`b'dsk'`)
- plaintext:

```text
dusk note: nustCTF{r3p34t_x0r_cr1b}
```

Once you know the key, CyberChef **XOR** with UTF8 `dsk` in repeating mode also works. Getting there without the crib is harder; with the flag prefix it is a clean lab exercise.

### Solve script

Save as `05-xor-at-dusk-solve.py` (also under `writeups/solves/`).

```python
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
```

Run:

```bash
python3 05-xor-at-dusk-solve.py ciphertext.hex
```

## Flag

`nustCTF{r3p34t_x0r_cr1b}`

## After the event: vulnerable construction and how to fix

**Learning only.** Not required for the blind solve.

### How this was built

Plaintext `dusk note: nustCTF{r3p34t_x0r_cr1b}` was XOR-encrypted under a repeating 3-byte key `dsk`, then hex-encoded for the sticky-note attachment. The flag prefix was left in the plaintext on purpose so crib dragging recovers the keystream period.

### Why it is weak

Repeating-key XOR is many-time-pad territory. A known plaintext prefix the length of (or longer than) the key period leaks the key directly. Even without a crib, short keys fall to frequency analysis and Hamming-distance key-length guesses (Friedman / Kasiski-style ideas adapted to bytes).

### Secure coding / crypto hygiene

- Do not XOR with a short repeating password for confidentiality. That is a teaching toy, not a cipher suite.
- Use a proper stream cipher or AEAD where the keystream is driven by a nonce/key and never reused across messages with the same nonce.
- Never ship predictable plaintexts (fixed headers, `nustCTF{`, `Cookie:`) under broken XOR if you care about secrecy; cribs are a gift to attackers.
- For local file protection, use established tools (age, age-encrypted archives, OS disk encryption) rather than hand-rolled XOR in a notebook script.
