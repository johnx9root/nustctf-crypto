# Desert Shift: Sealed Line on the Skeleton Coast

**Author:** John_x9  
**Difficulty:** Easy  
**Attachments:** `scroll.txt`  
**Theme:** Coast & Campus (Blind solves from Windhoek labs to the Skeleton Coast)

A scrap of parchment washed ashore near the Skeleton Coast reads almost like a campus archive note. Most of it is clear Namib prose. One sealed line between triple brackets looks alphabet-scrambled, as if only that strip rode the dunes.

## Blind solve path

You only have `scroll.txt`. Open it and read it like a field log.

```text
Welcome to the Skeleton Coast archive.
Most of this log is clear. Only the sealed line below was shifted.
[[[ZLJYLA: ubzaJAM{t1kks3_zo1ma_u0a_do0s3}]]]
End of parchment. Good hunting.
```

1. Notice the readable wrapper versus the gibberish inside `[[[` ... `]]]`. That contrast is the whole puzzle. Do not Caesar-shift the entire file; the outer sentences are already plaintext and will turn into noise if you do.
2. Extract only the sealed segment:
   `ZLJYLA: ubzaJAM{t1kks3_zo1ma_u0a_do0s3}`
3. Treat that string as a classic Caesar ciphertext: letters A-Z and a-z move through the alphabet; digits, braces, underscores, spaces, and colons stay put.
4. There are only 26 shifts. Brute-force decrypting with shift `0..25` (or equivalently encrypt with `0..25` and look the other way) until you see the flag prefix `nustCTF{`.

Working decrypt finds **shift 7** (encrypt +7, decrypt by subtracting 7 mod 26). The sealed plaintext becomes:

```text
SECRET: nustCTF{m1ddl3_sh1ft_n0t_wh0l3}
```

### Solve script

Save as `01-desert-shift-solve.py` (also under `writeups/solves/`). Put `scroll.txt` beside it, or pass the path as argv.

```python
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
```

Run:

```bash
python3 01-desert-shift-solve.py scroll.txt
```

## Flag

`nustCTF{m1ddl3_sh1ft_n0t_wh0l3}`

## After the event: vulnerable construction and how to fix

**Learning only.** Not required for the blind solve.

### How this was built

The generator left the Skeleton Coast framing text in clear. It applied a single Caesar shift of **7** only to the middle payload (the `SECRET: ...` line), then wrapped that ciphertext in `[[[` `]]]` markers so players could find the sealed strip. Digits and punctuation in the flag were left untouched, which is normal for letter-only classical ciphers and also makes the `nustCTF{` shape recognizable once the letters land.

### Why it is weak

Caesar has a 26-element keyspace. Partial application does not harden the cipher; it only teaches students to scope transforms carefully. Markers like `[[[` `]]]` further advertise where the secret lives.

### Secure coding / crypto hygiene

- Do not use classical monoalphabetic shifts for confidentiality. Prefer authenticated encryption (for example AES-GCM or ChaCha20-Poly1305) with a proper key.
- If you must obfuscate a demo string for a classroom, say so explicitly; do not ship “shifted middle third of a config file” as a security control.
- Avoid wrapping secrets in obvious delimiters in production logs. Prefer structured redaction and secret managers.
- When teaching CTF-style puzzles, keep the toy cipher in the challenge attachment, not in real campus services.
