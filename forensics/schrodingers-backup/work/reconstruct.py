#!/usr/bin/env python3
"""Replay valid WAL frames, snapshot committed state, collect armed tokens."""
import struct, os, subprocess, tempfile, pickle

BASE = "evidence/catalog.db"
frames = pickle.load(open("work/frames.pkl","rb"))

PGSZ = 1024
base = bytearray(open(BASE, "rb").read())
npages_base = len(base)//PGSZ
# current page images (1-indexed)
pages = {p: bytes(base[(p-1)*PGSZ:p*PGSZ]) for p in range(1, npages_base+1)}

def build_db():
    maxpg = max(pages)
    out = bytearray()
    for p in range(1, maxpg+1):
        out += pages.get(p, b"\x00"*PGSZ)
    return bytes(out)

def query_state():
    dbbytes = build_db()
    fd, path = tempfile.mkstemp(suffix=".db")
    os.write(fd, dbbytes); os.close(fd)
    def q(sql):
        r = subprocess.run(["sqlite3", f"file:{path}?immutable=1", sql],
                           capture_output=True, text=True)
        return r.stdout.strip(), r.stderr.strip()
    armed,_ = q("SELECT armed FROM control WHERE id=1;")
    label,_ = q("SELECT label FROM control WHERE id=1;")
    north,_ = q("SELECT hex(share) FROM north WHERE id=1;")
    south,_ = q("SELECT hex(share) FROM south WHERE id=1;")
    pulse,_ = q("SELECT pulse FROM maintenance WHERE id=1;")
    os.unlink(path)
    return armed, label, north, south, pulse

# baseline snapshot (NOT a visit)
b_armed,b_label,b_north,b_south,b_pulse = query_state()
print(f"BASELINE: armed={b_armed} label={b_label} pulse={b_pulse}")
print(f"  north={b_north}")
print(f"  south={b_south}")
tok = bytes(a^b for a,b in zip(bytes.fromhex(b_north), bytes.fromhex(b_south)))
print(f"  token={tok.hex()}  (baseline, not counted)\n")

visit_tokens = []
commit_no = 0
for fr in frames:
    if not (fr["salt_ok"] and fr["cksum_ok"]):
        print(f"-- stop: frame {fr['i']} invalid (salt_ok={fr['salt_ok']} cksum_ok={fr['cksum_ok']}) --")
        break
    pages[fr["pgno"]] = fr["page"]
    if fr["dbsize"] != 0:  # commit frame
        commit_no += 1
        armed,label,north,south,pulse = query_state()
        tok = bytes(a^b for a,b in zip(bytes.fromhex(north), bytes.fromhex(south)))
        mark = ""
        if armed == "1":
            visit_tokens.append(tok)
            mark = f"  <-- VISIT #{len(visit_tokens)}"
        print(f"commit {commit_no:2d} (frame {fr['i']:2d}) armed={armed} label={label:8s} pulse={pulse} token={tok.hex()}{mark}")

print(f"\nTotal committed txns: {commit_no}")
print(f"Total recorded visits (armed): {len(visit_tokens)}")

pickle.dump(visit_tokens, open("work/tokens.pkl","wb"))
