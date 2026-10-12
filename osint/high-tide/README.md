# High Tide

**Category:** OSINT | **Flag:** `csaw{mont_saint_michel}`

## Challenge

A single Google Maps screenshot (`high_tide.png`): a massive round granite medieval tower flying
French tricolor flags. Identify the place.

## Initial Analysis

Reverse-image search is the instinct here — but it's a **dead end**: Google Lens and Yandex both
fail because Google Maps user photos aren't web-indexed. So we fall back to feature + title reasoning:

- **Granite medieval fortress tower** + **French flags** → a coastal fortress in France.
- The challenge title, **"High tide"**, is the decisive clue — it names a place famous for its
  dramatic tides.

## The Core Concept

Classic **landmark recognition reinforced by the challenge title**. A French tidal island fortress
with a round granite tower is **Mont-Saint-Michel**, the Normandy abbey-island renowned for having
one of the highest tidal ranges in Europe (the sea "high tide" that periodically surrounds it).

## Flag

```
csaw{mont_saint_michel}
```

## Key Takeaways

- When reverse-image search fails (especially on Maps user photos), pivot to **architectural
  features + the challenge title** — CTF titles are hints, not decoration.
- Geography trivia pays off: "high tide" + French fortress is a near-unique fingerprint.

## Files

- `high_tide.png` — the challenge screenshot.
