import struct,subprocess,sys
SRC=sys.argv[1] if len(sys.argv)>1 else 'autopatch60.elf'
def build(variant,out):
    d=bytearray(open(SRC,'rb').read())
    o=lambda v:0x4000+v   # vaddr -> file offset (LOAD0 and LOAD1 both delta 0x4000)
    def put(v,b): d[o(v):o(v)+len(b)]=bytes(b)
    def rel(frm_next,to): return struct.pack('<i',to-frm_next)
    v=1 if variant=='both' else 0
    elf='pe1.elf'
    nm=subprocess.check_output(['nm',elf]).decode()
    pe=int([l.split()[0] for l in nm.splitlines() if l.endswith(' patch_entry')][0],16)
    subprocess.check_call(['llvm-objcopy','-O','binary','-j','.text',elf,'t.bin'])
    text=open('t.bin','rb').read()
    # 1) window address (first path) and window offset (maps path): window = site1 - 0x20
    put(0x28b,struct.pack('<I',0x960ed2))
    put(0x437,struct.pack('<I',0x560ed2))
    # 1b) faster polling: scan loop 500ms->10ms, ctx retry 500ms->10ms x100
    assert d[o(0x22f)]==0xbf and d[o(0x47d)]==0xbf and d[o(0x48e)]==0x0a
    put(0x230,struct.pack('<I',10000)); put(0x47e,struct.pack('<I',10000)); put(0x48e,bytes([100]))
    # 2) stub at 0x4b6
    PE0=pe
    stub=bytearray()
    stub+=bytes([0xbe])+struct.pack('<I',0x400000)          # 4b6 mov esi,0x400000
    stub+=bytes([0x44,0x89,0xe7])                            # 4bb mov edi,r12d
    stub+=b'\xe8'+rel(0x4c3,PE0)                              # 4be call patch_entry
    stub+=bytes([0x85,0xc0])                                 # 4c3 test eax,eax
    stub+=b'\x0f\x85'+rel(0x4cb,0x689)                       # 4c5 jne 689
    T=0x4b6+len(stub)
    stub+=bytes([0x4c,0x8b,0x35])+rel(T+7,0xdb18)             # mov r14,[close]
    stub+=bytes([0xc7,0x45,0xd0,0,0,0,0])                     # mov [rbp-0x30],0
    stub+=bytes([0x48,0x8d,0x3d])+rel(T+21,0xe763)            # lea rdi,[PATCHED]
    stub+=bytes([0x4c,0x8d,0x3d])+rel(T+28,0xdd7d)            # lea r15,[msg]
    stub+=b'\xe9'+rel(T+33,0x6f5)                             # jmp 6f5
    stub+=b'\x90'*(0x4ec-0x4b6-len(stub))
    PE=0x4b6+len(stub)
    put(0x4b6,stub)
    # 3) patch_entry code region 0x4d0.. (must stay below 0x689)
    TA=int([l for l in subprocess.check_output(['readelf','-SW',elf]).decode().splitlines() if ' .text ' in l][0].split('.text')[1].split()[1],16)
    assert TA>=PE,(hex(TA),hex(PE))
    put(PE,b'\xcc'*(TA-PE))
    assert TA+len(text)<=0x689,(TA+len(text))
    put(TA,text)
    if variant=='dbg':
        for sec,addr in (('.tab',0x6b0),('.str',0x836)):
            subprocess.check_call(['llvm-objcopy','-O','binary','-j',sec,elf,'x.bin'])
            x=open('x.bin','rb').read(); put(addr,x)
    if variant!='dbg':
        subprocess.check_call(['llvm-objcopy','-O','binary','-j','.tab',elf,'x.bin']); put(0x6b0,open('x.bin','rb').read())
    if v==1 and variant!='dbg':
        subprocess.check_call(['llvm-objcopy','-O','binary','-j','.p60',elf,'p.bin'])
        p=open('p.bin','rb').read()
        # llvm-objcopy binary output starts at the section's address; .p60 is the only section dumped
        assert 0x836+len(p)<=0x8bf,(0x836+len(p))
        put(0x836,p)
    # 4) second entry hook at 0x6a7 (dead code) and redirect jne at 0x477
    hook=bytes([0x48,0x8b,0x75,0xb0])+b'\xe9'+rel(0x6ac+5-1+0,0x4bb)  # placeholder, fixed below
    h=bytearray([0x48,0x8b,0x75,0xb0,0xe9]); h+=rel(0x6a7+4+5,0x4bb)
    put(0x6a7,h)
    assert d[o(0x477):o(0x477)+2]==b'\x0f\x85'
    put(0x479,rel(0x47d,0x6a7))
    # 5) ctx_ok at 0xbc6 (69 bytes available)
    ctx=open('ctx.bin','rb').read(); assert len(ctx)<=69
    put(0xbc6,ctx+b'\xcc'*(69-len(ctx)))
    # 5b) (removed) the base payload already waits for the game to exit and then watches for the next launch, so it patches every launch
    # 6) messages
    def setstr(v,old,new,prefix=None):
        f=o(v); assert d[f:f+len(old)]==old and (prefix is None or old.startswith(prefix)),(hex(v),d[f:f+len(old)])
        assert len(new)<=len(old); d[f:f+len(old)+1]=new+b'\0'*(len(old)+1-len(new))
    if variant=='both':
        setstr(0xdd7d,bytes(d[o(0xdd7d):o(0xdd7d)+32]),b'RDR2 60fps + 1440p',b'RDR2 60fps ON')
        setstr(0xdf54,b'RDR2 60fps: target not found, not applied',b'RDR2 60fps+1440p: target not found')
        setstr(0xe3c1,b'RDR2 60fps: write failed, not applied',b'RDR2 60fps+1440p: write failed')
        setstr(0xe44b,b'RDR2 60fps: unexpected eboot, not applied',b'RDR2 60fps+1440p: unexpected eboot')
    else:
        setstr(0xdd7d,bytes(d[o(0xdd7d):o(0xdd7d)+32]),b'RDR2 1440p',b'RDR2 60fps ON')
        setstr(0xdf54,b'RDR2 60fps: target not found, not applied',b'RDR2 1440p: target not found, not applied')
        setstr(0xe3c1,b'RDR2 60fps: write failed, not applied',b'RDR2 1440p: write failed, not applied')
        setstr(0xe44b,b'RDR2 60fps: unexpected eboot, not applied',b'RDR2 1440p: unexpected eboot, not applied')
    setstr(0xe763,b'ALREADY',b'PATCHED')
    open(out,'wb').write(d)
    print(out,len(d),'patch_entry at',hex(pe),'text',len(text))
build('both','rdr2_1440p60.elf')
