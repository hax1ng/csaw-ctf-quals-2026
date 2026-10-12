# Sanity Check

**Category:** Misc | **Points:** 1 (143 solves) | **Flag:** `csaw{heist_started}`

## Challenge

> Read the rules, and admire the page!

The traditional free-points warm-up — with a tiny twist.

## The Trick

The landing page proudly displays `csaw{heist_completed}`. That's a decoy. The actual instruction
is in the competition **rules** (the "read the rules" half of the prompt): swap `heist_completed`
for `heist_started`. The heist hasn't finished — it's just beginning.

Submitting the literal on-page `csaw{heist_completed}` (and the `csawctf{...}` variant) is rejected;
`csaw{heist_started}` is accepted.

## Flag

```
csaw{heist_started}
```

## Key Takeaways

- Even the sanity check can hide a one-step gotcha — **read the prompt literally** and follow both halves.
- Mind the flag wrapper: this event used `csaw{...}`, not `csawctf{...}`.
