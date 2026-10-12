# Recon: Two Marks, One Score

**Category:** OSINT | **Points:** 403 (129 solves) | **Flag:** `csaw{N723KP}`

## Challenge

Two surveillance photos tied to coordinates in a travel manifest: an ornate building corner, and an
LA Metro "M" logo. Identify the "operation," then the "identifier high in the sky."

## Initial Analysis

Two "marks" (locations), one "score" (the operation). Geolocate each photo:

- **Photo 1:** an ornate building corner → **Campo San Barnaba, Venice**.
- **Photo 2:** an LA Metro "M" → **Hollywood/Vine, Los Angeles**.

Venice + Los Angeles as a paired heist setting is the tell: both are iconic filming locations for
the 2003 film **The Italian Job**.

## The Core Concept

The two photos are both **filming locations from *The Italian Job* (2003)**. That identifies the
"operation." The final clue — **"the identifier high in the sky"** — points at the heist's
helicopter. The on-screen aircraft is an **MD 500** carrying the (false, prop) tail registration
**N723KP**, documented on the Internet Movie Plane Database (impdb.org).

## Exploitation (the pivot)

1. Reverse/landmark-search both photos → Venice + LA → *The Italian Job*.
2. Identify the film's helicopter and read its on-screen tail number via impdb.org → `N723KP`.

> A tempting dead end: an earlier line of analysis chased a 9/11 flights theory (AA11/UA175) from
> the manifest coordinates and never reached the answer. The filming-location pivot is what solved it.

## Flag

```
csaw{N723KP}
```

(Confirmed correct on CTFd, challenge ID 15.)

## Key Takeaways

- Pair-of-locations challenges often resolve to a **movie / shared cultural reference**, not raw geo-coords.
- Niche databases (impdb.org for aircraft, ship registries, etc.) hold the final identifier — know they exist.

## Files

- `First_Image.png`, `Second_Image.png` — the two surveillance photos.
