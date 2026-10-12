# CSALE

**Category:** Web | **Points:** 487 (49 solves) | **Flag:** `csawctf{TH4ts_R0ugH_B4dDy}`

> Flag wrapper note: CSALE uses `csawctf{...}` (confirmed in-challenge), unlike most of this event's `csaw{...}` flags.

## Challenge

"CSAW Store" — a Flask marketplace in "beta." The flag is locked behind a seller account's
**unlisted** section, which needs a 4-digit PIN.

## Initial Analysis

Reading the app source (`challenge/main.py`, `challenge/vault.py`):

- Listing search is built with string-concatenated SQL → **UNION SQL injection**.
- The app stores an **XOR-"encrypted" password vault** in the DB (recoverable once you can read it).
- The unlisted/seller area is gated by a **4-digit PIN**, and the per-session attempt counter is
  stored **inside the session cookie**.

There's also an **anti-AI honeypot**: a decoy flag `csawctf{Th1s_1S_4asy_r1gh1!?}` is planted to
catch automated solvers. Avoid it.

## The Vulnerability

A three-step chain:

1. **UNION SQLi** → dump the XOR-encrypted password vault.
2. **Decrypt the vault** (XOR) → log in as seeded users (e.g. the flag-holding seller).
3. **PIN brute** → because the attempt counter lives in the cookie, replaying a **pristine
   pre-attempt cookie** on every request resets the counter, so all 10,000 PINs can be tried.

## Exploitation

```bash
# 1-2: UNION SQLi dump + XOR-decrypt handled during recon -> seller creds
# 3: brute the 4-digit unlisted PIN by replaying a clean session cookie each try
python3 pin_brute.py http://<HOST>:5000
```

`pin_brute.py` logs in, then threads through PINs, clearing/replaying the pristine session cookie so
the server-side counter never advances. The hit unlocks the unlisted section → real flag.

## Flag

```
csawctf{TH4ts_R0ugH_B4dDy}
```

(Avoid the honeypot `csawctf{Th1s_1S_4asy_r1gh1!?}`.)

## Key Takeaways

- **Client-side state is attacker-controlled.** An attempt counter stored in the cookie is no
  rate-limit at all — reset it by replaying a clean cookie.
- UNION SQLi → credential vault → authenticated feature is a very common real-world-ish chain.
- Watch for **anti-AI honeyflags** — a too-easy flag string in plain sight is usually a trap.

## Files

- `pin_brute.py` — threaded PIN brute using pristine-cookie replay.
- `challenge/` — the Flask store source (`main.py`, `vault.py`, templates).
