# Secret Treaties

**Category:** Crypto | **Points:** 175 (235 solves) | **Flag:** `csaw{LLL_turns_kn4ps4cks_1nt0_p4nc4k3s_wh3n_d3ns1ty_1s_l0w}`

## Challenge

> We built a "quantum-resistant" public-key scheme from the good old subset-sum problem.
> Subset-sum is NP-complete, so surely nobody can read our messages without the private key... right?
>
> We encrypted the flag nine bytes at a time. Each 72-bit block became a single number: the sum
> of the public-key entries selected by that block's bits. Recover the flag.

We get `pubkey.txt` (the weights) and `ciphertext.txt` (one sum per 9-byte block).

## Initial Analysis

"NP-complete so it's safe" is the trap. Subset-sum (knapsack) cryptosystems are famously broken
when the **density** is low:

```
density = n / log2(max_weight)
```

With 72 bits per block (`n = 72` weights selected) and large weights, the density here is around
**0.75** — comfortably inside the range where lattice reduction solves subset-sum exactly.

## The Core Concept

This is the classic **low-density subset-sum attack** (Lagarias–Odlyzko / Coster et al.). Build a
lattice whose short vectors correspond to the 0/1 selection vector, then run **LLL/BKZ** reduction;
the correct subset falls out as the shortest vector.

A nice optimisation: the plaintext is ASCII, so the **top bit of every byte is 0**. Dropping those
9 known-zero bits per block lowers the effective density from ~0.75 to ~0.656, making the lattice
reduce more reliably. The final (padded) block needed **BKZ-20** to crack.

## Exploitation

`solve.sage` builds the CJLOSS lattice per block and reduces it. Each recovered block is verified
by re-encrypting (summing the selected weights) and checking it matches the ciphertext exactly —
all 7 blocks verified.

```bash
# run on a machine with SageMath (the lattice reduction is heavy — give it RAM/CPU)
sage solve.sage
```

## Flag

```
csaw{LLL_turns_kn4ps4cks_1nt0_p4nc4k3s_wh3n_d3ns1ty_1s_l0w}
```

...which is also a hint: LLL flattens low-density knapsacks like pancakes.

## Key Takeaways

- **Subset-sum ≠ secure.** Compute the density first; if it's below ~0.9408, LLL breaks it.
- Exploit plaintext structure (ASCII high-bit zeros) to push the density down and make reduction robust.

## Files

- `solve.sage` — per-block low-density subset-sum lattice attack (LLL/BKZ).
- `pubkey.txt`, `ciphertext.txt` — the challenge public key and ciphertext.
