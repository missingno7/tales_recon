/* m68k.c - memory, entry and interrupt glue for the translated 68000 assembly (m68k.h). */
#include <string.h>

#include "m68k.h"
#include "amiga.h"

struct m68k_state m68k;

/* ---- memory: the regions the guest owns - the DATA hunk and the exec arena in host
   order, the tables and the 68000 stack big-endian - and the custom chips. An access
   anywhere else (a stream read through bytes that are not a pointer) reads 0 and is
   logged: the Amiga reads bus noise there and carries on, the host would fault. ---- */
static struct { uintptr_t start, end; int big; } regions[32];
static int region_count;

void m68k_memory(void *start, uint32_t size, int big_endian)
{
    if (region_count < 32) {
        regions[region_count].start = (uintptr_t)start;
        regions[region_count].end = (uintptr_t)start + size;
        regions[region_count++].big = big_endian;
    }
}

void m68k_big_endian(void *start, uint32_t size) { m68k_memory(start, size, 1); }

/* The registered guest memory, for state-dump layouts: region i (0 when there is none). */
int m68k_region_info(int i, uint32_t *start, uint32_t *size)
{
    if (i < 0 || i >= region_count) return 0;
    *start = (uint32_t)regions[i].start;
    *size = (uint32_t)(regions[i].end - regions[i].start);
    return 1;
}

/* 1: big-endian, 0: host order, -1: not guest memory. Big-endian regions lie inside the
   DATA hunk, so they are found first. */
static int region(uint32_t address, uint32_t size)
{
    int found = -1;
    for (int i = 0; i < region_count; i++)
        if (address >= regions[i].start && address + size <= regions[i].end) {
            if (regions[i].big) return 1;
            found = 0;
        }
    return found;
}

static uint32_t outside(uint32_t address, const char *access)
{
    static int reported;
    if (reported < 16) {
        reported++;
        platform_log("m68k: %s outside guest memory at %08X: reads 0, writes are dropped", access, address);
    }
    platform_fault("guest memory access outside the game's memory");   /* ends a --strict run */
    return 0;
}

static int custom(uint32_t address) { return address >= 0xDFF000u && address < 0xDFF200u; }

/* The CIAs, as far as the game reads them: CIA-A (odd addresses) PRA bit 7 is the port 2 fire
   button, active low; the other bits read as inactive. CIA-B and the other registers read as
   idle (all ones). */
static int cia(uint32_t address) { return address >= 0xBFD000u && address < 0xBFF000u; }

static uint32_t cia_read8(uint32_t address)
{
    if ((address & 1) && address >= 0xBFE000u && ((address >> 8) & 0xF) == 0) {
        platform_poll();                  /* the input poll reads the fire bit before JOY1DAT */
        return platform_fire() ? 0x7F : 0xFF;
    }
    return 0xFF;
}

/* A hardware register read from the game's C code (port_gen translates dereferences of
   custom chip and CIA addresses into it). */
uint16_t amiga_read16(uint32_t address) { return (uint16_t)m68k_rd16(address); }

uint32_t m68k_rd8(uint32_t address)
{
    if (cia(address)) return cia_read8(address);
    if (custom(address)) {
        uint32_t word = custom_read16((address & ~1u) - 0xDFF000u);
        return address & 1 ? word & 0xFF : word >> 8;
    }
    if (region(address, 1) < 0) return outside(address, "read");
    return *(const uint8_t *)(uintptr_t)address;
}

uint32_t m68k_rd16(uint32_t address)
{
    const uint8_t *p = (const uint8_t *)(uintptr_t)address;
    uint16_t value;
    int kind;
    if (custom(address)) return custom_read16(address - 0xDFF000u);
    if (cia(address)) return cia_read8(address) << 8 | cia_read8(address + 1);
    if ((kind = region(address, 2)) < 0) return outside(address, "read");
    if (kind) return (uint32_t)p[0] << 8 | p[1];
    memcpy(&value, p, 2);
    return value;
}

uint32_t m68k_rd32(uint32_t address)
{
    const uint8_t *p = (const uint8_t *)(uintptr_t)address;
    uint32_t value;
    int kind;
    if (custom(address)) return custom_read16(address - 0xDFF000u) << 16 | custom_read16(address + 2 - 0xDFF000u);
    if ((kind = region(address, 4)) < 0) return outside(address, "read");
    if (kind) return (uint32_t)p[0] << 24 | (uint32_t)p[1] << 16 | (uint32_t)p[2] << 8 | p[3];
    memcpy(&value, p, 4);
    return value;
}

void m68k_wr8(uint32_t address, uint32_t value)
{
    if (custom(address)) { platform_log("byte write to custom %X", address); return; }
    if (region(address, 1) < 0) { outside(address, "write"); return; }
    *(uint8_t *)(uintptr_t)address = (uint8_t)value;
}

void m68k_wr16(uint32_t address, uint32_t value)
{
    uint8_t *p = (uint8_t *)(uintptr_t)address;
    uint16_t v = (uint16_t)value;
    int kind;
    if (custom(address)) { custom_write16(address - 0xDFF000u, v); return; }
    if ((kind = region(address, 2)) < 0) { outside(address, "write"); return; }
    if (kind) { p[0] = (uint8_t)(v >> 8); p[1] = (uint8_t)v; return; }
    memcpy(p, &v, 2);
}

void m68k_wr32(uint32_t address, uint32_t value)
{
    uint8_t *p = (uint8_t *)(uintptr_t)address;
    int kind;
    if (custom(address)) {
        custom_write16(address - 0xDFF000u, value >> 16);
        custom_write16(address + 2 - 0xDFF000u, value & 0xFFFF);
        return;
    }
    if ((kind = region(address, 4)) < 0) { outside(address, "write"); return; }
    if (kind) { m68k_put_be32(p, value); return; }
    memcpy(p, &value, 4);
}

void m68k_bad_entry(uint32_t pc)
{
    platform_log("m68k: no translated code at %08X", pc);
}

/* ---- entries: a 68000 stack of our own; everything runs on the game thread (main.c) ---- */
static uint8_t stack[16384] __attribute__((aligned(4)));
static int depth;

extern char amiga_data_hunk[];

static void enter(struct m68k_state *saved)
{
    static int registered;
    if (!registered) { registered = 1; m68k_big_endian(stack, sizeof stack); }
    *saved = m68k;
    if (depth++ == 0) A(7) = (uint32_t)(uintptr_t)(stack + sizeof stack - 16);
    A(4) = (uint32_t)(uintptr_t)amiga_data_hunk + 0x7FFE;     /* Aztec small data: A4 */
}

static uint32_t leave(const struct m68k_state *saved)
{
    uint32_t result = D(0);
    m68k = *saved;
    depth--;
    return result;
}

uint32_t m68k_entry(uint32_t pc, const char *widths, const uint32_t *args)
{
    struct m68k_state saved;
    uint32_t pushed = 0;
    if (pc == 0x57D2u)                                     /* play_sound: a sound command */
        platform_event("sound", args[0] & 0xFFFF);
    enter(&saved);
    for (int i = (int)strlen(widths) - 1; i >= 0; i--)
        if (widths[i] == 'w') { A(7) -= 2; m68k_wr16(A(7), args[i]); pushed += 2; }
        else { A(7) -= 4; m68k_wr32(A(7), args[i]); pushed += 4; }
    m68k_push32(0);
    m68k_run(pc);
    A(7) += pushed;
    return leave(&saved);
}

uint32_t m68k_interrupt(uint32_t code, uint32_t data, uint32_t a0)
{
    struct m68k_state saved;
    enter(&saved);
    A(0) = a0; A(1) = data; A(5) = code;
    m68k_push32(0);
    m68k_run(code);
    return leave(&saved);
}
