#!/usr/bin/env python3
"""Decode the timing channel in capture.pcap."""

import struct
from pathlib import Path


PCAP = Path("capture.pcap")


def packets(raw: bytes):
    # The supplied file has a one-byte-damaged little-endian pcap magic.
    assert raw[:4] == bytes.fromhex("c4c3b2a1")
    assert raw[4:24] == bytes.fromhex(
        "020004000000000000000000ffff000001000000"
    )
    offset = 24
    while offset < len(raw):
        sec, usec, incl_len, orig_len = struct.unpack_from("<IIII", raw, offset)
        offset += 16
        frame = raw[offset : offset + incl_len]
        offset += incl_len
        assert incl_len == orig_len == 46
        assert frame[12:14] == b"\x08\x00"  # Ethernet: IPv4
        assert frame[23] == 17                # IPv4: UDP
        ttl = frame[22]
        sport, dport = struct.unpack_from("!HH", frame, 34)
        yield sec + usec / 1_000_000, ttl, sport, dport, frame[42:]
    assert offset == len(raw)


all_packets = list(packets(PCAP.read_bytes()))

# TTL 113 / source-port 50xxx packets are random decoys.  The regular stream
# uses TTL 64, source-port 40000+key_byte, and always carries PING to port 9000.
signal = [p for p in all_packets if p[1] == 64]
assert len(all_packets) == 504
assert len(signal) == 385
assert all(p[3] == 9000 and p[4] == b"PING" for p in signal)

# Consecutive signal packets are separated by ~50 ms for 0 and ~150 ms for 1.
# There are 384 gaps = 48 big-endian bytes.
gaps = [b[0] - a[0] for a, b in zip(signal, signal[1:])]
assert all(0.035 < gap < 0.065 or 0.135 < gap < 0.165 for gap in gaps)
bits = [int(gap > 0.100) for gap in gaps]

ciphertext = bytearray()
key = bytearray()
for i in range(0, len(bits), 8):
    ciphertext.append(sum(bit << (7 - j) for j, bit in enumerate(bits[i:i+8])))
    key_byte = signal[i][2] - 40000
    assert all(p[2] - 40000 == key_byte for p in signal[i:i+8])
    key.append(key_byte)

plaintext = bytes(c ^ k for c, k in zip(ciphertext, key))

print(f"packets: {len(all_packets)} ({len(signal)} signal, {len(all_packets)-len(signal)} decoy)")
print(f"key: {key.decode()}")
print(f"ciphertext: {ciphertext.hex()}")
print(f"decoded: {plaintext.decode()}")
