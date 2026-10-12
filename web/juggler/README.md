# Juggler

**Category:** Web | **Points:** 468 (75 solves) | **Flag:** `csaw{tw0_f0r_0n3_2gc9w2hz}`

## Challenge

> Juggling — the act of tossing and catching two or more **mass**es where at least one is
> **assign**ed...

A PHP app. The flavour text bolds the hint: **mass assignment** + **type juggling**.

## Initial Analysis

Reading the source (`challenge/src/`):

- **`profile_update.php`** takes a JSON body and writes its fields straight into the session —
  including fields you shouldn't control. That's **mass assignment**: send `{"role": true}` and it
  lands in `$_SESSION['role']`.
- **`public/admin.php`** checks admin with `in_array($_SESSION['role'], $adminRoles)` — using the
  **non-strict** (loose) comparison.

## The Vulnerability

Two PHP footguns chained:

1. **Mass assignment** — `profile_update.php` lets you set `role` directly in the session.
2. **PHP loose comparison** — `in_array($x, $arr)` without the `true` third argument uses `==`.
   In PHP, `true == "admin"` (any non-empty string) is **true**. So setting `role` to the boolean
   `true` matches *every* entry in `$adminRoles`, passing the admin check.

Flow: register → login → `profile_update` with `{"role": true}` → read the admin page → flag.

## Exploitation

```bash
python3 exploit.py        # register -> login -> profile_update {"role":true} -> admin_read -> flag
```

## Flag

```
csaw{tw0_f0r_0n3_2gc9w2hz}
```

(The packaged `source/flag.txt` in the distribution is a `csaw{test_flag}` placeholder — the real
flag comes from the live admin endpoint.)

## Key Takeaways

- **Mass assignment**: never bind a request body wholesale into trusted state — allowlist fields.
- **PHP type juggling**: `in_array`/`==` without strict mode is exploitable; `true == "anystring"`.
  Always use `in_array($x, $arr, true)` / `===`.

## Files

- `exploit.py` — the register → mass-assign → admin chain.
- `challenge/` — the PHP app source (`src/profile_update.php`, `public/admin.php`, config, Dockerfile).
