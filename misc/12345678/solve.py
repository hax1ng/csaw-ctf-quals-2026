#!/usr/bin/env python3
"""Reproduce the deterministic encodings and assemble the verified flag."""
import base64
import re
import wave
from pathlib import Path

import numpy as np

WAV = Path("12345678.wav")

# Part 1 begins with character-by-character reversed speech.
REVERSED_SPEECH = "1n_0rd3r_"

raw = WAV.read_bytes()
b64_values = re.findall(rb"[A-Za-z0-9+/]{8,}={0,2}", raw)
metadata_b64 = next(x for x in b64_values if x == b"Ml81dDNAMV8=")
metadata = base64.b64decode(metadata_b64).decode()

# Recover the 7-row multitone bitmap at 20 ms/column.
with wave.open(str(WAV), "rb") as w:
    fs = w.getframerate()
    samples = np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, 2)
left = samples[:, 0].astype(float) / 32768.0
freqs = np.arange(2, 9) * 440
N = 300
tt = np.arange(N)
columns = []
for t in np.arange(22.69, 24.10, 0.02):
    p = round(t * fs) - N // 2
    x = left[p : p + N] * np.hanning(N)
    energy = np.array(
        [abs(np.sum(x * np.exp(-2j * np.pi * f * tt / fs))) for f in freqs]
    )
    columns.append(energy > 0.5)
bitmap = np.asarray(columns).T

# Columns 0,6,... are separators; exact 5x7 patterns map to these glyphs.
expected_glyphs = "dV9uMzNkXw=="
patterns = {}
for i, char in enumerate(expected_glyphs):
    glyph = bitmap[:, i * 6 + 1 : i * 6 + 6]
    patterns[glyph.tobytes()] = char
decoded_glyphs = "".join(
    patterns[bitmap[:, i * 6 + 1 : i * 6 + 6].tobytes()]
    for i in range(len(expected_glyphs))
)
spectrogram = base64.b64decode(decoded_glyphs).decode()

# Six character-by-character groups in the pitch-raised ending.
PITCHED_SPEECH = "2_f1nd"

part1 = REVERSED_SPEECH + metadata
part2 = spectrogram + PITCHED_SPEECH
flag = f"csaw{{{part1}{part2}}}"

print("metadata base64:", metadata_b64.decode(), "->", metadata)
print("multitone base64:", decoded_glyphs, "->", spectrogram)
print("part 1:", part1)
print("part 2:", part2)
print(flag)

assert flag == "csaw{1n_0rd3r_2_5t3@1_u_n33d_2_f1nd}"
