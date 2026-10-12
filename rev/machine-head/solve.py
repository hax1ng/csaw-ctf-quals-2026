#!/usr/bin/env python3
from z3 import *
bin=open('masterkey','rb').read()
code=bin[0x2040:0x27ba]
flag=[BitVec(f'f{i}',8) for i in range(53)]
regs=[BitVecVal(0,8) for _ in range(8)]
s=Solver()
# likely printable flag
for x in flag:
    s.add(x >= 0x20, x <= 0x7e)
ops={0x91:'LOAD',0x7a:'XOR_IMM',0x24:'ADD_IMM',0x1d:'MUL_IMM',0x4e:'XOR_REG',0x6d:'ADD_REG',0xb2:'ROL',0xa7:'CMP',0xe0:'END'}
for pc in range(0,len(code),3):
    op,a,b=code[pc:pc+3]
    # print(f'{pc+0x2040:04x}: {ops.get(op,hex(op)):8} {a:02x}, {b:02x}')
    if op==0x91: regs[a]=flag[b]
    elif op==0x7a: regs[a]=regs[a]^b
    elif op==0x24: regs[a]=regs[a]+b
    elif op==0x1d: regs[a]=regs[a]*b
    elif op==0x4e: regs[a]=regs[a]^regs[b]
    elif op==0x6d: regs[a]=regs[a]+regs[b]
    elif op==0xb2: regs[a]=RotateLeft(regs[a],b)
    elif op==0xa7: s.add(regs[a]==b)
    elif op==0xe0: break
    else: raise ValueError((pc,op,a,b))
print('checks',len(s.assertions()))
print(s.check())
m=s.model()
ans=bytes(m.eval(x).as_long() for x in flag)
print(ans)
# ensure unique
s.add(Or(*[x != m.eval(x) for x in flag])); print('another?',s.check())
