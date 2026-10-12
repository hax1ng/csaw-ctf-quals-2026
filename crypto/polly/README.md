# Polly

**Category:** Crypto | **Points:** 338 (166 solves) | **Flag:** `csaw{Am4Z3s_m3_thE_W1lL_0f_1nst1nct}`

## Challenge

> Isn't me, find the seed

A network service encrypts data with ChaCha20. Part of the nonce is generated from a 64-bit
xorshift PRNG, and the server leaks a single bit of information about the PRNG state on every
query. ("Polly" = the parrot that repeats you; "find the seed" is the literal goal.)

## Initial Analysis

Reading `challenge/main.py`:

- The 64-bit xorshift state is advanced per request.
- Each query leaks the **low byte** of `T^x(seed)` — i.e. a known linear function of the seed
  bits over GF(2).
- The ChaCha20 **nonce suffix** is derived from that same PRNG state, and the flag is encrypted
  once with a nonce whose suffix we can predict if we know the seed.

## The Core Concept

xorshift is **entirely linear over GF(2)**. Every leaked bit is a linear equation in the 64
unknown seed bits. Collect ≥ 64 independent equations and solve the system with Gaussian
elimination — the seed drops straight out, no brute force on 2⁶⁴ needed.

Once the seed is known you can roll the PRNG forward, reconstruct the exact nonce used for the
flag ciphertext, regenerate the ChaCha20 keystream, and XOR the flag back out.

## Exploitation

`solve.py` automates the whole thing:

1. Query the oracle until the recovered linear system reaches **rank 64**.
2. Solve over GF(2) → seed `0xd1163367e40e697a`.
3. Search the 24-bit nonce-suffix space for the collision that matches the flag ciphertext's nonce.
4. Rebuild the ChaCha20 keystream and XOR out the flag.

```bash
python3 solve.py          # local mode checks rank before sending each request
```

## Flag

```
csaw{Am4Z3s_m3_thE_W1lL_0f_1nst1nct}
```

## Key Takeaways

- **Any LFSR/xorshift PRNG is linear** — leaked bits become a GF(2) linear system you solve directly.
- Never derive a nonce from a weak/recoverable PRNG. Nonce reuse (or nonce *prediction*) turns a
  stream cipher into plaintext XOR.

## Files

- `solve.py` — GF(2) seed recovery + nonce search + keystream XOR.
- `challenge/` — the challenge service source (`main.py`) and Docker packaging.
