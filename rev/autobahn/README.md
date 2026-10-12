# Autobahn

**Category:** Rev | **Points:** 92 (263 solves) | **Flag:** `csaw{c0d3_th4t_rewr1t3s_1ts3lf_c4nt_b3_tru5t3d}`

## Challenge

> Our engine only fires with the right password.

A small ELF (`nitro`). Opening it in a disassembler, the key function is pure garbage — it only
makes sense at runtime.

## Initial Analysis

Static disassembly of the password check shows noise, not instructions. That, plus a dedicated
section (`enccode`), is the fingerprint of **self-modifying code (SMC)**: the real bytes are
encrypted on disk and decrypted into memory just before execution.

Looking at `main`, before it calls the check it:

- `mprotect`s the `enccode` section as **RWX**, then
- **XOR-decrypts** `secret_check` in place with an 8-byte key: `13 37 c0 de ba ad f0 0d` (a cute
  `1337c0de baadf00d`).

## The Vulnerability / Core Concept

**Self-modifying code.** The disassembler can't show you the real logic because it isn't there until
runtime. Two ways to beat it:

1. **Dynamic:** break *after* the `mprotect`/XOR loop in a debugger and dump the now-decrypted section.
2. **Static:** replicate the XOR with the key `1337c0debaadf00d` to produce a decrypted copy, then
   disassemble that.

The decrypted `secret_check` builds the password `n2o_boost` and derives the flag from it.

## Exploitation

```bash
# static approach: XOR-decrypt the enccode section with 13 37 c0 de ba ad f0 0d,
# then disassemble -> recover password "n2o_boost" -> binary prints the flag
./nitro
# password: n2o_boost
```

## Flag

```
csaw{c0d3_th4t_rewr1t3s_1ts3lf_c4nt_b3_tru5t3d}
```

## Key Takeaways

- When a function disassembles to **noise next to an `mprotect`/XOR loop**, suspect self-modifying code.
- Either dump the decrypted bytes at runtime, or reproduce the decryption statically — both recover
  the real logic. (The flag literally says it: code that rewrites itself can't be trusted.)

## Files

- `nitro` — the challenge binary (self-modifying password check).
