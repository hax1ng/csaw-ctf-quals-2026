#!/usr/bin/env python3
"""schrodingers-backup solve: reconstruct WAL history -> tokens -> key -> flag."""
import json, pickle, hashlib, sys
sys.path.insert(0, "evidence")
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

DOMAIN = b"csaw-2026/schrodingers-backup/v1\x00"

tokens = pickle.load(open("work/tokens.pkl","rb"))
print(f"[*] {len(tokens)} recorded visit tokens (in order)")

key = hashlib.sha256(DOMAIN + b"".join(tokens)).digest()
print(f"[*] derived key = {key.hex()}")

cap = json.load(open("evidence/capsule.json"))
nonce = bytes.fromhex(cap["nonce"])
ct = bytes.fromhex(cap["ciphertext"])

pt = AESGCM(key).decrypt(nonce, ct, DOMAIN)
flag = pt.decode()
print(f"[+] FLAG: {flag}")
open("flag.txt","w").write(flag+"\n")
