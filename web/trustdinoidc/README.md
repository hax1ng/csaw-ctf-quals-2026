# TrustDinOIDC

**Category:** Web | **Points:** 299 (185 solves) | **Flag:** `csaw{str4ta_sk1pped_th3_p1n}`

## Challenge

A dinosaur-poster portal protected by **OIDC**. Printing the "Flagosaurus" is admin-only; you need
the `flagosaurus:redeem` scope, which you're not supposed to be able to grant yourself.

## Initial Analysis

There are two identity providers in play — `PaleoID` (the real root of trust) and `StrataID` (a
second path). JWTs are validated using the **`x5c`** header (an embedded X.509 certificate chain).

The bug is in how **StrataID validates the chain**: it does **name-only** validation — it checks the
leaf certificate's *issuer field* and *CN* strings, but **never verifies the leaf's signature**
against the PaleoID root. (The flag spells it out: "strata skipped the pin" — StrataID skipped
certificate pinning / signature verification.)

## The Vulnerability

**JWT `x5c` certificate-chain injection.** Because StrataID only matches names:

1. Generate a self-signed leaf certificate whose **issuer field claims the PaleoID root** (and the
   right CN).
2. Embed that leaf in the JWT's `x5c` header and sign the token with the matching private key.
3. StrataID sees the "correct" issuer/CN name, skips the signature check, and trusts the token — so
   you can forge a token carrying the `flagosaurus:redeem` scope.

## Exploitation

`solve.py` builds the forged cert + JWT and drives the OAuth flow end-to-end:

```bash
python3 solve.py        # forge x5c leaf -> signed JWT w/ flagosaurus:redeem -> redeem -> flag
```

(`forge.py` / `forge2.py` / `confusion.py` are the cert/token-forging helpers used while developing
the final `solve.py`.)

## Flag

```
csaw{str4ta_sk1pped_th3_p1n}
```

## Key Takeaways

- **Name matching is not signature verification.** Trusting a cert because its issuer *field* says
  the right thing — without cryptographically verifying the chain — is a total auth bypass.
- The `x5c` JWT header is dangerous: if the server trusts attacker-supplied certs, you can sign your
  own tokens. Pin to known keys / verify the full chain to a trusted root.

## Files

- `solve.py` — end-to-end `x5c` chain-injection OAuth exploit.
- `forge.py`, `forge2.py`, `confusion.py` — cert/JWT forging helpers.
