# Roll Call

**Category:** OSINT (data reconciliation) | **Points:** 172 (236 solves) | **Flag:** `csaw{halcyonleaks_still_water_77}`

## Challenge

> You are an intelligence analyst on an executive protection detail. Someone has made a credible
> threat against your principal... Before the team can assess anyone, you have to scope the case:
> **Who is actually in it?**

You get `d.zip`: an authoritative intake database (`intake.db`) plus a hand-maintained, *lagging*
watchlist CSV and supporting comms dumps.

## Initial Analysis

The watchlist is maintained by hand and is behind the real data. The question "who is in the case?"
becomes: **which subjects were escalated but never written onto the watchlist?** This is a
set-difference problem — but with a trap.

Looking at the schema in `intake.db`: `escalations`, `watchlist`, and `identities`. The naive
approach is to diff by *handle*, but people have **alias handles**, so diffing on handles produces
false positives. The correct key is **`person_id`**.

## The Core Concept

**SQL set-difference by identity, not by alias.** Compute the escalated `person_id`s that have no
corresponding `watchlist` entry. That isolates exactly two people (P03 and P09) while correctly
rejecting two alias-handle false positives. Take each person's *primary* handle, lowercase, and
alphabetize → the two names that build the flag.

## Exploitation

```bash
unzip d.zip
python3 solve.py        # set-difference over person_id -> primary handles
# -> halcyonleaks_still_water_77
```

The solver is deterministic and reproducible against `intake.db`.

## Flag

```
csaw{halcyonleaks_still_water_77}
```

## Key Takeaways

- Reconcile records on a **stable identity key** (`person_id`), never on mutable aliases/handles —
  that distinction is the whole challenge.
- "Who's actually in the case" = set difference between the authoritative source and the lagging copy.

## Files

- `solve.py` — SQL set-difference reconciliation.
- `d.zip` — the intake DB, watchlist CSV, and comms dumps.
