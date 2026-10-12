#!/usr/bin/env python3
from pathlib import Path
raw = bytes.fromhex('''
4d62696e 1e676963 6c1e5f68 5f6a676d
576d1e5f 68521e62 536a6a1e 6256531e
636d536c 1e625653 1e506a5f 511e576d
1e5d6d5f 6165216c 6323212d 52596323
2d6c5922 5c63232d 59502c51 626c222d
5c7bfe
''')
key = bytes(((b ^ 0x0a) + 0x0c) & 0xff for b in raw)
print(len(raw), key, key.hex())
import pefile
p=pefile.PE('extracted/vcheck.exe')
for t in p.DIRECTORY_ENTRY_RESOURCE.entries:
 if t.id==10:
  d=t.directory.entries[0].directory.entries[0].data.struct
  r=bytearray(p.get_data(d.OffsetToData,d.Size))
  Path('resource101.bin').write_bytes(r)
  for i in range(len(r)-0xf0): r[0xf0+i]^=key[i%len(key)]
  Path('resource101_dec.bin').write_bytes(r)
  Path('stage1.bin').write_bytes(r[0xf0:])
