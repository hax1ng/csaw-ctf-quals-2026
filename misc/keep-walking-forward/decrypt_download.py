#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys
ct=Path('http_export/version-helper').read_bytes()
# Stage 1 calls GetComputerNameExA(ComputerNameDnsDomain), so the input is the
# DNS domain, not the host name/FQDN.  The other values are retained as useful
# negative controls for the reverse-engineering result.
for host in ['evermore.internal','DESKTOP-M919A7K.evermore.internal',
             'desktop-m919a7k.evermore.internal','DESKTOP-M919A7K',
             'desktop-m919a7k']:
 src=host.encode()[:32]
 k=bytearray(32)
 prev=0
 for i in range(32):
  k[i]=((src[i%len(src)]*0x83)&0xff)^prev
  prev=k[i]
 pt=bytes(c^k[i%32] for i,c in enumerate(ct))
 name='download_dec_'+host.replace('.','_')+'.bin'
 Path(name).write_bytes(pt)
 print(host,'len',len(host),len(src),'key',k.hex(),'head',pt[:32].hex(),'sha256',hashlib.sha256(pt).hexdigest())
 if host == 'evermore.internal':
  assert pt[0] == 0xe8 and int.from_bytes(pt[5:9], 'little') == 0xfdc0
  Path('stage2.bin').write_bytes(pt)
