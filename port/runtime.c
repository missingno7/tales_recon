/* runtime.c - the Aztec C runtime pieces the game binds by name (see the link-name
   macros of the staged units: F_h00_7978 segload, F_h00_7522 freeseg, F_h00_7A6C movmem,
   F_h00_75D8 index) and the runtime globals it references. */
#include "amiga.h"

#include <string.h>

/* Manx overlays: the Amiga build loads an overlay node from the program file before its
   functions run. The port links every node in, so loading always succeeds. */
int16_t segload(const char *name) { (void)name; return 1; }
int16_t freeseg(int32_t segment) { (void)segment; return 0; }

/* movmem(source, destination, length): Aztec argument order, overlapping-safe. */
int16_t movmem(const void *source, void *destination, uint32_t length)
{
    memmove(destination, source, (uint16_t)length);
    return 0;
}

/* index(string, c): BSD strchr. */
int32_t index(const char *string, int32_t c) { return (int32_t)(intptr_t)strchr(string, (char)c); }

/* Runtime globals: arguments as the startup stored them, the device table, errno. The
   game refers to some under the runtime's internal names (_argc, _devtab ...); those are
   DATA cells, which the DATA hunk owns (port_gen RUNTIME_CELLS). */
int16_t argc;
char **argv;
int16_t arg_len;
char *arg_lin;
uint8_t devtab[16 * 6];
int16_t aztec_errno;
extern int16_t _argc, _arg_len;
extern char **_argv, *_arg_lin;
extern int32_t MathBase;   /* mathffp.library: host floating point needs no library */

/* The runtime's internal DOS and exec glue (_Open, _AllocMem ...): the same calls. */
int32_t Open(int32_t name, int32_t mode);
int16_t Close(int32_t fh);
int32_t AllocMem(int32_t size, int32_t flags);
int16_t FreeMem(int32_t block, int32_t size);
int32_t OpenLibrary(int32_t name, int32_t version);
int16_t CloseLibrary(int32_t library);
int32_t _Open(int32_t name, int32_t mode) { return Open(name, mode); }
int16_t _Close(int32_t fh) { return Close(fh); }
int32_t _AllocMem(int32_t size, int32_t flags) { return AllocMem(size, flags); }
int16_t _FreeMem(int32_t block, int32_t size) { return FreeMem(block, size); }
int32_t _OpenLibrary(int32_t name, int32_t version) { return OpenLibrary(name, version); }
int16_t _CloseLibrary(int32_t library) { return CloseLibrary(library); }
