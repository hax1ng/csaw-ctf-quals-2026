#!/usr/bin/env python3
"""
Music Security Department (CSAW 2026 Rev) — solve.
The CDJ patch is a custom bytecode VM. EXPORT renders a 42-char "stem" via a
keystream cipher:  output[i] = (((state[i]+b[i]) & 255) % 95) + 32
  state = ebc(S ^ KEY)          (6 bytes; KEY typed via `KEY <12hex>`)
  b[i]  = stream[(5*i)%42] ^ S[i%6]
  stream = session.bin[0x8c:0xb6] (42 bytes)
  S      = mixer state after CUE IKOW[g / EQ music'_' / EXPORT arg
           (len-10 arg "9a3f......" -> S = [231,37,102,195,131,137], live-measured)
Only the first 6 output chars are directly controllable (state); chars 6..41 are a
fixed PRNG seeded by the 6-byte state. So the flag is the render output for ONE
specific KEY. Brute all keys giving a well-formed csaw{...}/flag{...} and pick the
one with a MEANINGFUL body -> csaw{~i_love_my_computer_&_it_loves_me~<3}.
Live-confirmed: CUE IKOW[g / SYNC / EQ music'_' / KEY bf03942fbd12 / EXPORT 9a3f000000
"""
import itertools
STREAM=list(open('extracted/session.bin','rb').read()[:248])[0x8c:0x8c+42]
S=[231,37,102,195,131,137]  # len-10 arg mixer state (live-validated)

def render(state):
    st=list(state); out=[]; i42=i6=0
    def emit(a):
        nonlocal i42,i6
        b=STREAM[i42]^S[i6]; i42=(i42+5)%42; i6=(i6+1)%6
        a=(a+b)&255; out.append((a%95)+32)
    for a in st: emit(a)
    ctr=36
    for _ in range(36):
        a=(st[5]+st[0])&255; a^=st[2]; a=(a+st[4])&255; a=(a*0x67)&255
        b=(a>>3)&255; a^=b; a^=st[1]; a=(a+st[3])&255; a^=ctr; a=(a+0x9e)&255
        st=st[1:]+[a]; emit(a); ctr-=1
    return bytes(out).decode('latin1')

def candbyte(i,ch):
    i42=(5*i)%42; i6=i%6; b=STREAM[i42]^S[i6]; t=ord(ch)-32
    return [st for st in range(256) if (((st+b)&255)%95)==t]

# brute the 6-byte render state that yields a csaw{...} with a meaningful body
for pfx in ("csaw{","flag{"):
    opts=[candbyte(i,pfx[i]) for i in range(5)]
    for combo in itertools.product(*opts):
        for s6 in range(256):
            r=render(list(combo)+[s6])
            if r.startswith(pfx) and r.endswith('}') and 'love' in r.lower():
                print("FLAG:", r)
