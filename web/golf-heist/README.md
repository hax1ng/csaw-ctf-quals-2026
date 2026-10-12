# Golf Heist

**Category:** Web | **Flag:** `csaw{el3gant_sw1ng_n3ver_c4ught}`

## Challenge

A FastAPI "Golf Heist" vault app. In production it sits behind a **Caddy** reverse proxy that uses
`forward_auth` for authentication. The flag comes from the `FLAG` env var, served only to admins at
`/api/vault/admin-item`.

## Initial Analysis

Reading `app/main.py` (and the embedded Caddyfile snippet) shows the trust model:

- Caddy runs a `forward_auth` sub-request to an auth service, which sets identity **headers** (like
  `X-User-Role`) that the backend then trusts.
- The backend reads `X-User-Role` to decide if you're admin.

The classic Caddy `forward_auth` mistake (**GHSA-7r4p-vjf4-gxv4**): if the proxy doesn't strip
client-supplied copies of those headers, a user can just **send `X-User-Role: admin` themselves** and
the backend believes it.

## The Vulnerability

Two parts:

1. **Header-injection privilege escalation** — supply `X-User-Role: admin` directly to reach the
   admin-only vault endpoint.
2. **The vault phrase** — the admin item is gated by a phrase computed from leaked **Enigma rotor**
   hints exposed by the app; reconstruct the Enigma settings to compute the phrase.

## Exploitation

`solve.py` leaks the rotor hints, computes the Enigma phrase, and requests the admin item with the
forged role header:

```bash
python3 solve.py https://golf-heist.ctf.csaw.io
# -> GET /api/vault/admin-item  with header  X-User-Role: admin
```

## Flag

```
csaw{el3gant_sw1ng_n3ver_c4ught}
```

## Key Takeaways

- **Never trust identity headers from the client** behind `forward_auth`. The proxy must *strip*
  inbound `X-User-*` headers or the auth is cosmetic (GHSA-7r4p-vjf4-gxv4).
- Auth bypass + a secondary crypto puzzle (Enigma) is a common "two-stage web" pattern — solve the
  access control first, then the content gate.

## Files

- `solve.py` — rotor leak → Enigma phrase → forged-header admin request.
- `app/` — the FastAPI challenge source (incl. the Caddy `forward_auth` config).
- `Dockerfile`, `requirements.txt` — deployment context.
