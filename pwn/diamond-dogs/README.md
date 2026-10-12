# Diamond Dogs

**Category:** Pwn | **Points:** 331 (170 solves) | **Flag:** `csaw{w3dd1ngs_4r3_b4s1c4lly_fun3r4ls_w1th_c4k3}`

## Challenge

A K-9 "dog + note" heap manager (`guard-dog`). You can adopt/command/release dogs and
file/read/shred notes.

> A released dog doesn't always stay gone. Get a shell.

**libc:** 2.31.

## Initial Analysis (`checksec` + the menu)

The binary is a standard heap-manager CTF shape. The bug is in the "release" paths: freeing a dog
or note **does not NULL the pointer**, leaving dangling references. So "released" objects are still
reachable — a classic **use-after-free**.

## The Vulnerability

Two primitives from the UAF:

1. **libc leak** — free a chunk large enough to land in the **unsorted bin**, then read it back; the
   `fd`/`bk` pointers leak a libc address, defeating ASLR.
2. **Fake object** — because freed pointers aren't cleared, you can get a note chunk and a dog chunk
   to **overlap**. Craft a fake "dog" whose `speak` function pointer is `system` and whose body is
   the string `"cat flag.txt"`.

Calling the fake dog's `speak()` then executes `system("cat flag.txt")`.

## Exploitation

`exploit.py` (pwntools) walks the sequence:

```text
1. adopt/file chunks, free into unsorted bin        -> leak libc base
2. UAF overlap: note data lands over a dog object    -> forge {fn=system, arg="cat flag.txt"}
3. "command" the forged dog -> speak() == system("cat flag.txt")
```

```bash
python3 exploit.py <HOST> <PORT>     # target supplied as args (libc 2.31)
```

The process returns cleanly to the menu after the `system()` call (controlled call, not a crash),
printing the flag.

## Flag

```
csaw{w3dd1ngs_4r3_b4s1c4lly_fun3r4ls_w1th_c4k3}
```

## Key Takeaways

- **Free without NULLing = UAF.** Dangling pointers give both an unsorted-bin libc leak and chunk overlap.
- Overlapping a controllable buffer onto an object with a **function pointer** turns UAF into a clean
  `system()` call — no ROP needed.

## Files

- `exploit.py` — full pwntools UAF → leak → fake-object → `system` exploit.
- `guard-dog` — the challenge binary (libc 2.31; use a matching libc to run locally).
