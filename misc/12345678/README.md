# 12345678!

**Category:** Misc | **Points:** 500 (7 solves) | **Flag:** `csaw{1n_0rd3r_2_5t3@1_u_n33d_2_f1nd}`

## Challenge

> listen....when you find the answer it will glisten.....

A single file: `12345678.wav`. 500 points, only 7 solves — one of the hardest misc challenges of
the event.

## Initial Analysis

"Listen" + a WAV = audio steganography, and the low solve count warns there's *more than one* layer.
Standard first passes — spectrogram (Audacity/`sox`), channel split, metadata — each reveal a
*different* fragment of the flag. The flag is assembled from **four independent stego layers**:

| Layer | Technique | Fragment |
|-------|-----------|----------|
| 1 | **Reversed speech** — play audio backwards, transcribe | `1n_0rd3r_` |
| 2 | **Base64 in RIFF/ID3 date metadata** | `2_5t3@1_` |
| 3 | **Multitone "dot-matrix font"** — 7 carrier frequencies rendered as a bitmap → Base64 | `u_n33d_` |
| 4 | **Pitch-raised spelled speech** — slow down / drop pitch, it spells the last part | `2_f1nd` |

## The Core Concept

There's no single clever bug — it's a **layered audio-stego gauntlet**. The real difficulty is
*recognising* each encoding (reversed waveform, metadata smuggling, a multitone bitmap font, and
pitch-shifted voice) and realising the final flag is the **concatenation** of all four fragments,
in order.

## Exploitation

`solve.py` pulls the pieces programmatically (reverse the samples, parse the metadata Base64,
demodulate the 7-tone bitmap, resample the spelled section) and concatenates them.

```bash
python3 solve.py 12345678.wav
```

## Flag

```
csaw{1n_0rd3r_2_5t3@1_u_n33d_2_f1nd}
```

> Note: an earlier attempt produced the plausible-but-wrong
> `csaw{@11_u_n33d_15_2_5t3@1_th3_k3y_1n_0rd3r_2_g3t_th3_g01d}` — that candidate was rejected.
> The accepted flag is the one above.

## Key Takeaways

- Hard audio-stego challenges stack layers — check **reversal, pitch, metadata, and spectrogram/tone
  encodings** independently, then assemble.
- When a fragment reads like part of a sentence, keep going — the flag may span several channels.

## Files

- `solve.py` — extracts and concatenates all four stego layers.
- `12345678.wav` — the challenge audio.
