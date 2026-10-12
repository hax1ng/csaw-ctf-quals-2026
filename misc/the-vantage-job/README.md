# The Vantage Job

**Category:** Misc (OSINT chain) | **Points:** 475 (67 solves) | **Flag:** `csaw{cr0ss_pl4tf0rm_carel3ssness}`

## Challenge

A heist-themed, multi-platform OSINT chase. A thief who goes by "Ferryman" left behind
`evidence_01.pdf` (an almost-blank poem) and a hint file. Follow his cross-platform brags to the
flag. The flag — `cr0ss_pl4tf0rm_carel3ssness` — is the whole lesson: he reused identity across
platforms and got sloppy.

## Initial Analysis

`evidence_01.pdf` looks blank, but it's a **near-white poem** — contrast-stretch it (or select-all /
re-render) and text appears. That poem points to the first platform, and from there it's a chain of
links where each platform leaks the next handle.

## The Core Concept — the OSINT hop chain

1. **Contrast-stretch the PDF poem** → a reference to a Discord bot command.
2. **Discord `/fingerprint`** (bot `ferryman_vt`) → next clue.
3. **Instagram acrostic** → recover X/Twitter handles.
4. **X handles** `@tockferr`, `@timepieces_ferr` → TinyURL aliases in the bios.
5. **TinyURL → `paste.d4rk4shes.com`** → a Base64 blob.
6. Base64 decodes to a **JPEG whose EXIF `UserComment` holds the flag**.

## Exploitation

`solve.py` reproduces the final step — pulling the flag out of the recovered image's EXIF:

```bash
python3 solve.py      # reads artifacts/vantage_final_image.jpg EXIF UserComment -> flag
exiftool artifacts/vantage_final_image.jpg | grep -i usercomment
```

The small `artifacts/*.json` files record each OSINT hop (Discord invite, Instagram oEmbed, the X
profiles) so the trail is reproducible.

## Flag

```
csaw{cr0ss_pl4tf0rm_carel3ssness}
```

## Key Takeaways

- **Identity reuse across platforms** is the core OSINT lesson — one handle links to the next until
  the whole persona unravels.
- Near-white / low-contrast text in PDFs is a classic hiding spot; stretch contrast before giving up.
- The flag frequently lives in **EXIF `UserComment`** of a recovered image — always dump metadata.

## Files

- `solve.py` — extracts the flag from the final image's EXIF.
- `evidence_01.pdf`, `evidence_02.txt` — the starting artifacts.
- `artifacts/vantage_final_image.jpg` (+ `*_exif.txt`) — the terminal image carrying the flag.
- `artifacts/*.json` — recorded OSINT hop records.
