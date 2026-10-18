/* m68k.h - what the translated 68000 assembly runs on (tools/asm_port.py, docs/sdl3-port.md).

   The reconstructed assembly (audio driver, Paula interrupt handlers, VBlank server and
   colour callbacks) is translated instruction by instruction into C on this register file.
   Addresses are host addresses (the port is a 32-bit build). Memory is the game's own:
   the DATA hunk and the heap hold host-order values written by the C code, so they are
   read and written in host order; the TYPED_CODE_DATA tables keep the 68000's big-endian
   bytes and are registered as big-endian regions; 0xDFF000-0xDFF1FF is the custom chip
   set (Paula). A code address is M68K_CODE_BASE + its original CODE offset: the DATA
   hunk's code pointers (`recon_h00_544C + 200`) and the Interrupt structures hold such
   keys, and m68k_run() dispatches them to the translated code. */
#ifndef M68K_H
#define M68K_H
#include <stdint.h>
#include <string.h>

#define M68K_CODE_BASE 0x70000000u

struct m68k_state {
    uint32_t d[8], a[8];
    int x, n, z, v, c;
};
extern struct m68k_state m68k;
#define D(i) m68k.d[i]
#define A(i) m68k.a[i]

/* memory */
uint32_t m68k_rd8(uint32_t address);
uint32_t m68k_rd16(uint32_t address);
uint32_t m68k_rd32(uint32_t address);
void m68k_wr8(uint32_t address, uint32_t value);
void m68k_wr16(uint32_t address, uint32_t value);
void m68k_wr32(uint32_t address, uint32_t value);
void m68k_memory(void *start, uint32_t size, int big_endian);   /* register guest memory */
void m68k_big_endian(void *start, uint32_t size);   /* register a big-endian region */
static inline void m68k_put_be32(void *at, uint32_t value)
{
    uint8_t *p = (uint8_t *)at;
    p[0] = (uint8_t)(value >> 24); p[1] = (uint8_t)(value >> 16); p[2] = (uint8_t)(value >> 8); p[3] = (uint8_t)value;
}
static inline void m68k_push32(uint32_t value) { A(7) -= 4; m68k_wr32(A(7), value); }

/* control: run the translated code at a code address until its rts */
void m68k_run(uint32_t pc);                          /* generated (asm_code.c) */
void m68k_bad_entry(uint32_t pc);
static inline int m68k_is_code(uint32_t address) { return address >= M68K_CODE_BASE && address < M68K_CODE_BASE + 0x10000u; }

/* entry from the port: C calls (arguments pushed as Aztec C pushes them: 'w' 16-bit,
   'l' 32-bit, right to left) and interrupts (a1 = is_Data, a5 = is_Code). Both return d0
   and leave the caller's registers as they were. All entries come from the game thread
   (main.c), as the Amiga ran them on one CPU. */
uint32_t m68k_entry(uint32_t pc, const char *widths, const uint32_t *args);
uint32_t m68k_interrupt(uint32_t code, uint32_t data, uint32_t a0);
void asm_tables_init(void);                          /* generated (asm_tables.c) */

/* condition codes */
#define M68K_MASK(s) ((s) == 1 ? 0xFFu : (s) == 2 ? 0xFFFFu : 0xFFFFFFFFu)
#define M68K_MSB(s) ((s) == 1 ? 0x80u : (s) == 2 ? 0x8000u : 0x80000000u)

static inline uint32_t m68k_logic(uint32_t r, int s)
{
    r &= M68K_MASK(s);
    m68k.n = (r & M68K_MSB(s)) != 0; m68k.z = r == 0; m68k.v = m68k.c = 0;
    return r;
}
static inline uint32_t m68k_add(uint32_t d, uint32_t s, int size)
{
    uint32_t m = M68K_MASK(size), r;
    d &= m; s &= m; r = (d + s) & m;
    m68k.c = m68k.x = size == 4 ? r < d : (d + s) > m;
    m68k.v = ((~(d ^ s) & (d ^ r)) & M68K_MSB(size)) != 0;
    m68k.n = (r & M68K_MSB(size)) != 0; m68k.z = r == 0;
    return r;
}
static inline uint32_t m68k_sub(uint32_t d, uint32_t s, int size)
{
    uint32_t m = M68K_MASK(size), r;
    d &= m; s &= m; r = (d - s) & m;
    m68k.c = m68k.x = s > d;
    m68k.v = (((d ^ s) & (d ^ r)) & M68K_MSB(size)) != 0;
    m68k.n = (r & M68K_MSB(size)) != 0; m68k.z = r == 0;
    return r;
}
static inline void m68k_cmp(uint32_t d, uint32_t s, int size)
{
    int x = m68k.x;
    m68k_sub(d, s, size);
    m68k.x = x;
}
static inline uint32_t m68k_lsl(uint32_t v, uint32_t count, int size)
{
    uint32_t bits = (uint32_t)size * 8, m = M68K_MASK(size);
    v &= m;
    if (count) {
        m68k.c = m68k.x = count <= bits ? (v >> (bits - count)) & 1 : 0;
        v = count >= bits ? 0 : (v << count) & m;
    } else m68k.c = 0;
    m68k.v = 0; m68k.n = (v & M68K_MSB(size)) != 0; m68k.z = v == 0;
    return v;
}
static inline uint32_t m68k_lsr(uint32_t v, uint32_t count, int size)
{
    uint32_t bits = (uint32_t)size * 8;
    v &= M68K_MASK(size);
    if (count) {
        m68k.c = m68k.x = count <= bits ? (v >> (count - 1)) & 1 : 0;
        v = count >= bits ? 0 : v >> count;
    } else m68k.c = 0;
    m68k.v = 0; m68k.n = (v & M68K_MSB(size)) != 0; m68k.z = v == 0;
    return v;
}
static inline uint32_t m68k_roxl(uint32_t v, uint32_t count, int size)
{
    uint32_t m = M68K_MASK(size);
    v &= m;
    for (uint32_t i = 0; i < count; i++) {
        int out = (v & M68K_MSB(size)) != 0;
        v = ((v << 1) | (uint32_t)m68k.x) & m;
        m68k.x = out;
    }
    m68k.c = m68k.x; m68k.v = 0; m68k.n = (v & M68K_MSB(size)) != 0; m68k.z = v == 0;
    return v;
}
static inline uint32_t m68k_roxr(uint32_t v, uint32_t count, int size)
{
    uint32_t m = M68K_MASK(size);
    v &= m;
    for (uint32_t i = 0; i < count; i++) {
        int out = v & 1;
        v = (v >> 1) | (m68k.x ? M68K_MSB(size) : 0);
        m68k.x = out;
    }
    m68k.c = m68k.x; m68k.v = 0; m68k.n = (v & M68K_MSB(size)) != 0; m68k.z = v == 0;
    return v;
}

/* the custom chips (paula.c) */
uint32_t custom_read16(uint32_t offset);
void custom_write16(uint32_t offset, uint32_t value);
#endif
