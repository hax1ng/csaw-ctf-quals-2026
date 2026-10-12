import sys
data=open('session.bin','rb').read()
KB=data[248:]; PB0=data[:248]+bytes(8)

class VM:
    def __init__(self):
        self.kb=bytearray(KB); self.mem=bytearray(PB0)
        self.R=[0,0,0,0]; self.pc=0; self.ptr=0; self.flag=0
        self.stack=[]; self.out=bytearray(); self.inq=[]
        self.notes=[]; self.steps=0; self.fe_empty=0
    def feed(self,s): self.inq.extend(s); self.fe_empty=0
    def rd(self,a):
        if a==0xfe: return min(len(self.inq),255)
        if a==0xfd:
            return self.inq.pop(0) if self.inq else 0
        return self.mem[a]
    def wr(self,a,v):
        if a==0xff:
            self.out.append(v&255); self.fe_empty=0
        else:
            self.mem[a]=v&255
    def run(self, maxsteps=60_000_000, spin=8):
        m=self.mem; R=self.R
        while self.steps<maxsteps:
            self.steps+=1
            pc=self.pc; x=self.kb[pc]; y=self.kb[pc+1]
            op=x>>4; lo=x&15; hi=lo>>2; mode=lo&3; nxt=pc+2
            if op==0:
                if lo==1:
                    if not self.stack: return 'ret_empty'
                    nxt=self.stack.pop()
                elif lo==2: return 'halt'
            elif op in(1,2):
                idx=hi+(op-1)*4; r=mode; v=R[r]
                R[r]=[(v+y)&255,(v-y)&255,(v*y)&255,(v//y if y else 0),v&y,v^y,(v>>y)&255,(v<<y)&255][idx]
            elif op==3:
                o=(y>>4)&3; d=(y>>6)&3; a=R[d]; b=R[o]
                R[d]=[(a+b)&255,(a-b)&255,(a*b)&255,(a//b if b else 0),a&b,a^b,(a>>(b&7))&255,(a<<(b&7))&255,a|b,(a%b if b else 0)][lo] if lo<10 else a
            elif op==4:
                if mode==0: R[hi]=y
                elif mode==1:
                    pr=y&3; a=R[pr]; R[hi]=self.rd(a)
                    if y&4: R[pr]=(a+1)&255
                elif mode==2:
                    a=y
                    if a==0xfe:
                        n=min(len(self.inq),255); R[hi]=n
                        if n==0:
                            self.fe_empty+=1
                            if self.fe_empty>spin: self.pc=pc; return 'need_input'
                        else: self.fe_empty=0
                    else: R[hi]=self.rd(a)
                elif mode==3: R[hi]=self.rd(self.mem[y])
            elif op==5:
                if mode in(0,2): self.wr(y,R[hi])
                elif mode==1:
                    pr=y&3; a=R[pr]; self.wr(a,R[hi])
                    if y&4: R[pr]=(a+1)&255
                elif mode==3: self.wr(self.mem[y],R[hi])
            elif op==6:
                v=R[mode]; self.flag=[v==y,v!=y,v>y,v>=y][hi]
            elif op==7:
                r2=y&3; v=R[mode]; w=R[r2]; self.flag=[v==w,v!=w,v>w,v>=w][hi]
            elif op==8:
                if lo==0: self.ptr=y
                elif lo==1: self.wr(self.ptr,y)
            elif op in(9,10,11): self.notes.append((op,lo,y,list(R)))
            elif op==12: nxt=(lo<<8)|y
            elif op==13: nxt=((lo<<8)|y) if self.flag else nxt
            elif op==14: nxt=((lo<<8)|y) if not self.flag else nxt
            elif op==15: self.stack.append(nxt); nxt=(lo<<8)|y
            self.pc=nxt
        return 'maxsteps'

def session(cmds):
    vm=VM(); vm.run()
    for c in cmds:
        vm.feed(list((c+'\n').encode())); vm.run()
    return vm

def render_of(cmds):
    vm=session(cmds); t=bytes(vm.out).decode('latin1')
    if 'rendering stem ...' in t:
        after=t.split('rendering stem ...',1)[1]
        for line in after.split('\n'):
            if line.strip(): return line.strip()
    return None

if __name__=='__main__':
    base=["CUE IKOW[g","SYNC","EQ music'_'","KEY 4d5344213799"]
    for arg in ["9a3faa","9a3f00","9a3fZZ","AAAAAAAA","9a3f000000","DEADBEEF"]:
        r=render_of(base+["EXPORT "+arg])
        print("arg=%-12s render=%r"%(arg,r))
    # validate HELP still works
    v=session(["HELP"]); print("HELP ok:", b'this list' in bytes(v.out))
