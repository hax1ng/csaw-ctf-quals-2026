# Finders Keepers!

**Category:** Crypto | **Points:** 212 (221 solves) | **Flag:** `csaw{y0u_@lw@ys_kn0w_wh3r3_t0_l00k}`

## Challenge

> I wanna steal everything, but I don't know where it is.... maybe this video can help?

We get a single file: `finderskeepers.mp4`.

## Initial Analysis

The video itself is a red herring — don't bother scrubbing frames. The hint ("I don't know
**where** it is") points at *metadata*, i.e. "where" you look. Dumping the container tags with
`exiftool` reveals a suspicious Base64 blob stuffed into the `Subject` metadata field:

```bash
exiftool finderskeepers.mp4
```

Base64-decoding that field gives a string that *looks* like a flag but is scrambled:
`esnp{...}` — the `esnp` is clearly `csaw` run through a substitution.

## The Core Concept

`csaw` → `esnp` is a **Vigenère shift**. Because we know the plaintext starts with `csaw{`,
this is a textbook known-plaintext attack: subtract the known prefix from the ciphertext to
recover the start of the key, which spells out `cantfindit` — matching the challenge's
"I don't know where it is" flavour text.

## Exploitation

```python
# pull the Base64 out of the MP4 Subject tag, decode, then Vigenère-decrypt
import base64
ct = base64.b64decode(subject_field).decode()
key = "cantfindit"
flag = "".join(
    chr((ord(c) - ord(k) + 26) % 26 + ord('a')) if c.isalpha() else c
    for c, k in zip(ct, itertools.cycle(key))
)
```

Decrypting with the recovered key `cantfindit` yields the flag.

## Flag

```
csaw{y0u_@lw@ys_kn0w_wh3r3_t0_l00k}
```

## Key Takeaways

- **Always check metadata** — `exiftool` on any media file is step zero. "Where to look" was the whole puzzle.
- Vigenère falls instantly to a known-plaintext attack when you know the flag prefix (`csaw{`).

## Files

- `finderskeepers.mp4` — the challenge file (flag hidden in the `Subject` metadata tag).
