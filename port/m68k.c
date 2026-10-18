/* m68k.c - memory, entry and interrupt glue for the translated 68000 assembly (m68k.h). */
#include <SDL3/SDL.h>

#include "m68k.h"
#include "amiga.h"

struct m68k_state m68k;

/* ---- memory: host order, except the registered big-endian regions and the chips ---- */
static struct { uintptr_t start, end; } regions[16];
static int region_count;

void m68k_big_endian(void *start, uint32_t size)
{
    if (region_count < 16) {
        regions[region_count].start = (uintptr_t)start;
        regions[region_count++].end = (uintptr_t)start + size;
    }
}

static int big_endian(uint32_t address)
{
    for (int i = 0; i < region_count; i++)
        if (address >= regions[i].start && address < regions[i].end) return 1;
    return 0;
}

static int custom(uint32_t address) { return address >= 0xDFF000u && address < 0xDFF200u; }

uint32_t m68k_rd8(uint32_t address)
{
    if (custom(address)) {
        uint32_t word = custom_read16((address & ~1u) - 0xDFF000u);
        return address & 1 ? word & 0xFF : word >> 8;
    }
    return *(const uint8_t *)(uintptr_t)address;
}

uint32_t m68k_rd16(uint32_t address)
{
    const uint8_t *p = (const uint8_t *)(uintptr_t)address;
    uint16_t value;
    if (custom(address)) return custom_read16(address - 0xDFF000u);
    if (big_endian(address)) return (uint32_t)p[0] << 8 | p[1];
    memcpy(&value, p, 2);
    return value;
}

uint32_t m68k_rd32(uint32_t address)
{
    const uint8_t *p = (const uint8_t *)(uintptr_t)address;
    uint32_t value;
    if (custom(address)) return custom_read16(address - 0xDFF000u) << 16 | custom_read16(address + 2 - 0xDFF000u);
    if (big_endian(address)) return (uint32_t)p[0] << 24 | (uint32_t)p[1] << 16 | (uint32_t)p[2] << 8 | p[3];
    memcpy(&value, p, 4);
    return value;
}

void m68k_wr8(uint32_t address, uint32_t value)
{
    if (custom(address)) { platform_log("byte write to custom %X", address); return; }
    *(uint8_t *)(uintptr_t)address = (uint8_t)value;
}

void m68k_wr16(uint32_t address, uint32_t value)
{
    uint8_t *p = (uint8_t *)(uintptr_t)address;
    uint16_t v = (uint16_t)value;
    if (custom(address)) { custom_write16(address - 0xDFF000u, v); return; }
    if (big_endian(address)) { p[0] = (uint8_t)(v >> 8); p[1] = (uint8_t)v; return; }
    memcpy(p, &v, 2);
}

void m68k_wr32(uint32_t address, uint32_t value)
{
    uint8_t *p = (uint8_t *)(uintptr_t)address;
    if (custom(address)) {
        custom_write16(address - 0xDFF000u, value >> 16);
        custom_write16(address + 2 - 0xDFF000u, value & 0xFFFF);
        return;
    }
    if (big_endian(address)) { m68k_put_be32(p, value); return; }
    memcpy(p, &value, 4);
}

void m68k_bad_entry(uint32_t pc)
{
    platform_log("m68k: no translated code at %08X", pc);
}

/* ---- entries: one lock (the Amiga had one CPU), a 68000 stack of our own ---- */
static SDL_Mutex *driver_lock;
static uint8_t stack[16384] __attribute__((aligned(4)));
static int depth;

void m68k_lock(void)
{
    if (!driver_lock) {
        driver_lock = SDL_CreateMutex();                    /* SDL mutexes are recursive */
        m68k_big_endian(stack, sizeof stack);
    }
    SDL_LockMutex(driver_lock);
}

void m68k_unlock(void) { SDL_UnlockMutex(driver_lock); }

extern char amiga_data_hunk[];

static void enter(struct m68k_state *saved)
{
    m68k_lock();
    *saved = m68k;
    if (depth++ == 0) A(7) = (uint32_t)(uintptr_t)(stack + sizeof stack - 16);
    A(4) = (uint32_t)(uintptr_t)amiga_data_hunk + 0x7FFE;     /* Aztec small data: A4 */
}

static uint32_t leave(const struct m68k_state *saved)
{
    uint32_t result = D(0);
    m68k = *saved;
    depth--;
    m68k_unlock();
    return result;
}

uint32_t m68k_entry(uint32_t pc, const char *widths, const uint32_t *args)
{
    struct m68k_state saved;
    uint32_t pushed = 0;
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
