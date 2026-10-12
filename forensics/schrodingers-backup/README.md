# Schrödinger's Backup

**Category:** Forensics | **Points:** 500 | **Flag:** `csaw{th3_c4t_c0mm1tt3d_but_th3_j0urn4l_r3m3mb3r5}`

## Challenge

Recover an AES-256-GCM "time capsule" whose key is derived from the **ordered history of visit
tokens**. The catch: that history lives only in an *uncheckpointed SQLite WAL* (write-ahead log),
and the WAL is deliberately salted with traps — baseline state, an uncommitted transaction, and
residue from an older generation. You have to replay exactly the real committed visits, in order.

## What We're Given

`evidence.zip` → a SQLite database (`catalog.db`), its WAL (`catalog.db-wal`), and the encrypted
`capsule.json` (nonce + ciphertext).

## Initial Analysis

SQLite's WAL stores page-level frames. A frame "counts" only if it's part of a valid, *committed*
transaction. The WAL header has a salt (`salt1`/`salt2`) and a seed checksum; every frame carries
its own salt + a running checksum chained from the header. So we can mechanically separate the
real history from the traps:

- **salt mismatch** → frame belongs to an older WAL generation (residue) → ignore.
- **checksum breaks the running chain** → corrupt/forged → stop.
- **`dbsize != 0`** in the frame header → this frame is a **commit**.

## The Core Concept

The whole challenge is **SQLite WAL forensics**. Walk the frames while maintaining the running
checksum seeded from the header. Replay each valid frame onto the base DB pages; at every commit,
snapshot the DB and read the current visit token (`north.share XOR south.share`), but only record
it when `control.armed == 1`. Concatenate the recorded tokens in order, `SHA-256` them with a
domain-separation string, and that's the AES-256-GCM key.

The GCM auth tag is the proof you got it right — one wrong/extra/missing token and `decrypt`
throws `InvalidTag`.

## Exploitation

The solve is a three-stage pipeline (run from the challenge dir after `unzip evidence.zip`):

```bash
unzip evidence.zip -d evidence
python3 work/walparse.py      # parse + checksum-validate WAL frames  -> work/frames.pkl
python3 work/reconstruct.py   # replay valid frames, collect armed visit tokens -> work/tokens.pkl
python3 solve.py              # SHA-256 key derivation + AES-GCM decrypt -> flag
```

`solve.py` derives `key = SHA256(DOMAIN + b"".join(tokens))` and GCM-decrypts the capsule.

## Flag

```
csaw{th3_c4t_c0mm1tt3d_but_th3_j0urn4l_r3m3mb3r5}
```

## Key Takeaways

- A SQLite `-wal` file is a goldmine: committed vs. uncommitted vs. stale state is all recoverable
  from the salt + checksum chain.
- AEAD tags double as a solver's correctness oracle — if GCM verifies, your reconstruction is exact.

## Files

- `solve.py` — key derivation + GCM decrypt.
- `work/walparse.py` — WAL frame parser + checksum validator.
- `work/reconstruct.py` — frame replay + ordered token collection.
- `evidence.zip` — the challenge DB, WAL, and encrypted capsule.
