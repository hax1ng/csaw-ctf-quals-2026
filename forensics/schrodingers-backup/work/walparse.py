#!/usr/bin/env python3
import struct, sys

WAL = "evidence/catalog.db-wal"
data = open(WAL, "rb").read()

# --- WAL header (32 bytes) ---
magic = struct.unpack(">I", data[0:4])[0]
# magic 0x377f0682 -> little-endian checksums? 0x377f0683 -> big-endian
big_endian_cksum = (magic == 0x377f0683)
fmt = ">II" if big_endian_cksum else "<II"
ver   = struct.unpack(">I", data[4:8])[0]
pgsz  = struct.unpack(">I", data[8:12])[0]
ckpt  = struct.unpack(">I", data[12:16])[0]
salt1 = struct.unpack(">I", data[16:20])[0]
salt2 = struct.unpack(">I", data[20:24])[0]
hck1  = struct.unpack(">I", data[24:28])[0]
hck2  = struct.unpack(">I", data[28:32])[0]

print(f"magic=0x{magic:08x} big_endian_cksum={big_endian_cksum} ver={ver} pgsz={pgsz} ckpt={ckpt}")
print(f"hdr salt1=0x{salt1:08x} salt2=0x{salt2:08x} hck1=0x{hck1:08x} hck2=0x{hck2:08x}")

def wal_cksum(s0, s1, buf):
    # buf length must be multiple of 8
    assert len(buf) % 8 == 0
    n = len(buf) // 4
    words = struct.unpack((">" if big_endian_cksum else "<") + "I"*n, buf)
    for i in range(0, n, 2):
        s0 = (s0 + words[i] + s1) & 0xffffffff
        s1 = (s1 + words[i+1] + s0) & 0xffffffff
    return s0, s1

# verify header checksum over first 24 bytes
c0, c1 = wal_cksum(0, 0, data[0:24])
print(f"computed hdr cksum = 0x{c0:08x} 0x{c1:08x}  (match={c0==hck1 and c1==hck2})")

FRAME_HDR = 24
frame_sz = FRAME_HDR + pgsz
nframes = (len(data) - 32) // frame_sz
print(f"nframes={nframes}\n")

# Walk frames maintaining running checksum from header checksum
run0, run1 = hck1, hck2
frames = []
for i in range(nframes):
    off = 32 + i*frame_sz
    fh = data[off:off+FRAME_HDR]
    pgno = struct.unpack(">I", fh[0:4])[0]
    dbsize = struct.unpack(">I", fh[4:8])[0]   # nonzero => commit frame
    fs1 = struct.unpack(">I", fh[8:12])[0]
    fs2 = struct.unpack(">I", fh[12:16])[0]
    fc1 = struct.unpack(">I", fh[16:20])[0]
    fc2 = struct.unpack(">I", fh[20:24])[0]
    page = data[off+FRAME_HDR:off+FRAME_HDR+pgsz]

    salt_ok = (fs1 == salt1 and fs2 == salt2)

    # cumulative checksum: over frame header first 8 bytes + page data, seeded by running
    t0, t1 = wal_cksum(run0, run1, fh[0:8])
    t0, t1 = wal_cksum(t0, t1, page)
    cksum_ok = (t0 == fc1 and t1 == fc2)

    frames.append(dict(i=i, pgno=pgno, dbsize=dbsize, fs1=fs1, fs2=fs2,
                       fc1=fc1, fc2=fc2, salt_ok=salt_ok, cksum_ok=cksum_ok,
                       page=page))
    commit = "COMMIT(dbsize=%d)" % dbsize if dbsize else ""
    print(f"frame {i:2d} pg={pgno} salt=({fs1:08x},{fs2:08x}) salt_ok={salt_ok} "
          f"cksum_ok={cksum_ok} {commit}")
    # advance running checksum only along valid chain
    run0, run1 = t0, t1

import pickle
pickle.dump(frames, open("work/frames.pkl","wb"))
