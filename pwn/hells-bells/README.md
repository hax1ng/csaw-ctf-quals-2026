# Hells Bells

**Category:** Pwn | **Points:** 368 (150 solves) | **Flag:** `csaw{wh3n_y0u_r34ch_th3_cr0ssr04ds_d0nt_turn_l3ft}`

## Challenge

A "thermite-charge" inventory manager (`thermite-charge`): plant / rewire / inspect / defuse charges.

> The quartermaster claims a defused charge is untouchable — it isn't. Get a shell.

**libc:** glibc 2.31 (pre-safe-linking).

## Initial Analysis

The hint points straight at the `defuse` operation. Defusing a charge frees its chunk but **leaves
the pointer live** — so a "defused" (freed) charge can still be inspected and rewired. Use-after-free
again, but the exploitation path differs from Diamond Dogs.

## The Vulnerability

1. **libc leak** — free a chunk into the **unsorted bin** and inspect it to leak a libc address.
2. **tcache poisoning** — on glibc 2.31 the tcache has **no safe-linking** (no pointer mangling), so
   you can overwrite a freed chunk's `fd` to point the tcache freelist at an arbitrary address. Aim
   it at **`__free_hook`**.
3. Allocate over `__free_hook`, write `system` into it, then `defuse` a chunk whose contents are
   `/bin/sh` → `free("/bin/sh")` becomes `system("/bin/sh")`.

## Exploitation

`solve.py` (pwntools):

```text
1. unsorted-bin leak              -> libc base
2. UAF + tcache fd overwrite      -> freelist -> &__free_hook
3. alloc __free_hook, set =system
4. free a "/bin/sh" chunk         -> system("/bin/sh") -> shell -> cat flag
```

```bash
python3 solve.py <HOST> <PORT>
```

## Flag

```
csaw{wh3n_y0u_r34ch_th3_cr0ssr04ds_d0nt_turn_l3ft}
```

## Key Takeaways

- **glibc 2.31 tcache has no safe-linking** — a single `fd` overwrite gives arbitrary allocation.
- `__free_hook = system` + a chunk containing `/bin/sh` is the cleanest UAF→shell primitive on that libc.

## Files

- `solve.py` — full pwntools UAF → tcache poison → `__free_hook` exploit.
- `thermite-charge` — the challenge binary (glibc 2.31).
