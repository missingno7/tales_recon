/* asm_ports.c - C versions of the game's reconstructed 68000 assembly
   (src/recovered/asm-reconstructed/, RECONSTRUCTED_ASM) that the port needs.

   Ported: the VBlank server (resident_frameless_615E), its callback bridge
   (resident_callback_617C) and the palette-cycling callback (resident_callback_61A0).
   Not yet ported: the audio driver (resident_driver_*, the Paula IRQ handlers
   resident_frameless_55D6/5646/56B6/5726, the sound-command entry 57D2) - the port is
   silent until it is, and each entry reports itself once when it is reached. The game's
   own waits on the driver (G_h01_2A16 == 0) pass, since nothing plays. */
#include "aztec.h"
#include "amiga.h"
#include <string.h>

extern int32_t G_h01_B1EC;                         /* game tick */
extern struct View G_h01_53A2;                     /* the game's View (A4 - 0x2c5c) */

/* ---- palette cycling (resident_callback_617C / 61A0) ---- */
#pragma pack(push, 2)
struct cprlist { struct cprlist *Next; uint16_t *start; int16_t MaxCount; };
struct cycle { uint16_t *colours; uint16_t count; uint16_t offset; };   /* DP_Cycle */
#pragma pack(pop)

typedef void (*cycle_callback)(uint16_t *copper_colours);
extern cycle_callback G_h01_2BC2[5];               /* per-scene callback, index G_h01_2C26 */
extern struct cycle G_h01_2BFE[5];
extern int32_t G_h01_2C26;
extern int8_t G_h01_2C2A;                          /* countdown */
extern uint8_t G_h01_2C2B;                         /* cycle position */
extern uint8_t G_h01_2C2C;                         /* speed */

/* 619E: rts (scene without colour cycling). */
void recon_h00_619E(uint16_t *copper_colours) { (void)copper_colours; }

/* 61A0: every time the countdown underflows (step G_h01_2C2C per frame) the cycle position
   moves back by one, wrapping to the record's count, and count + 1 colours from that
   position are written into the copper list's colour MOVEs (every second word) from the
   record's first register on. */
void recon_h00_61A0(uint16_t *copper_colours)
{
    const struct cycle *record;
    int16_t position;
    const uint16_t *source;
    uint16_t *target;
    G_h01_2C2A = (int8_t)(G_h01_2C2A - (int8_t)G_h01_2C2C);
    if (G_h01_2C2A >= 0)
        return;
    G_h01_2C2A = 0x7f;
    record = &G_h01_2BFE[G_h01_2C26];
    position = (int16_t)G_h01_2C2B - 1;
    if (position < 0)
        position = (int16_t)record->count;
    G_h01_2C2B = (uint8_t)position;
    source = (const uint16_t *)((const uint8_t *)record->colours + ((position << 1) & 0xff));
    target = copper_colours + 2 * record->offset;
    for (int n = 0; n <= record->count; n++) {
        *target = *source++;
        target += 2;
    }
}

/* 617C: the colour words of the View's long-frame copper list start 6 bytes in (the
   value of instruction 1, COLOR00); call the scene's callback with them. */
static void callback_bridge(void)
{
    struct cprlist *list = G_h01_53A2.LOFCprList;
    if (list && list->start)
        G_h01_2BC2[G_h01_2C26]((uint16_t *)((uint8_t *)list->start + 6));
}

/* ---- the audio driver: not yet ported ---- */
static void audio_frame(void) { /* resident_driver_58BC: per-frame score update */ }

/* 615E: the VBlank server - tick, colour cycling, audio frame; returns 0 (Z set) so the
   next server in the chain runs. */
int32_t recon_h00_615E(void)
{
    G_h01_B1EC++;
    callback_bridge();
    audio_frame();
    return 0;
}

/* 701A: kprintf(format, ...) - exec RawDoFmt with kputchar (6FDE) to the serial port. Here
   the text goes to the log. RawDoFmt: %d/%u/%x/%c take a 16-bit word, %ld/%lx a long, %s a
   string; in the port every argument occupies a 4-byte slot. */
#include <stdarg.h>
#include <stdio.h>
int16_t recon_h00_701A(const char *format, ...)
{
    char out[512];
    size_t n = 0;
    va_list args;
    va_start(args, format);
    for (const char *f = format; *f && n < sizeof out - 32; f++) {
        char spec[16];
        size_t k = 0;
        int is_long = 0;
        if (*f != '%') { out[n++] = *f; continue; }
        spec[k++] = *f++;
        while (*f && strchr("-0123456789.", *f) && k < 10) spec[k++] = *f++;
        if (*f == 'l') { is_long = 1; f++; }
        if (!*f) break;
        spec[k++] = *f == 'u' ? 'u' : *f; spec[k] = 0;
        if (*f == 's') n += (size_t)snprintf(out + n, sizeof out - n, spec, va_arg(args, const char *));
        else if (*f == '%') out[n++] = '%';
        else {
            int32_t v = va_arg(args, int32_t);
            if (!is_long) v = *f == 'd' ? (int16_t)v : (uint16_t)v;
            n += (size_t)snprintf(out + n, sizeof out - n, spec, v);
        }
    }
    va_end(args);
    out[n < sizeof out ? n : sizeof out - 1] = 0;
    if (n && out[n - 1] == '\n') out[n - 1] = 0;
    platform_log("kprintf: %s", out);
    return 0;
}

/* Sound command (57D2 -> 57E4): silent until the driver is ported. */
int16_t recon_h00_57D2(int16_t command) { (void)command; return 0; }

#define PENDING(name) int16_t name(void) { platform_unimplemented(#name); return 0; }
PENDING(recon_h00_544C) PENDING(recon_h00_5594) PENDING(recon_h00_55D6) PENDING(recon_h00_5646)
PENDING(recon_h00_56B6) PENDING(recon_h00_5726) PENDING(recon_h00_579E) PENDING(recon_h00_57B6)
PENDING(recon_h00_5868) PENDING(recon_h00_5ACA) PENDING(recon_h00_5B06) PENDING(recon_h00_5B20)
PENDING(recon_h00_5B26) PENDING(recon_h00_5B3A) PENDING(recon_h00_5B62) PENDING(recon_h00_5B8C)
PENDING(recon_h00_5BAA) PENDING(recon_h00_5BBC) PENDING(recon_h00_5BC6) PENDING(recon_h00_5BE6)
PENDING(recon_h00_5C6A) PENDING(recon_h00_5C90) PENDING(recon_h00_5CB6) PENDING(recon_h00_5CC6)
PENDING(recon_h00_5CD6) PENDING(recon_h00_5CDE) PENDING(recon_h00_5D08) PENDING(recon_h00_5D1E)
PENDING(recon_h00_5D44) PENDING(recon_h00_5D5A) PENDING(recon_h00_5D62) PENDING(recon_h00_5D78)
PENDING(recon_h00_5D92) PENDING(recon_h00_5D98) PENDING(recon_h00_5DA0) PENDING(recon_h00_5DA4)
PENDING(recon_h00_5DAC) PENDING(recon_h00_5DB4) PENDING(recon_h00_5DBC) PENDING(recon_h00_5DC6)
PENDING(recon_h00_5DD0) PENDING(recon_h00_5DDA) PENDING(recon_h00_5DF6) PENDING(recon_h00_5DFE)
PENDING(recon_h00_5E64) PENDING(resident_asm_559E)

/* Typed CODE-data the driver reads (src/recovered/code-data/audio5.asm): the complete
   selector table; filled when the CODE-data tables are translated with the driver. */
uint32_t G_h00_6200_complete[176];
