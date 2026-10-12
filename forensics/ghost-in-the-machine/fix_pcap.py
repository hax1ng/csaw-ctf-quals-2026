#!/usr/bin/env python3
"""Repair the deliberately altered libpcap magic byte."""
from pathlib import Path

src = Path("capture.pcap")
dst = Path("capture_fixed.pcap")
data = bytearray(src.read_bytes())
assert data[:4] == bytes.fromhex("c4c3b2a1")
data[0] = 0xD4  # little-endian microsecond-resolution libpcap magic
dst.write_bytes(data)
print(f"wrote {dst} ({len(data)} bytes)")
