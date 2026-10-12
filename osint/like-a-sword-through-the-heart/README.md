# Like a Sword Through the Heart

**Category:** OSINT | **Points:** 496 | **Flag:** `csaw{cleitus_the_black}`

## Challenge

A pure text riddle — no files:

> Comradery and brotherhood... all put to an end over a clouded fight... find the name of the other man.

## Initial Analysis

No image, no metadata — this is a **historical-knowledge riddle**. Break down the clues:

- **"Comradery and brotherhood"** → two men who were close, one a subordinate/foster-brother.
- **"clouded fight"** → a drunken ("clouded" judgement) quarrel.
- **"put to an end"** / "sword through the heart" → one killed the other.
- **"the other man"** → we need the *victim's* name.

## The Core Concept

The riddle points to a famous episode from antiquity: **Alexander the Great**, in a drunken rage in
328 BC, killed his close friend and cavalry commander — his foster-brother in arms — by running him
through with a spear/sword. "The other man" is **Cleitus the Black** (Kleitos Melas), the officer who
had earlier saved Alexander's life at the Granicus.

## Flag

```
csaw{cleitus_the_black}
```

## Key Takeaways

- Text-only OSINT riddles are usually **history/mythology lookups** — map each phrase to a known event.
- "Clouded" = drunk, "brotherhood ended by a blade" = a famous betrayal/killing; those framings
  narrow the search fast.

(Fallback variants considered in case of rejection: `black cleitus`, `cleitus`.)
