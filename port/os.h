/* os.h - internal interface between the OS emulation (os_*.c) and the platform (main.c). */
#ifndef OS_H
#define OS_H

#include "amiga.h"

/* exec: interrupts and multitasking state kept by the platform */
void platform_forbid(int on);
void platform_add_server(int number, void *interrupt);      /* struct Interrupt * */
void platform_remove_server(int number, void *interrupt);
void *platform_set_vector(int number, void *interrupt);     /* returns the previous one */
void platform_input_handler(void *interrupt);               /* input.device handler, NULL = none */
void *platform_vector(int number);                          /* SetIntVector's Interrupt, or NULL */
void paula_start(void);                                     /* paula.c: audio output */
void paula_record(const char *path);                        /* also write it to a WAV file */
void paula_stop(void);

/* An exec struct Interrupt: is_Data and is_Code are what a server is called with. */
#pragma pack(push, 2)
struct Interrupt {
    struct Node is_Node;
    void *is_Data;
    void (*is_Code)(void);
};
#pragma pack(pop)

#endif
