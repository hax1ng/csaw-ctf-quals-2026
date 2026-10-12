# Taking on the Temple

**Category:** Crypto | **Flag:** `csaw{tH3_c0fF3r_w4s_n3v3r_th3_gU4rd1an}`

## Challenge

A Flask "vault" web app themed as a temple you have to break into. The server hands
you a chain of artifacts (`stone.json`, `frost.bin`, `iron.json`, `vault.json`) and a
primer, and expects you to peel back several layers of encryption in the right order
before the final coffer opens and the session flips to `"won": true`.

## Initial Analysis

Reading `app/app.py` + `app/artifacts.py` shows the vault is a staged puzzle. Each stage
emits a labelled marker (`GRANITE-…`, `CRYO-…`, `FERRUM-…`) that is the key material for
the next stage. The layers, in order:

1. **Braille primer** — the first clue is Braille, which decodes to the seed phrase.
2. **Vigenère (plaintext autokey)** — the "Stone" layer is a classic autokey cipher where
   the key extends itself with the recovered plaintext.
3. **SHA-256 keystream (CTR-style) XOR** — the "Frost" and "Iron" layers XOR the data
   against a keystream of `SHA256(key || counter)` blocks.
4. **AES-GCM** — the final `vault.json` is AES-GCM; the key is derived from the markers
   collected across the previous stages.

## The Core Concept

Nothing here is a single exotic bug — it's a **chained-decryption puzzle**. The trick is
recognising each primitive from its structure (Braille dots → autokey's self-extending key
→ a SHA-256 counter keystream → an AES-GCM blob with a 12-byte nonce and 16-byte tag) and
feeding each stage's output into the next. The GCM tag at the end is the correctness oracle:
it only authenticates if every earlier marker was recovered exactly right.

## Exploitation

`solve.py` walks the whole chain end-to-end against the hosted artifacts in `challenge/hosted_data/`:

```bash
python3 solve.py hosted_data
```

It decodes the Braille primer, runs the autokey decrypt to recover `k1=GRANITE-992220037417`,
rebuilds the SHA-256 keystreams to recover `k2=CRYO-664128208716` and `k3=FERRUM-345246166574`,
derives the AES-GCM key from those markers, and decrypts `vault.json` to the flag. A valid GCM
tag confirms the solve (the live session recorded `"won": true`).

## Flag

```
csaw{tH3_c0fF3r_w4s_n3v3r_th3_gU4rd1an}
```

## Key Takeaways

- Multi-stage crypto challenges are about **primitive recognition**: learn to spot an autokey
  cipher, a hash-based keystream, and an AEAD blob by shape alone.
- An AEAD tag (GCM) is a free correctness check — if it verifies, every upstream key was right.

## Files

- `solve.py` — full chained solver (Braille → autokey → SHA-256 CTR → AES-GCM).
- `challenge/` — the challenge Flask app (`app.py`, `artifacts.py`) and the hosted artifacts.
