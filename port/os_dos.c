/* os_dos.c - dos.library for the game: Open/Read/Seek/Close on the disk images, Delay.
   A file handle is an index + 1 into an open-file table (the game only stores and passes
   it back). Seek returns the previous position, as AmigaDOS does. */
#include "amiga.h"
#include "os.h"
#include "m68k.h"

#include <string.h>

#define OFFSET_BEGINNING (-1)
#define OFFSET_CURRENT 0
#define OFFSET_END 1

struct dos_file { const uint8_t *data; uint32_t size, pos; int used; };
static struct dos_file files[32];

/* The game's DOSBase. The game reads it directly: resident_F_2F24 walks
   DOSBase->dl_Root->rn_Info->di_DevInfo (BPTRs) to find the inserted volumes, which is how
   request_disk sees whether DT1:/DT2: are present. The port builds that tree with one
   DLT_VOLUME node per mounted disk image (dl_Task set: the volume is in a drive). */
extern struct Library *DOSBase;   /* a DATA cell (port_gen RUNTIME_CELLS) */

#define BPTR(p) ((uint32_t)(uintptr_t)(p) >> 2)
#pragma pack(push, 2)
struct DosLibrary { struct Library dl_lib; void *dl_Root; uint8_t rest[32]; };
struct RootNode { uint32_t rn_TaskArray, rn_ConsoleSegment; uint32_t rn_Time[3]; uint32_t rn_RestartSeg, rn_Info, rn_FileHandlerSegment; };
struct DosInfo { uint32_t di_McName, di_DevInfo, di_Devices, di_Handlers, di_NetHand; };
struct DeviceList {
    uint32_t dl_Next, dl_Type;
    void *dl_Task;
    uint32_t dl_Lock;
    uint32_t dl_VolumeDate[3];
    uint32_t dl_LockList, dl_DiskType, dl_unused, dl_Name;
};
#pragma pack(pop)

void dos_init(void)
{
    static struct DosLibrary library __attribute__((aligned(4)));
    static struct RootNode root __attribute__((aligned(4)));
    static struct DosInfo info __attribute__((aligned(4)));
    static struct DeviceList nodes[4] __attribute__((aligned(4)));
    static uint8_t names[4][36] __attribute__((aligned(4)));
    static uint8_t drive_task[64] __attribute__((aligned(4)));
    int count = adf_volume_count() < 4 ? adf_volume_count() : 4;
    library.dl_Root = &root;
    root.rn_Info = BPTR(&info);
    info.di_DevInfo = count ? BPTR(&nodes[0]) : 0;
    for (int i = 0; i < count; i++) {
        const char *name = adf_volume_name(i);
        size_t len = strlen(name) < 30 ? strlen(name) : 30;
        names[i][0] = (uint8_t)len;
        memcpy(names[i] + 1, name, len);
        nodes[i].dl_Next = i + 1 < count ? BPTR(&nodes[i + 1]) : 0;
        nodes[i].dl_Type = 2;                    /* DLT_VOLUME */
        nodes[i].dl_Task = drive_task;           /* mounted in a drive */
        nodes[i].dl_Name = BPTR(names[i]);
    }
    DOSBase = &library.dl_lib;
    /* guest memory: the game walks these through DOSBase and BPTRs */
    m68k_memory(&library, sizeof library, 0); m68k_memory(&root, sizeof root, 0);
    m68k_memory(&info, sizeof info, 0); m68k_memory(nodes, sizeof nodes, 0);
    m68k_memory(names, sizeof names, 0); m68k_memory(drive_task, sizeof drive_task, 0);
}

int32_t Open(int32_t name, int32_t mode)
{
    const char *path = (const char *)(intptr_t)name;
    uint32_t size;
    const uint8_t *data = adf_file(path, &size);
    (void)mode;                                  /* MODE_OLDFILE only: the game writes nothing */
    if (!data) { platform_log("Open %s: not found", path); return 0; }
    for (int i = 0; i < 32; i++)
        if (!files[i].used) {
            files[i] = (struct dos_file){ data, size, 0, 1 };
            platform_log("Open %s -> %d (%u bytes)", path, i + 1, size);
            return i + 1;
        }
    return 0;
}

static struct dos_file *handle(int32_t fh) { return fh > 0 && fh <= 32 && files[fh - 1].used ? &files[fh - 1] : NULL; }

int16_t Close(int32_t fh) { struct dos_file *f = handle(fh); if (f) f->used = 0; return 0; }

int32_t Read(int32_t fh, int32_t buffer, int32_t length)
{
    struct dos_file *f = handle(fh);
    uint32_t n;
    if (!f || length < 0) return -1;
    n = f->size - f->pos < (uint32_t)length ? f->size - f->pos : (uint32_t)length;
    memcpy((void *)(intptr_t)buffer, f->data + f->pos, n);
    f->pos += n;
    return (int32_t)n;
}

int32_t Seek(int32_t fh, int32_t position, int32_t mode)
{
    struct dos_file *f = handle(fh);
    int32_t previous, target;
    if (!f) return -1;
    previous = (int32_t)f->pos;
    target = mode == OFFSET_BEGINNING ? position : mode == OFFSET_CURRENT ? previous + position : (int32_t)f->size + position;
    if (target < 0 || (uint32_t)target > f->size) return -1;
    f->pos = (uint32_t)target;
    return previous;
}

int16_t Delay(int32_t ticks) { platform_wait_ticks((int)ticks); return 0; }
