from pathlib import Path
import base64, hashlib, json, random
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

DIGIT_WORDS=("ZERO","ONE","TWO","THREE","FOUR","FIVE","SIX","SEVEN","EIGHT","NINE")

def autokey_encrypt(text,primer):
    text="".join(c for c in text.upper() if c.isalpha())
    key="".join(c for c in primer.upper() if c.isalpha())
    out=[]
    for i,ch in enumerate(text):
        k=ord(key[i])-65 if i<len(key) else ord(text[i-len(key)])-65
        out.append(chr((ord(ch)-65+k)%26+65))
    return "".join(out)

def stream_xor(data,material):
    out=bytearray(); pos=counter=0
    while pos<len(data):
        block=hashlib.sha256(material+counter.to_bytes(8,"big")).digest()
        chunk=data[pos:pos+32]
        out.extend(x^y for x,y in zip(chunk,block))
        pos+=len(chunk); counter+=1
    return bytes(out)

def build_artifacts(data,seed,flag):
    data=Path(data)
    rng=random.Random(int.from_bytes(hashlib.sha256(seed.encode()).digest(),"big"))
    # Keep the marker space too large to bypass the cryptography by using the
    # submission forms as online correctness oracles.
    suffixes=rng.sample(range(100_000_000_000,1_000_000_000_000),3)
    k1=f"GRANITE-{suffixes[0]:012d}"
    k2=f"CRYO-{suffixes[1]:012d}"
    k3=f"FERRUM-{suffixes[2]:012d}"

    suffix_words=" ".join(DIGIT_WORDS[int(d)] for d in f"{suffixes[0]:012d}")
    stone_plain=("THE FIRST FRAGMENT IS NOT THE KEY ITSELF. KEEP THE WORDS INTACT "
                 "AND RECORD THE ENTIRE LINE AFTER THE COLON. FRAGMENT ONE: "
                 "MEMORY OPENS WHAT STONE HAS SEALED. MARKER: GRANITE. "
                 f"SUFFIX: {suffix_words}")
    stone={
        "braille":"\u280e\u281e\u2815\u281d\u2811",
        "inscription":"WHAT IS REMEMBERED IS NEVER WRITTEN ONLY ONCE.",
        "ciphertext":autokey_encrypt(stone_plain,"STONE"),
        "decoys":["Q0hFQ0tTVU1fRkFJTF9OT1RfS0VZ","STONE-LOCK / 04 / 19","checksum: 7f1a0d"]
    }
    (data/"stone.json").write_text(json.dumps(stone,indent=2)+"\n",encoding="utf-8")

    frost_plain=("FROST RECORD // ORIGIN MATTERS\n"
                 "Use the complete marker from the first chamber, not the fragment label.\n"
                 "FRAGMENT TWO: PRESERVATION IS A TRACE OF ORIGIN.\n"
                 f"MARKER: {k2}\nORDER NOTE: SECOND\n").encode()
    (data/"frost.bin").write_bytes(stream_xor(frost_plain,hashlib.sha256(k1.encode()).digest()))

    h0=hashlib.sha256(k2.encode()).digest()
    h1=hashlib.sha256(h0+k1.encode()).digest()
    h2=hashlib.sha256(h1[::-1]+k2.encode()).digest()
    iron_plain=("IRON RECORD // THE SHAPE OF THE ANSWER IS NOT THE ANSWER.\n"
                "FRAGMENT THREE: ENDURANCE JOINS WHAT MEMORY AND PRESERVATION HOLD.\n"
                f"MARKER: {k3}\nORDER NOTE: THIRD\n").encode()
    iron={
        "braille":"\u280a\u2817\u2815\u281d",
        "inscription":"THE SHAPE OF THE ANSWER IS NOT THE ANSWER.",
        "columns":[hashlib.sha256(k.encode()).hexdigest() for k in (k1,k2,k3)],
        "payload_b64":base64.b64encode(stream_xor(iron_plain,h2)).decode(),
        "plate_note":"Begin with marker two. Join that digest to marker one. Reverse that result before the final join to marker two."
    }
    (data/"iron.json").write_text(json.dumps(iron,indent=2)+"\n",encoding="utf-8")

    key=hashlib.sha256(f"{k1}|{k2}|{k3}".encode()).digest()
    nonce=hashlib.sha256(f"{seed}|{flag}".encode()).digest()[:12]
    aad="NORTHERN-RELIQUARY-V1"
    vault={
        "braille":"\u2827\u2801\u2825\u2807\u281e",
        "poem":["Three fragments sleep beneath the frost,","Each guards the piece the others lost.","Stone keeps memory, frost keeps time,","Iron joins the broken line.","Set all three where old locks meet;","The buried hoard will yield its seat."],
        "nonce_b64":base64.b64encode(nonce).decode(),
        "aad":aad,
        "ciphertext_b64":base64.b64encode(AESGCM(key).encrypt(nonce,flag.encode(),aad.encode())).decode(),
        "hint":"Join the three complete markers in map order with |, then SHA-256 the result for the AES-GCM key."
    }
    (data/"vault.json").write_text(json.dumps(vault,indent=2)+"\n",encoding="utf-8")
    return k1,k2,k3
