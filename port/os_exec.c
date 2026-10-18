/* os_exec.c - exec.library for the game: memory, lists, tasks, ports and devices,
   interrupts. Signatures follow the game's own declarations (16-bit results as int16_t,
   pointers as 32-bit values); arguments arrive as 32-bit slots, as on the 68000 stack. */
#include "amiga.h"
#include "os.h"

#include <stdlib.h>
#include <string.h>

#define MEMF_CLEAR 0x10000

/* Every allocation remembers its size: FreeMem is called with the same size. */
int32_t AllocMem(int32_t size, int32_t flags)
{
    void *block = calloc(1, (size_t)(size > 0 ? size : 1));
    (void)flags;                                 /* chip/public/clear: one host heap, always cleared */
    return (int32_t)(intptr_t)block;
}

int16_t FreeMem(int32_t block, int32_t size) { (void)size; free((void *)(intptr_t)block); return 0; }

int32_t AvailMem(int32_t flags) { (void)flags; return 512 * 1024; }

/* Allocate/Deallocate on a caller-owned MemHeader: the game allocates one pool, sets up
   its own MemHeader over it and checks every freed block against the pool bounds
   (free_memory_checked), so blocks must come from the pool. Exec's algorithm: sizes in
   8-byte units, first fit from the start of a free chunk, coalescing on free. */
#pragma pack(push, 2)
struct MemChunk { struct MemChunk *mc_Next; uint32_t mc_Bytes; };
struct MemHeader {
    struct Node mh_Node;
    uint16_t mh_Attributes;
    struct MemChunk *mh_First;
    uint8_t *mh_Lower, *mh_Upper;
    uint32_t mh_Free;
};
#pragma pack(pop)

int32_t Allocate(struct MemHeader *mh, int32_t size)
{
    uint32_t bytes = ((uint32_t)size + 7u) & ~7u;
    struct MemChunk **link = &mh->mh_First;
    if (size <= 0 || bytes > mh->mh_Free) return 0;
    for (struct MemChunk *chunk = mh->mh_First; chunk; link = &chunk->mc_Next, chunk = chunk->mc_Next) {
        if (chunk->mc_Bytes < bytes) continue;
        if (chunk->mc_Bytes == bytes) *link = chunk->mc_Next;
        else {
            struct MemChunk *rest = (struct MemChunk *)((uint8_t *)chunk + bytes);
            rest->mc_Next = chunk->mc_Next;
            rest->mc_Bytes = chunk->mc_Bytes - bytes;
            *link = rest;
        }
        mh->mh_Free -= bytes;
        return (int32_t)(intptr_t)chunk;
    }
    return 0;
}

int16_t Deallocate(struct MemHeader *mh, int32_t block, int32_t size)
{
    uint8_t *start = (uint8_t *)(intptr_t)((uint32_t)block & ~7u);
    uint32_t bytes = (((uint32_t)block & 7u) + (uint32_t)size + 7u) & ~7u;
    struct MemChunk **link = &mh->mh_First, *previous = NULL, *chunk = mh->mh_First, *freed;
    if (!block || size <= 0) return 0;
    while (chunk && (uint8_t *)chunk < start) { previous = chunk; link = &chunk->mc_Next; chunk = chunk->mc_Next; }
    freed = (struct MemChunk *)start;
    freed->mc_Bytes = bytes;
    freed->mc_Next = chunk;
    *link = freed;
    if (chunk && start + bytes == (uint8_t *)chunk) {                 /* merge with the next */
        freed->mc_Bytes += chunk->mc_Bytes;
        freed->mc_Next = chunk->mc_Next;
    }
    if (previous && (uint8_t *)previous + previous->mc_Bytes == start) { /* merge with the previous */
        previous->mc_Bytes += freed->mc_Bytes;
        previous->mc_Next = freed->mc_Next;
    }
    mh->mh_Free += bytes;
    return 0;
}

int16_t NewList(struct List *list)
{
    list->lh_Head = (struct Node *)&list->lh_Tail;
    list->lh_Tail = NULL;
    list->lh_TailPred = (struct Node *)&list->lh_Head;
    return 0;
}

int16_t AddTail(struct List *list, struct Node *node)
{
    struct Node *tail = (struct Node *)&list->lh_Tail;
    node->ln_Succ = tail;
    node->ln_Pred = list->lh_TailPred;
    list->lh_TailPred->ln_Succ = node;
    list->lh_TailPred = node;
    return 0;
}

int32_t RemTail(struct List *list)
{
    struct Node *node = list->lh_TailPred;
    if (node->ln_Pred == NULL) return 0;          /* empty: TailPred points at the head */
    list->lh_TailPred = node->ln_Pred;
    node->ln_Pred->ln_Succ = (struct Node *)&list->lh_Tail;
    return (int32_t)(intptr_t)node;
}

int16_t Forbid(void) { platform_forbid(1); return 0; }
int16_t Permit(void) { platform_forbid(0); return 0; }

/* The game's own task: a zeroed Process the startup and the input handler refer to. */
static uint8_t own_task[256];
int32_t FindTask(int32_t name) { (void)name; return (int32_t)(intptr_t)own_task; }

/* Message ports and IO requests exist only as memory the game can fill in. */
int32_t CreatePort(int32_t name, int32_t pri) { (void)name; (void)pri; return (int32_t)(intptr_t)calloc(1, 64); }
int16_t DeletePort(int32_t port) { free((void *)(intptr_t)port); return 0; }
int32_t CreateStdIO(int32_t port) { (void)port; return (int32_t)(intptr_t)calloc(1, 64); }
int16_t DeleteStdIO(int32_t io) { free((void *)(intptr_t)io); return 0; }

/* input.device: the game adds an input handler (IND_ADDHANDLER) with DoIO; the platform
   delivers its key events to that handler (platform_input_handler). */
int32_t OpenDevice(int32_t name, int32_t unit, int32_t io, int32_t flags)
{
    (void)unit; (void)io; (void)flags;
    platform_log("OpenDevice %s", (const char *)(intptr_t)name);
    return 0;                                    /* 0 = success */
}
int16_t CloseDevice(int32_t io) { (void)io; return 0; }

#define IOSTD_COMMAND 28                         /* offset of io_Command in an IOStdReq */
#define IOSTD_DATA 40                            /* offset of io_Data */
#define IND_ADDHANDLER 9
#define IND_REMHANDLER 10

int16_t DoIO(int32_t io)
{
    uint8_t *req = (uint8_t *)(intptr_t)io;
    uint16_t command = *(uint16_t *)(req + IOSTD_COMMAND);
    void *data = *(void **)(req + IOSTD_DATA);
    if (command == IND_ADDHANDLER) platform_input_handler(data);
    else if (command == IND_REMHANDLER) platform_input_handler(NULL);
    else platform_log("DoIO command %u", command);
    return 0;
}

/* Interrupts: VBlank servers (AddIntServer 5) and the audio channel vectors
   (SetIntVector 7..10) are called by the platform's VBlank and Paula sources. */
int16_t AddIntServer(int32_t number, int32_t interrupt) { platform_add_server((int)number, (void *)(intptr_t)interrupt); return 0; }
int16_t RemIntServer(int32_t number, int32_t interrupt) { platform_remove_server((int)number, (void *)(intptr_t)interrupt); return 0; }
int32_t SetIntVector(int32_t number, int32_t interrupt) { return (int32_t)(intptr_t)platform_set_vector((int)number, (void *)(intptr_t)interrupt); }

/* Libraries: each base is a zeroed Library with enough space for the fields the game
   reads; the game never calls through the vectors (all calls go through the glue). */
static struct Library library_bases[8];
static const char *library_names[8];
int32_t OpenLibrary(int32_t name, int32_t version)
{
    const char *n = (const char *)(intptr_t)name;
    (void)version;
    for (int i = 0; i < 8; i++) {
        if (!library_names[i]) { library_names[i] = n; library_bases[i].lib_Version = 34; }
        if (!strcmp(library_names[i], n)) { platform_log("OpenLibrary %s", n); return (int32_t)(intptr_t)&library_bases[i]; }
    }
    return 0;
}
int16_t CloseLibrary(int32_t library) { (void)library; return 0; }
