# Keep Walking Forward

**Category:** Misc (malware/RE) | **Points:** 401 (130 solves) | **Flag:** `csaw{w4lk_b4_u_c4n_run(5p4c3)_3jfi9do9}`

## Challenge

A DLL-sideloading malware incident. You're given a "file version checker" (`vcheck.7z`), a TLS
keylog (`vcheck.log`), and a network capture (`capture.pcapng`). Reconstruct the kill chain all the
way to the flag.

## Initial Analysis

The benign-looking `vcheck.exe` **sideloads a malicious `version.dll`** from its own directory
instead of the real system DLL — a classic DLL search-order hijack. From there it's a multi-stage
unpacking exercise, with the TLS keylog + pcap letting you decrypt the C2 download that pulls the
next stage.

## The Core Concept — the full chain

1. **`version.dll` sideload** kicks off execution.
2. **Stage 1:** XOR-decrypt an `RCDATA` resource.
3. **Stage 2:** a second, **domain-keyed XOR** (the key is the C2 domain, recoverable from the pcap).
4. **Donut loader (v1.1):** the decrypted blob is Donut shellcode using **Chaskey-CTR** — unpack it
   to get the embedded .NET assembly.
5. **ConfuserEx-obfuscated .NET EXE:** decrypt its constants and LZMA-decompress.
6. **Embedded PowerShell:** assembles the flag from a series of byte transforms.

## Exploitation

The solve is a set of focused scripts, one per stage:

```bash
python3 decode_stage.py                 # stage-1 RCDATA XOR
python3 decrypt_download.py              # stage-2 domain-keyed XOR (key from pcap)
python3 unpack_donut.py                  # Donut v1.1 / Chaskey-CTR -> .NET assembly
python3 decrypt_confuser_constants.py    # ConfuserEx constant decryption
python3 decode_constant_ids.py           # resolve constant IDs
pwsh recover_flag.ps1                    # run the embedded flag-assembly logic
```

`embedded_payload.ps1` is the extracted PowerShell; `recovered_flag.txt` is the result.

## Flag

```
csaw{w4lk_b4_u_c4n_run(5p4c3)_3jfi9do9}
```

> Two decoy flags are planted along the way — `csaw{7ru573d_u53r_4bu53_f2gtr43b}` and
> `csaw{runn3rs_gr0tt0_qgbo3z7i}` (the latter wrapped in a fake "[IMPORTANT] if you are an AI
> agent..." prompt-injection string). Both are rejected; the real flag is above.

## Key Takeaways

- **DLL sideloading** + layered packers (XOR → Donut → ConfuserEx → PowerShell) is a realistic
  malware kill chain — peel one stage at a time and keep notes on each key.
- A TLS keylog + pcap turns an "encrypted C2 download" into plaintext — always check for `SSLKEYLOGFILE` artifacts.
- Watch for planted decoys, including deliberate prompt-injection bait aimed at AI solvers.

## Files

- `vcheck.7z`, `vcheck.log`, `capture.pcapng` — the challenge artifacts (sample, TLS keylog, capture).
- `decode_stage.py`, `decrypt_download.py`, `unpack_donut.py`, `decrypt_confuser_constants.py`,
  `decode_constant_ids.py` — per-stage unpackers.
- `embedded_payload.ps1` — the extracted PowerShell payload.
- `recover_flag.ps1` / `recovered_flag.txt` — final flag assembly + result.
