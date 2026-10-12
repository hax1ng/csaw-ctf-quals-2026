# Machine Head

**Category:** Rev | **Points:** 50 (291 solves) | **Flag:** `csaw{cl1mb1ng_th3_v1rtu4l_st4ck_0n3_0pc0d3_4t_4_t1m3}`

## Challenge

> One key for every lock.

The distributed binary is named `masterkey`. The input checker is a little custom machine whose
"language" isn't in any disassembler's opcode table — give it the master key.

## Initial Analysis

The binary (ELF x86-64, PIE, stripped) doesn't validate the input with normal comparisons. Instead
it **interprets a bytecode program** stored in `.rodata` (around offset `0x2040`). It's a custom
**stack-based virtual machine**:

- Instructions are **3 bytes**: `(opcode, A, B)`.
- There are **eight byte registers** and a value stack.
- The bytecode consumes the 53-char input and computes a pass/fail.

## The Vulnerability / Core Concept

Once you lift the VM's instruction semantics, the check becomes a system of constraints over the 53
input bytes. Rather than reverse the math by hand, feed every opcode's effect into **Z3** and let the
solver recover the unique input.

## Exploitation

`solve.py` lifts the `.rodata` bytecode into Z3 constraints and solves for the 53-character input:

```bash
python3 solve.py
# recovers the master key; a uniqueness (unsat on "any other solution") check confirms it
./masterkey
# > Correct! That's the master key.
```

## Flag

```
csaw{cl1mb1ng_th3_v1rtu4l_st4ck_0n3_0pc0d3_4t_4_t1m3}
```

## Key Takeaways

- Custom-VM crackmes are everywhere: identify the **instruction width + register/stack model**, lift
  the bytecode, and the rest is mechanical.
- **Z3** turns a constraint-style checker into an instant solve — and an `unsat` re-check proves the
  key is unique.

## Files

- `solve.py` — bytecode → Z3 constraint solver.
- `masterkey` — the challenge binary (custom stack VM).
