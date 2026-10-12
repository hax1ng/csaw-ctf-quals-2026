#!/usr/bin/env python3
# Brute (KEY, EXPORT-arg) offline via the validated emu.py, for the intended config.
# Distinguisher: render output contains 'csaw' or 'flag{' or is highly readable.
import emu, itertools, sys, hashlib

def render_for(key_hex, export_arg, cue='IKOW[g', eq="music'_'"):
    vm=emu.VM(); vm.run()
    for c in [f'CUE {cue}','SYNC',f'EQ {eq}',f'KEY {key_hex}']:
        vm.feed(list((c+'\n').encode())); vm.run()
    vm.feed(list((f'EXPORT {export_arg}'+'\n').encode())); vm.run()
    out=bytes(vm.out).decode('latin1')
    if 'rendering stem ...' in out:
        after=out.split('rendering stem ...',1)[1]
        for line in after.split('\n'):
            if line.strip(): return line.strip()
    return None

def readable(s):
    if not s: return 0
    # count alnum + common flag chars
    good=sum(1 for c in s if c.isalnum() or c in '_{}!?-')
    return good

# Candidate KEYs (as 12-hex). Meaningful sources:
salt=b's4lt26'; mkey=b'M4ch1n3_K3y!!'
def hx(b): return b.hex()
key_cands=set()
key_cands.add('000000000000')
key_cands.add('4d5344213799')            # MSD!7 (S seed)
key_cands.add(hx(salt))                  # s4lt26 ascii -> 6 bytes
# windows of mkey (13 bytes) -> all 6-byte windows
for i in range(len(mkey)-5):
    key_cands.add(hx(mkey[i:i+6]))
# hashes truncated to 6 bytes
for seed in [salt,mkey,b'CSIRAC',b'I_LOVE_MY_COMPUTER',b'9a3f',salt+mkey,mkey+salt]:
    key_cands.add(hashlib.md5(seed).hexdigest()[:12])
    key_cands.add(hashlib.sha256(seed).hexdigest()[:12])
# 9a3f-prefixed
key_cands.add('9a3f00000000')
key_cands.add('9a3faabbccdd')

# Candidate EXPORT args: '9a3f'+ suffixes of various lengths (RECALL shows 9a3f......)
arg_cands=set()
arg_cands.add('9a3f')
for suf in ['aa','aabb','aabbcc','000000','s4lt26','stem','!!','26','2626','aabbccddee']:
    arg_cands.add('9a3f'+suf)
arg_cands.add('9a3faabbcc')  # len10
arg_cands.add('9a3f'+ 's4lt2')  # len 9
# also meaningful full args
for a in ['s4lt26','M4ch1n3_K3y!!','I_LOVE_MY_COMPUTER','9a3faa']:
    arg_cands.add(a)

print(f"KEY candidates: {len(key_cands)}, EXPORT-arg candidates: {len(arg_cands)}  = {len(key_cands)*len(arg_cands)} combos")
hits=[]
best=[]
for k in sorted(key_cands):
    for a in sorted(arg_cands):
        try:
            line=render_for(k,a)
        except Exception as e:
            continue
        if not line: continue
        if 'csaw' in line or 'flag{' in line.lower():
            hits.append((k,a,line)); print(f"  !!! FLAGISH  KEY={k} ARG={a} -> {line!r}")
        r=readable(line)
        best.append((r,k,a,line))
best.sort(reverse=True)
print("\n=== Top 15 most-readable renders ===")
for r,k,a,line in best[:15]:
    print(f"  [{r}/{len(line)}] KEY={k} ARG={a} -> {line!r}")
print("\n=== csaw/flag hits:",len(hits))
