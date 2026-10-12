# Music Security Department

**Category:** Rev | **Points:** 499 (17 solves) | **Flag:** `csaw{~i_love_my_computer_&_it_loves_me~<3}`

## Challenge

A fake DJ "CDJ" deck built as a **Purr-Data** music patch that answers on a patch port. You have to
"heist" a sealed flag stem out of it. 499 points, 17 solves — a brutal rev.

## Initial Analysis

The distributable (`csirac.zip`) is a Purr-Data / Pd (Pure Data) patch, plus some decoy native
binaries (`csirac.pd_linux` ELF, `csirac.dll` PE) that are red herrings — "they will not lead to the
flag." The real logic is inside the `.pd` patch itself.

Dumping the patch and its runtime state (`extracted/session.bin` = the VM's RAM+ROM,
`extracted/csirac.pd` = the boot patch) reveals that the patch implements a **custom bytecode virtual
machine**. The deck's commands are opcodes; the interesting one is `EXPORT`.

## The Vulnerability / Core Concept

`EXPORT` is a **keystream cipher**: it emits the flag stem XOR'd (streamed) against a key derived
from a 6-byte secret. There's no leak of the key, so:

1. **Emulate** the Pd bytecode VM (`run/emu2.py`) to understand `EXPORT`'s transform.
2. **Brute-force the 6-byte key** (`run/brute_full.py`), decrypting the exported body under each candidate.
3. **Filter by English** — keep the single candidate whose decrypted body reads as real,
   grammatical English. That uniquely identifies the correct key.

The validated ritual ended up being `KEY bf03942fbd12` / `EXPORT 9a3f000000`.

## Exploitation

```bash
python3 run/emu2.py          # emulate the Pd bytecode VM to model EXPORT
python3 run/brute_full.py    # brute the 6-byte key, keep the English-readable plaintext
python3 solve.py             # end-to-end: emulate -> brute -> decrypt flag stem
```

## Flag

```
csaw{~i_love_my_computer_&_it_loves_me~<3}
```

## Key Takeaways

- A "music patch" can hide a full **bytecode VM** — treat an unfamiliar scripting environment (Pd,
  here) as a CPU and write an emulator for it.
- When a key is small (6 bytes) and the plaintext is natural language, **brute + English-ness filter**
  beats any cleverness.
- Ignore planted decoy binaries that don't carry the real logic.

## Files

- `solve.py` — end-to-end emulate → brute → decrypt.
- `run/emu2.py` — the Pd bytecode VM emulator.
- `run/brute_full.py` — 6-byte key brute-forcer with English filter.
- `extracted/session.bin` — the VM RAM+ROM image.
- `extracted/csirac.pd` — the boot patch.
- `csirac.zip` — the original challenge distributable.
