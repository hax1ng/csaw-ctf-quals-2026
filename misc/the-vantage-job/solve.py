#!/usr/bin/env python3
"""Reproduce the final public OSINT hop; does not submit the flag."""
import base64
import hashlib
import re
from pathlib import Path

import requests
from PIL import Image

ALIAS = "https://tinyurl.com/38fw78xp"
EXPECTED = "https://paste.d4rk4shes.com/"
OUT = Path("artifacts/vantage_final_image.jpg")

s = requests.Session()
r = s.get(ALIAS, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=False, timeout=20)
r.raise_for_status()
destination = requests.compat.urljoin(ALIAS, r.headers["Location"])
assert destination == EXPECTED, (destination, EXPECTED)

r = s.get(destination, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
r.raise_for_status()
payload = base64.b64decode(r.content.strip(), validate=True)
assert payload.startswith(b"\xff\xd8\xff"), "response did not decode as JPEG"
OUT.write_bytes(payload)

with Image.open(OUT) as im:
    comment = im.getexif().get_ifd(0x8769).get(0x9286)  # ExifIFD.UserComment
if isinstance(comment, bytes):
    if comment.startswith(b"UNICODE\0"):
        comment = comment[8:].decode("utf-16-be").rstrip("\0")
    else:
        comment = comment.decode(errors="replace").rstrip("\0")

assert re.fullmatch(r"csaw\{[^{}]+\}", comment), repr(comment)
print("destination:", destination)
print("jpeg sha256:", hashlib.sha256(payload).hexdigest())
print("flag:", comment)
