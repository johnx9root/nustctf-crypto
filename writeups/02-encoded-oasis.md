# Encoded Oasis: Layers by a Windhoek Whiteboard

**Author:** John_x9  
**Difficulty:** Easy  
**Attachments:** `note.b32`  
**Theme:** Coast & Campus (Blind solves from Windhoek labs to the Skeleton Coast)

Near a dusty whiteboard on the Windhoek side of campus, someone left `note.b32` like a water bottle at a desert oasis. The name hints at Base32. The alphabet inside suggests something else. Peel until the memo reads like CyberSoc notes, not sand.

## Blind solve path

You only have `note.b32`. Start by inspecting characters, not by trusting the extension.

1. Open the file. You will see `A-Za-z0-9+/=`. That is Base64-shaped, not Base32’s `A-Z2-7`. Treat `.b32` as a coastal mirage.
2. Base64-decode the whole string. The result is printable ASCII that looks like a long hex dump: only `0-9a-f` characters.
3. Hex-decode that ASCII hex string. You get another Base64 blob (binary that is still Base64 text once viewed as Latin-1/ASCII).
4. Base64-decode again. Look at the first bytes. A zlib stream often starts with `78 9c` or a nearby header. That is your cue.
5. zlib-decompress. You should get a short UTF-8 memo:

```text
NUST CyberSoc layered memo:
nustCTF{l4y3rs_b34t_0n3_cl1ck}
```

Outer to inner stack, for your lab notebook:

1. Base64  
2. ASCII hex string  
3. Base64  
4. zlib of the memo  

CyberChef works the same way: From Base64, From Hex, From Base64, then Zlib Inflate (or Raw Inflate, depending on the build).

### Solve script

Save as `02-encoded-oasis-solve.py` (also under `writeups/solves/`).

```python
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
```

Run:

```bash
python3 02-encoded-oasis-solve.py note.b32
```

## Flag

`nustCTF{l4y3rs_b34t_0n3_cl1ck}`

## After the event: vulnerable construction and how to fix

**Learning only.** Not required for the blind solve.

### How this was built

The author wrote a short CyberSoc memo containing the flag, zlib-compressed it, Base64-encoded that blob, hex-encoded the Base64 text as ASCII hex, then Base64-encoded the hex string once more. The file was named `note.b32` on purpose so a single decode click fails. Encoding is not encryption; every layer is reversible without a key.

### Why it is weak

Nested encoding raises effort slightly and teaches tooling discipline. It does not provide confidentiality. Anyone who peels layers in order recovers the plaintext. Misleading extensions are a social trap, not a cryptographic one.

### Secure coding / crypto hygiene

- Never “protect” secrets by Base64, hex, zlib, or any stack of reversible encodings. Attackers decode just like students do.
- Use real crypto with keys stored outside the blob (KMS, sealed secrets, OS keyring). Prefer AEAD so tampering is detected.
- Name files honestly in production pipelines. Misleading extensions break scanners and confuse incident response.
- If you need compression plus transport encoding (for example zlib then Base64 in a JSON field), document the stack; do not treat it as a vault.
