#!/usr/bin/env python3
from pathlib import Path
import struct, sys

def ror32(x,n): return ((x>>n)|(x<<(32-n)))&0xffffffff

def chaskey(key,block):
 k=struct.unpack('<4I',key)
 w=list(struct.unpack('<4I',block))
 for i in range(4): w[i]^=k[i]
 for _ in range(16):
  w[0]=(w[0]+w[1])&0xffffffff
  w[1]=ror32(w[1],27)^w[0]
  w[2]=(w[2]+w[3])&0xffffffff
  w[3]=ror32(w[3],24)^w[2]
  w[2]=(w[2]+w[1])&0xffffffff
  w[0]=(ror32(w[0],16)+w[3])&0xffffffff
  w[3]=ror32(w[3],19)^w[0]
  w[1]=ror32(w[1],25)^w[2]
  w[2]=ror32(w[2],16)
 for i in range(4): w[i]^=k[i]
 return struct.pack('<4I',*w)

def crypt(key,ctr,data):
 ctr=bytearray(ctr); data=bytearray(data)
 for pos in range(0,len(data),16):
  x=chaskey(key,ctr)
  n=min(16,len(data)-pos)
  for i in range(n):data[pos+i]^=x[i]
  for i in range(15,-1,-1):
   ctr[i]=(ctr[i]+1)&255
   if ctr[i]: break
 return bytes(data)

if __name__=='__main__':
 b=Path(sys.argv[1] if len(sys.argv)>1 else 'stage2.bin').read_bytes()
 # skip initial E8 disp32 and use declared instance length
 inst=bytearray(b[5:5+struct.unpack_from('<I',b,5)[0]])
 key=inst[4:20];ctr=inst[20:36]
 inst[0x23c:]=crypt(key,ctr,inst[0x23c:])
 Path('donut_instance_dec.bin').write_bytes(inst)
 print('inst len',hex(len(inst)),'key',key.hex(),'ctr',ctr.hex())
 print('exit entropy oep api_cnt',struct.unpack_from('<IIII',inst,0x230))
