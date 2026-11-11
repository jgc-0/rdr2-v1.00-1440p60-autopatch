typedef unsigned char u8; typedef unsigned int u32; typedef unsigned long long u64;
#define H_ __attribute__((visibility("hidden")))
extern int cmd(u32, const void*, u32) H_;
extern int expect_success(void) H_;
extern int proc_read(u32, u64, void*, u32) H_;
extern int g_sock H_;
extern long (*p_send)(int, const void*, unsigned long, int) H_;

static int wr(u32 pid, u64 a, const void* p, u32 n) {
    u32 h[4] = { pid, (u32)a, (u32)(a >> 32), n };
    if (cmd(0xbdaa0003, h, 16) || expect_success()) return -1;
    for (u32 o = 0; o < n;) { long r = p_send(g_sock, (const u8*)p + o, n - o, 0); if (r <= 0) return -2; o += (u32)r; }
    return expect_success() ? -3 : 0;
}
#ifdef WITH60
__attribute__((noinline, section(".text.p60"))) int p60(u32 pid, u64 base) {
    const u64 a = base + 0x468ee1f; u8 c[4];
    if (proc_read(pid, a, c, 3)) return -5;
    if (c[0] == 0x31 && c[2] == 0x90) return 0;
    if (!(c[0] == 0x0f && c[1] == 0x44 && c[2] >= 0xc0)) return -6;
    const u8 n[3] = { 0x31, (u8)(0xc0 + 9 * ((c[2] >> 3) & 7)), 0x90 };
    return wr(pid, a, n, 3);
}
#endif
#define RANGE 0x223
struct __attribute__((packed)) X { u32 off; u8 n; u8 d[7]; };
struct __attribute__((packed)) TAB { u8 wh[30]; u8 cb[15]; struct X xs[2]; };
__attribute__((section(".text.tab"))) static const struct TAB T = {
    /* 0x960ef2: movabs rax,(1440<<32|2560); mov [r12+0x160],rax; mov [r14+0x94],rax; nop*5 */
    { 0x48,0xb8, 0x00,0x0a,0,0, 0xa0,0x05,0,0, 0x49,0x89,0x84,0x24,0x60,0x01,0,0, 0x49,0x89,0x86,0x94,0,0,0, 0x90,0x90,0x90,0x90,0x90 },
    /* 0x961106: mov byte [r12+0xf7],0; nop*6 */
    { 0x41,0xc6,0x84,0x24,0xf7,0,0,0,0, 0x90,0x90,0x90,0x90,0x90,0x90 },
    { { 0x34fef6, 7, { 0x31, 0xc0, 0x90, 0x90, 0x90, 0x90, 0x90 } },   /* settings-apply: runtime CB flag <- 0 */
      { 0x7282634, 1, { 0 } } },                                       /* runtime CB flag global */
};
int patch_entry(u32 pid, u64 base) {
    u8 b[RANGE + 5]; u64 a = base + 0x560ef2;
    if (proc_read(pid, a, b, RANGE)) return -1;
    if (b[0] != 0x41 || b[2] != 0x84 || b[0x214] != 0x74 || b[0x215] != 0x0d) return -2;
    for (int i = 0; i < 30; i++) b[i] = T.wh[i];
    for (int i = 0; i < 15; i++) b[0x214 + i] = T.cb[i];
    int rc = wr(pid, a, b, RANGE);
    for (int i = 0; i < 2 && !rc; i++) rc = wr(pid, base + T.xs[i].off, T.xs[i].d, T.xs[i].n);
#ifdef WITH60
    if (!rc && p60(pid, base)) rc = -5;
#endif
    return rc ? -3 : 0;
}
