#!/usr/bin/env python3
"""Extract and decrypt Confuser constants data from the recovered DotnetProto payload."""
import lzma, struct
from pathlib import Path
import pefile
src=Path('donut_module.bin'); data=src.read_bytes(); pe=pefile.PE(data=data)
enc=list(struct.unpack('<336I',data[pe.get_offset_from_rva(0x2050):][:336*4]))
state=(-111125465)&0xffffffff
key=[]
for _ in range(16):
    state ^= state >> 12
    state ^= (state << 25)&0xffffffff
    state ^= state >> 27
    state &= 0xffffffff
    key.append(state)
out=[]
for pos in range(0,len(enc),16):
    block=enc[pos:pos+16]
    plain=[x^k for x,k in zip(block,key)]
    out.extend(plain)
    # The initializer chains the key by XORing it with each plaintext word,
    # which is equivalent to replacing it with the ciphertext block.
    key=block
packed=struct.pack('<%dI'%len(out),*out)
Path('constants_lzma.bin').write_bytes(packed)
prop=packed[0]; dsz=int.from_bytes(packed[1:5],'little'); outlen=int.from_bytes(packed[5:9],'little',signed=True)
lc=prop%9; tmp=prop//9; lp=tmp%5; pb=tmp//5
flt=[{'id':lzma.FILTER_LZMA1,'dict_size':dsz,'lc':lc,'lp':lp,'pb':pb}]
z=lzma.LZMADecompressor(format=lzma.FORMAT_RAW,filters=flt)
blob=z.decompress(packed[9:],max_length=outlen)
assert len(blob)==outlen,(len(blob),outlen)
Path('constants_blob.bin').write_bytes(blob)
print(f'packed={len(packed)} prop=0x{prop:02x} dict=0x{dsz:x} output={len(blob)}')
