#!/usr/bin/env python3
"""Offline solver for Taking on the Temple / Midnight Vault."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# Standard (uncontracted) English Braille.  The first tablet spells STONE,
# which is the primer for its plaintext-autokey cipher.
BRAILLE = dict(
    zip(
        "abcdefghijklmnopqrstuvwxyz",
        "⠁⠃⠉⠙⠑⠋⠛⠓⠊⠚⠅⠇⠍⠝⠕⠏⠟⠗⠎⠞⠥⠧⠺⠭⠽⠵",
    )
)
BRAILLE = {value: key for key, value in BRAILLE.items()}

DIGIT_WORDS = {
    "ZERO": "0",
    "ONE": "1",
    "TWO": "2",
    "THREE": "3",
    "FOUR": "4",
    "FIVE": "5",
    "SIX": "6",
    "SEVEN": "7",
    "EIGHT": "8",
    "NINE": "9",
}


def braille_letters(value: str) -> str:
    return "".join(BRAILLE[ch] for ch in value).upper()


def autokey_decrypt(ciphertext: str, primer: str) -> str:
    """Decrypt a Vigenere plaintext-autokey ciphertext."""
    primer_values = [ord(ch) - ord("A") for ch in primer.upper()]
    plaintext_values: list[int] = []
    for i, ch in enumerate(ciphertext.upper()):
        key_value = (
            primer_values[i]
            if i < len(primer_values)
            else plaintext_values[i - len(primer_values)]
        )
        plaintext_values.append((ord(ch) - ord("A") - key_value) % 26)
    return "".join(chr(value + ord("A")) for value in plaintext_values)


def digit_words_to_number(value: str) -> str:
    """Decode a concatenation such as SIXONE... without requiring spaces."""
    if not value:
        return ""
    for word, digit in DIGIT_WORDS.items():
        if value.startswith(word):
            try:
                return digit + digit_words_to_number(value[len(word) :])
            except ValueError:
                pass
    raise ValueError(f"cannot parse digit-word suffix at {value!r}")


def stream_xor(data: bytes, material: bytes) -> bytes:
    """XOR data with SHA-256(material || uint64_be(counter)) blocks."""
    output = bytearray()
    for counter, pos in enumerate(range(0, len(data), 32)):
        block = hashlib.sha256(material + counter.to_bytes(8, "big")).digest()
        output.extend(a ^ b for a, b in zip(data[pos : pos + 32], block))
    return bytes(output)


def marker_from_text(text: str, prefix: str) -> str:
    match = re.search(rf"MARKER:\s*({re.escape(prefix)}-\d{{12}})", text)
    if not match:
        raise ValueError(f"could not find {prefix} marker")
    return match.group(1)


def solve(data_dir: Path) -> str:
    stone = json.loads((data_dir / "stone.json").read_text())
    primer = braille_letters(stone["braille"])
    stone_plain = autokey_decrypt(stone["ciphertext"], primer)
    suffix_words = stone_plain.split("SUFFIX", 1)[1]
    k1 = "GRANITE-" + digit_words_to_number(suffix_words)

    frost_material = hashlib.sha256(k1.encode()).digest()
    frost_plain = stream_xor(
        (data_dir / "frost.bin").read_bytes(), frost_material
    ).decode()
    k2 = marker_from_text(frost_plain, "CRYO")

    # Follow iron.json's plate_note literally, retaining raw digest bytes:
    # SHA256(marker2), append marker1 and hash, reverse that digest, append
    # marker2 and hash once more.
    h0 = hashlib.sha256(k2.encode()).digest()
    h1 = hashlib.sha256(h0 + k1.encode()).digest()
    h2 = hashlib.sha256(h1[::-1] + k2.encode()).digest()
    iron = json.loads((data_dir / "iron.json").read_text())
    iron_plain = stream_xor(base64.b64decode(iron["payload_b64"]), h2).decode()
    k3 = marker_from_text(iron_plain, "FERRUM")

    vault = json.loads((data_dir / "vault.json").read_text())
    key = hashlib.sha256(f"{k1}|{k2}|{k3}".encode()).digest()
    flag = AESGCM(key).decrypt(
        base64.b64decode(vault["nonce_b64"]),
        base64.b64decode(vault["ciphertext_b64"]),
        vault["aad"].encode(),
    ).decode()

    print(f"[+] Stone primer: {primer}")
    print(f"[+] Stone marker: {k1}")
    print(f"[+] Frost marker: {k2}")
    print(f"[+] Iron marker: {k3}")
    print(f"[+] Flag: {flag}")
    return flag


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", nargs="?", type=Path, default=Path("data"))
    args = parser.parse_args()
    solve(args.data_dir)
