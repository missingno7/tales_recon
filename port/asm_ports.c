/* asm_ports.c - port versions of reconstructed 68000 assembly that tools/asm_port.py leaves
   out (asm_port.PORT_C_VERSIONS). Everything else - the audio driver, the Paula interrupt
   handlers, the VBlank server and its colour callbacks - is translated from the assembly
   itself (build/port-gen/asm_code.c on port/m68k.h); BltMaskBitMapRastPort's glue is in
   os_graphics.c. */
#include "aztec.h"
#include "amiga.h"
#include <string.h>

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
