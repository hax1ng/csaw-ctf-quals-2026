#!/usr/bin/env python3
"""Reproduce the Hemispheres extraction without password guessing."""

from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from PIL import Image


ROOT = Path(__file__).resolve().parent
PNG = ROOT / "the_signal.png"


def blue_lsb_message(path: Path) -> bytes:
    with Image.open(path) as image:
        pixels = image.convert("RGB").get_flattened_data()
        bits = [blue & 1 for _, _, blue in pixels]
    raw = bytes(
        sum(bits[pos + bit] << (7 - bit) for bit in range(8))
        for pos in range(0, len(bits) - 7, 8)
    )
    # The stream starts with a two-byte, big-endian payload length.
    size = int.from_bytes(raw[:2], "big")
    if not 0 < size <= len(raw) - 2:
        raise ValueError("invalid blue-LSB message length")
    return raw[2 : 2 + size]


def appended_zip(path: Path) -> bytes:
    data = path.read_bytes()
    # IEND is a zero-length PNG chunk: length, type, and CRC total 12 bytes.
    marker = b"\x00\x00\x00\x00IEND\xaeB`\x82"
    end = data.rfind(marker)
    if end < 0:
        raise ValueError("canonical PNG IEND chunk not found")
    trailer = data[end + len(marker) :]
    if not trailer.startswith(b"PK\x03\x04"):
        raise ValueError("PNG trailer is not a ZIP local header")
    return trailer


def main() -> None:
    password = blue_lsb_message(PNG)
    archive = appended_zip(PNG)
    (ROOT / "tail.zip").write_bytes(archive)

    print(f"password: {password.decode()}")
    with ZipFile(BytesIO(archive)) as zf:
        for name in zf.namelist():
            contents = zf.read(name, pwd=password)
            output = ROOT / "extracted" / name
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(contents)
            print(f"{name}: {contents.decode().rstrip()}")


if __name__ == "__main__":
    main()
