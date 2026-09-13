# Vigenère Trail: Acronym on the Windhoek Ridge

**Author:** John_x9  
**Difficulty:** Easy  
**Attachments:** `ciphertext.txt`  
**Theme:** Coast & Campus (Blind solves from Windhoek labs to the Skeleton Coast)

Outside Windhoek, trail markers read like a repeating-keyword cipher: Vigenère, the old polyalphabetic workhorse. There is no `key.txt` in the pack. The ranger’s tip is a motto; the dunes keep the rest.

## Blind solve path

You have `ciphertext.txt` and the challenge text’s motto. That is enough.

Ciphertext:

```text
GHQ NMNG UA ohsfKUS{4cd0vzz_uzt0dxs_h1o}
```

Motto from the brief:

```text
Never Assume Mist Is Benign
```

1. Build the key as the **first letter of each word**: `N` `A` `M` `I` `B` → **`NAMIB`**. Fitting for a Namibia-flavored campus trail.
2. Decrypt with classic Vigenère: for each alphabetic ciphertext letter, subtract the matching key letter’s alphabet index mod 26. Preserve case from the ciphertext. Advance the key index only when you process a letter; digits, braces, and spaces stay unchanged and do not consume key material.
3. You should land on readable English plus the flag:

```text
THE FLAG IS nustCTF{4cr0nym_unl0cks_v1g}
```

CyberChef: paste the ciphertext, **Vigenère Decode**, key `NAMIB`.

### Solve script

Save as `03-vigenere-trail-solve.py` (also under `writeups/solves/`).

```python
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
```

Run:

```bash
python3 03-vigenere-trail-solve.py ciphertext.txt
```

## Flag

`nustCTF{4cr0nym_unl0cks_v1g}`

## After the event: vulnerable construction and how to fix

**Learning only.** Not required for the blind solve.

### How this was built

The plaintext `THE FLAG IS nustCTF{4cr0nym_unl0cks_v1g}` was Vigenère-encrypted under the repeating keyword `NAMIB`. The motto was published in the challenge description so the acronym reconstruction is part of the puzzle. Non-letters in the flag body were left alone, and the key pointer skipped them, which matches common CTF Vigenère helpers.

### Why it is weak

Short dictionary-like keys (especially geographic acronyms) fall to crib dragging, Kasiski, or simply reading the prompt carefully. Vigenère is not modern crypto. Publishing the motto beside the ciphertext is intentional for teaching, disastrous for secrecy.

### Secure coding / crypto hygiene

- Do not use Vigenère, Beaufort, or other classical polyalphabetics to hide real credentials or tokens.
- Never derive production keys from mottos, slogans, or public campus phrases. Use a CSPRNG and store keys in a proper secret store.
- If you need password-based keys, use a memory-hard KDF (Argon2id, scrypt) with a unique salt, not an acronym.
- Challenge authors: keep “key from story text” as a CTF mechanic only; document it in the after-party notes so juniors do not copy the pattern into apps.
