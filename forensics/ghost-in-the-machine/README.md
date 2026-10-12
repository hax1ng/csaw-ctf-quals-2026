# Ghost in the Machine

**Category:** Forensics | **Points:** 279 (194 solves) | **Flag:** `csaw{t1m1ng_1s_3v3ryth1ng_1n_th3_s1l3nt_ch4nn3l}`

## Challenge

> We intercepted a host quietly beaconing out of a locked-down network. The firewall logs every
> byte that leaves — and every byte here is boring. Same source, same destination, the same little
> `PING` payload, over and over. And yet something is getting out... it's buried in the noise, it's
> scrambled, and the operator left just enough on the wire to unscramble it — if you know which
> columns to trust.

We get `capture.pcap`.

## Initial Analysis

First surprise: the pcap won't open cleanly — the libpcap magic is off by one byte (`...c4` where
it should be `...d4`). A one-byte repair (`fix_pcap.py`) makes Wireshark happy.

Every packet is an identical `PING` UDP beacon, so the payload carries nothing. The data is in the
**metadata** — "which columns to trust" is the hint. Three channels matter:

- **TTL** selects signal packets from decoys (trust only the right TTL).
- **Inter-packet timing** encodes the bits (short gap = 0, long gap = 1, with a ~70 ms gap marking
  byte boundaries).
- **UDP source port** carries the per-byte XOR key.

## The Core Concept

A **timing-based covert channel**. The message is modulated into the delays *between* packets, not
their contents — so byte inspection sees only noise. Decode: filter by TTL, bin the inter-arrival
gaps into 0/1 bits, group into bytes, then XOR each byte with a key byte derived from that packet's
source port (the key spells `sh4dow…`). The sender's jitter even matches `random.seed(1337)`.

## Exploitation

```bash
python3 fix_pcap.py        # repair the libpcap magic byte
python3 solve.py           # TTL filter -> inter-gap bit decode -> source-port XOR
```

Two independent decoders (a custom parser and a `tshark` pass) agree on the output, and the XOR
yields exactly a grammatical braced flag with no leftover bits.

## Flag

```
csaw{t1m1ng_1s_3v3ryth1ng_1n_th3_s1l3nt_ch4nn3l}
```

## Key Takeaways

- Covert channels hide in **timing, header fields, and ordering** — not payloads. When every packet
  looks identical, measure the *gaps*.
- A corrupted magic/header is often a deliberate speed bump; know your file formats byte-for-byte.

## Files

- `fix_pcap.py` — one-byte libpcap magic repair.
- `solve.py` — TTL filter + inter-packet-gap bit decoder + source-port XOR.
- `capture.pcap` — the intercepted beacon capture.
