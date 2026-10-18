/* amiga.h - the Amiga the game runs on, as the port's platform layer sees it.

   The game reads and writes Amiga OS structures directly (it builds its own View,
   ViewPort, RasInfo and BitMap; it follows View->ViewPort->RasInfo->BitMap->Planes),
   so these declarations keep the AmigaOS 1.3 layouts: fixed-width fields, 4-byte
   pointers (the port is an i686 build) and the 68000's 2-byte alignment. Values are in
   host byte order: the game's C code computes and stores them natively.

   docs/sdl3-port.md describes the design; docs/platform.md lists every OS call and
   hardware access the game makes. */
#ifndef AMIGA_H
#define AMIGA_H

#include <stdint.h>
#include <stddef.h>

#pragma pack(push, 2)

struct Node {
    struct Node *ln_Succ, *ln_Pred;
    uint8_t ln_Type;
    int8_t ln_Pri;
    char *ln_Name;
};

struct List {
    struct Node *lh_Head, *lh_Tail, *lh_TailPred;
    uint8_t lh_Type, l_pad;
};

struct Library {
    struct Node lib_Node;
    uint8_t lib_Flags, lib_pad;
    uint16_t lib_NegSize, lib_PosSize, lib_Version, lib_Revision;
    char *lib_IdString;
    uint32_t lib_Sum;
    uint16_t lib_OpenCnt;
};

struct BitMap {
    uint16_t BytesPerRow, Rows;
    uint8_t Flags, Depth;
    uint16_t pad;
    uint8_t *Planes[8];
};

struct Rectangle { int16_t MinX, MinY, MaxX, MaxY; };

struct TextAttr { char *ta_Name; uint16_t ta_YSize; uint8_t ta_Style, ta_Flags; };

struct TextFont {
    uint8_t tf_Message[20];             /* struct Message, unused here */
    uint16_t tf_YSize;
    uint8_t tf_Style, tf_Flags;
    uint16_t tf_XSize, tf_Baseline, tf_BoldSmear, tf_Accessors;
    uint8_t tf_LoChar, tf_HiChar;
    void *tf_CharData;
    uint16_t tf_Modulo;
    void *tf_CharLoc, *tf_CharSpace, *tf_CharKern;
};

struct RastPort {
    struct Layer *Layer;
    struct BitMap *BitMap;
    uint16_t *AreaPtrn;
    void *TmpRas, *AreaInfo, *GelsInfo;
    uint8_t Mask;
    int8_t FgPen, BgPen, AOlPen;
    int8_t DrawMode, AreaPtSz, linpatcnt, dummy;
    uint16_t Flags, LinePtrn;
    int16_t cp_x, cp_y;
    uint8_t minterms[8];
    int16_t PenWidth, PenHeight;
    struct TextFont *Font;
    uint8_t AlgoStyle, TxFlags;
    uint16_t TxHeight, TxWidth, TxBaseline;
    int16_t TxSpacing;
    void *RP_User;
    uint32_t longreserved[2];
    uint16_t wordreserved[7];
    uint8_t reserved[8];
};

struct Layer {
    struct Layer *front, *back;
    void *ClipRect;
    struct RastPort *rp;
    struct Rectangle bounds;
    uint8_t reserved[4];
    uint16_t priority, Flags;
    struct BitMap *SuperBitMap;
    void *SuperClipRect, *Window;
    int16_t Scroll_X, Scroll_Y;
    uint8_t rest[100];                  /* layers.library private state, unused here */
};

struct ColorMap {
    uint8_t Flags, Type;
    uint16_t Count;
    uint16_t *ColorTable;               /* 0x0RGB per colour */
};

struct RasInfo {
    struct RasInfo *Next;
    struct BitMap *BitMap;
    int16_t RxOffset, RyOffset;
};

struct ViewPort {
    struct ViewPort *Next;
    struct ColorMap *ColorMap;
    void *DspIns, *SprIns, *ClrIns, *UCopIns;
    int16_t DWidth, DHeight, DxOffset, DyOffset;
    uint16_t Modes;
    uint8_t SpritePriorities, reserved;
    struct RasInfo *RasInfo;
};

struct View {
    struct ViewPort *ViewPort;
    void *LOFCprList, *SHFCprList;
    int16_t DyOffset, DxOffset;
    uint16_t Modes;
};

#pragma pack(pop)

/* ---- the platform (port/main.c) ---- */
void platform_log(const char *format, ...);
void platform_unimplemented(const char *name);   /* logs once per name */
const struct View *platform_view(void);          /* the View the game loaded (LoadView) */
void platform_set_view(const struct View *view);
void platform_wait_ticks(int ticks);             /* DOS Delay: 50 Hz ticks */
uint16_t platform_joystick(void);                /* JOY1DAT for port 2 */
int platform_fire(void);                         /* port 2 fire button, 1 = pressed */
uint16_t platform_beam(void);                    /* VPOSR/VHPOSR sample for the game */

/* ---- disk images (port/adf.c) ---- */
int adf_mount(const char *volume, const char *image_path);   /* 0 on success */
/* A whole file of a mounted volume ("DT1:main.arc", case-insensitive). The returned
   buffer belongs to the disk layer; NULL when absent. */
const uint8_t *adf_file(const char *amiga_path, uint32_t *size);
int adf_volume_count(void);
const char *adf_volume_name(int index);

/* ---- dos.library state (port/os_dos.c) ---- */
void dos_init(void);                             /* DOSBase and the volume list, after mounting */

#endif
