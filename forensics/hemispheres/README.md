# Hemispheres

**Category:** Forensics | **Points:** 50 (318 solves) | **Flag:** `csaw{0n3_f1l3_tw0_truth5_p0lygl0t_m4g1c}`

## Challenge

> We received an image. Just an image. Our analyst swears there's more to it, but every tool says
> it's a perfectly ordinary PNG... And even when you find the second thing, it's locked. The key
> was never written down.

One file: `the_signal.png`.

## Initial Analysis

It renders as a normal PNG, so `file` and image viewers are no help. But a PNG officially ends at
its `IEND` chunk — so look at what comes *after* it:

```bash
xxd the_signal.png | grep -A2 IEND      # bytes after IEND
binwalk the_signal.png                  # flags an appended ZIP
```

There's a `PK\x03\x04` ZIP signature appended after `IEND`. The file is a **PNG/ZIP polyglot**:
a valid PNG *and* a valid ZIP at once ("one file, two truths").

## The Core Concept

Two layers:

1. **Polyglot carving** — the appended archive (`tail.zip`) is a ZipCrypto-encrypted ZIP sitting
   past the PNG's `IEND`.
2. **LSB stego for the password** — the archive password "was never written down" because it's
   hidden in the image's **blue-channel least-significant bits**, length-framed (first bits give a
   length, then that many bytes of ASCII): `r3ad_b3tw33n_th3_p1x3ls`.

## Exploitation

`solve.py` carves the trailing ZIP, extracts the blue-channel LSB password, and decrypts the
archive (CRC32 verifies both members):

```bash
python3 solve.py
# recovered password: r3ad_b3tw33n_th3_p1x3ls
# -> extracted/flag.txt
```

## Flag

```
csaw{0n3_f1l3_tw0_truth5_p0lygl0t_m4g1c}
```

## Key Takeaways

- Always inspect the bytes **after `IEND`** (or `FFD9` for JPEG) — appended archives are a classic
  polyglot trick.
- "The key was never written down" is a tell for **LSB steganography** carrying the passphrase.

## Files

- `solve.py` — polyglot carver + blue-channel LSB extractor + ZipCrypto decrypt.
- `the_signal.png` — the PNG/ZIP polyglot.
- `tail.zip` — the carved encrypted archive.
