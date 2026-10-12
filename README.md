# CSAW CTF Qualification Round 2026 — Writeups

Solutions, exploits, and writeups for challenges solved during the **CSAW CTF Qualification
Round 2026**.

- **Event:** CSAW CTF Qualification Round 2026 ([ctf.csaw.io](https://ctf.csaw.io/)) — CTFd platform
- **Dates:** September 18–20, 2026 (Fri 12:00 EDT → Sun 12:00 EDT)
- **Author:** [hax1ng](https://github.com/hax1ng)
- **Challenges solved:** 25 across 7 categories

Each challenge has its own directory with a standalone writeup (`README.md`) plus the final solve
scripts / exploits and the relevant challenge files.

> **Flag format:** this event used `csaw{...}` (a couple of challenges, e.g. CSALE, used `csawctf{...}`
> — noted where it applies).

## About the event

CSAW is one of the longest-running student-oriented CTFs, run by NYU's OSIRIS Lab. The 2026
qualifier ran a broad CTFd board across Crypto, Forensics, Misc, OSINT, Pwn, Rev, and Web, with a
loose "heist" theme running through many of the challenges.

## Solved challenges

### Crypto
| Challenge | Points | Solves | Core idea |
|-----------|:------:|:------:|-----------|
| [Taking on the Temple](crypto/taking-on-the-temple/) | — | — | Chained decrypt: Braille → autokey Vigenère → SHA-256 keystream → AES-GCM |
| [Finders Keepers!](crypto/finders-keepers/) | 212 | 221 | Flag in MP4 metadata → Base64 → Vigenère (known-plaintext key recovery) |
| [Polly](crypto/polly/) | 338 | 166 | xorshift nonce seed recovery over GF(2) → ChaCha20 keystream reuse |
| [Secret Treaties](crypto/secret-treaties/) | 175 | 235 | Low-density subset-sum (knapsack) broken with LLL/BKZ lattice reduction |

### Forensics
| Challenge | Points | Solves | Core idea |
|-----------|:------:|:------:|-----------|
| [Schrödinger's Backup](forensics/schrodingers-backup/) | 500 | — | SQLite WAL frame validation → ordered tokens → AES-GCM key derivation |
| [Hemispheres](forensics/hemispheres/) | 50 | 318 | PNG/ZIP polyglot + blue-channel LSB password → ZipCrypto decrypt |
| [Ghost in the Machine](forensics/ghost-in-the-machine/) | 279 | 194 | pcap timing covert channel (TTL filter + inter-packet bits + source-port XOR) |

### Misc
| Challenge | Points | Solves | Core idea |
|-----------|:------:|:------:|-----------|
| [12345678!](misc/12345678/) | 500 | 7 | Four stacked WAV audio-stego layers assembled into one flag |
| [House of Hollow Houses](misc/house-of-hollow-houses/) | 83 | 266 | Web breadcrumb: robots.txt → acrostic → Base64 → Morse-in-spacing → /sanctum/ |
| [Keep Walking Forward](misc/keep-walking-forward/) | 401 | 130 | DLL sideload → XOR stages → Donut shellcode → ConfuserEx .NET → PowerShell |
| [Sanity Check](misc/sanity-check/) | 1 | 143 | Read the rules: swap `heist_completed` → `heist_started` |
| [The Vantage Job](misc/the-vantage-job/) | 475 | 67 | Cross-platform OSINT trail: PDF → Discord → Instagram → X → paste → EXIF |

### OSINT
| Challenge | Points | Solves | Core idea |
|-----------|:------:|:------:|-----------|
| [High Tide](osint/high-tide/) | — | — | Landmark + title reasoning → Mont-Saint-Michel |
| [Like a Sword Through the Heart](osint/like-a-sword-through-the-heart/) | 496 | — | Historical riddle → Alexander kills Cleitus the Black |
| [Recon: Two Marks, One Score](osint/recon-two-marks-one-score/) | 403 | 129 | *The Italian Job* filming locations → prop helicopter tail number |
| [Roll Call](osint/roll-call/) | 172 | 236 | SQL set-difference by `person_id` (not alias) over an intake DB |

### Pwn
| Challenge | Points | Solves | Core idea |
|-----------|:------:|:------:|-----------|
| [Diamond Dogs](pwn/diamond-dogs/) | 331 | 170 | Double UAF → unsorted-bin libc leak → fake object w/ `system` callback |
| [Hells Bells](pwn/hells-bells/) | 368 | 150 | UAF → libc leak → tcache poison `__free_hook` → `system("/bin/sh")` (glibc 2.31) |

### Rev
| Challenge | Points | Solves | Core idea |
|-----------|:------:|:------:|-----------|
| [Music Security Department](rev/music-security-department/) | 499 | 17 | Bytecode VM hidden in a Purr-Data patch; brute the 6-byte EXPORT keystream |
| [Autobahn](rev/autobahn/) | 92 | 263 | Self-modifying code: `mprotect` + XOR-decrypt the real check at runtime |
| [Machine Head](rev/machine-head/) | 50 | 291 | Custom stack VM lifted into Z3 constraints to recover the key |

### Web
| Challenge | Points | Solves | Core idea |
|-----------|:------:|:------:|-----------|
| [Golf Heist](web/golf-heist/) | — | — | Caddy `forward_auth` header-injection privesc (`X-User-Role: admin`) + Enigma |
| [CSALE](web/csale/) | 487 | 49 | UNION SQLi → XOR vault → 4-digit PIN brute via pristine-cookie replay |
| [TrustDinOIDC](web/trustdinoidc/) | 299 | 185 | JWT `x5c` cert-chain injection (name-only, signature never verified) |
| [Juggler](web/juggler/) | 468 | 75 | PHP mass assignment + loose-comparison (`true == "admin"`) auth bypass |

## Notable solves

- **12345678!** (Misc, 500 pts, **7 solves**) — a four-layer audio-stego gauntlet (reversed speech,
  metadata Base64, a multitone bitmap font, and pitch-shifted voice), all concatenated.
- **Music Security Department** (Rev, 499 pts, **17 solves**) — a complete custom bytecode VM hidden
  inside a Purr-Data music patch, with the flag sealed behind a brute-forceable keystream cipher.
- **Secret Treaties** (Crypto) — a clean LLL/BKZ break of a "quantum-resistant" subset-sum scheme,
  exploiting ASCII high-bit structure to push the lattice density down.

## Repository layout

```
<category>/<challenge>/
  README.md        # the writeup
  solve.py / ...   # final solve script(s) / exploit(s)
  <challenge files># source, binaries, or evidence needed to reproduce
```

## Disclaimer

All material here targets intentionally-vulnerable challenges built for an authorized educational
CTF. Techniques are documented for learning and for the challenge authors' reference. Remote
challenge endpoints were only reachable during the event.
