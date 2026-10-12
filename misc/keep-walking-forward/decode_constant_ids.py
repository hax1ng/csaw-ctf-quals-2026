#!/usr/bin/env python3
from pathlib import Path
import struct
params={
4:(-364597865,-2043337015),
5:(678569981,-1391043752),
6:(-1977528279,-2051187129),
7:(2040317745,-394795464),
8:(-762388767,559248657),
}
b=Path('constants_blob.bin').read_bytes()
for line in Path('constant_ids.tsv').read_text().splitlines():
 t,id_=map(int,line.split())
 mul,x=params[t]; u=((id_&0xffffffff)*(mul&0xffffffff)&0xffffffff)^(x&0xffffffff)
 typ=u>>30; off=(u&0x3fffffff)<<2
 n=struct.unpack_from('<I',b,off)[0]
 raw=b[off+4:off+4+n]
 try: val=raw.decode('utf8')
 except: val=raw.hex()
 print(f'{t}\t{id_}\ttype={typ}\toff=0x{off:x}\t{val}')
