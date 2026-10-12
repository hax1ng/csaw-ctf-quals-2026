# House of Hollow Houses

**Category:** Misc | **Points:** 83 (266 solves) | **Flag:** `csaw{w4nd3r3r_0f_th3_h0ll0w_h0us3}`

## Challenge

> A labyrinth of "hollow" rooms served as a static website — each room links to others, and the
> flag lies waiting in the sanctum. Players wander the interlinked rooms (and read what the pages
> are quietly telling them) to find the way in.

Hosted static site: `https://hollow-houses.ctf.csaw.io/`.

## Initial Analysis

It's a static site of interlinked "rooms." "Read what the pages are quietly telling you" is the
cue to look past the rendered text — comments, headers, `robots.txt`, and the structure of the
pages themselves. The trail is a breadcrumb chain:

1. **`robots.txt`** points at a disallowed path.
2. A **hidden acrostic** across the room pages spells `OSSUARY`.
3. That decodes (Base64) to a pointer to **`/mirror/`**.
4. On `/mirror/`, the message is encoded in **Morse hidden in the inter-word spacing**:
   `THE FLAG LIES WAITING IN THE SANCTUM`.
5. **`/sanctum/`** serves the flag.

## The Core Concept

A pure **web-breadcrumb / steganographic-in-plain-sight** puzzle: no exploit, just careful reading.
Each layer hides its pointer in a different channel — robots.txt, an acrostic, Base64, and Morse
encoded as whitespace — until you reach the sanctum.

## Exploitation

`crawl_linked.py` spiders the interlinked rooms and `solve_wellspring.py` walks the decode chain
(acrostic → Base64 → Morse-from-spacing) to the final path.

```bash
python3 crawl_linked.py          # map the room graph
python3 solve_wellspring.py      # follow the breadcrumb chain to /sanctum/
```

The flag is served directly in `/sanctum/` (captured in `artifacts/sanctum.html`).

## Flag

```
csaw{w4nd3r3r_0f_th3_h0ll0w_h0us3}
```

## Key Takeaways

- `robots.txt`, HTML comments, acrostics, and whitespace are all legitimate hiding spots — read the
  *markup*, not just the page.
- Morse hidden in spacing/case is a recurring CTF trick; normalise whitespace and look for `. -` structure.

## Files

- `crawl_linked.py` — link-graph crawler.
- `solve_wellspring.py` — breadcrumb decode chain.
- `artifacts/sanctum.html` — the page that serves the flag.
