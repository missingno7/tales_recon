/* os_graphics.c - graphics.library and layers.library on planar bitmaps.

   The game draws into BitMaps it allocates (5 bitplanes, 320x200) and shows them with a
   View it builds itself (InitView/InitVPort/MakeVPort/MrgCop/LoadView). Drawing here
   writes the same planar bits graphics.library would; the platform shows the loaded View.

   Copper list: the game's VBlank colour cycling (resident_callback_617C/61A0) writes
   palette values straight into View->LOFCprList->start: one word every 4 bytes, colour n at
   instruction n + 1. MrgCop therefore builds that layout, and the platform takes the
   displayed palette from it, as the hardware would. */
#include "amiga.h"
#include "os.h"

#include <stdlib.h>
#include <string.h>

#define JAM2 1
#define COMPLEMENT 2
#define INVERSVID 4

/* ---- planar pixels ---- */
static int pixel(const struct BitMap *bm, int x, int y)
{
    int value = 0;
    if (x < 0 || y < 0 || x >= bm->BytesPerRow * 8 || y >= bm->Rows) return 0;
    for (int p = 0; p < bm->Depth; p++)
        if (bm->Planes[p] && (bm->Planes[p][y * bm->BytesPerRow + (x >> 3)] & (0x80 >> (x & 7))))
            value |= 1 << p;
    return value;
}

static void plot(struct BitMap *bm, int x, int y, int pen, int mask)
{
    if (x < 0 || y < 0 || x >= bm->BytesPerRow * 8 || y >= bm->Rows) return;
    for (int p = 0; p < bm->Depth; p++) {
        uint8_t *b;
        if (!bm->Planes[p] || !(mask & (1 << p))) continue;
        b = &bm->Planes[p][y * bm->BytesPerRow + (x >> 3)];
        if (pen & (1 << p)) *b |= (uint8_t)(0x80 >> (x & 7)); else *b &= (uint8_t)~(0x80 >> (x & 7));
    }
}

/* RastPort coordinates are relative to its layer. */
static int origin_x(const struct RastPort *rp) { return rp->Layer ? rp->Layer->bounds.MinX : 0; }
static int origin_y(const struct RastPort *rp) { return rp->Layer ? rp->Layer->bounds.MinY : 0; }

static void rp_plot(struct RastPort *rp, int x, int y, int pen)
{
    int ax = x + origin_x(rp), ay = y + origin_y(rp);
    if (rp->Layer && (ax > rp->Layer->bounds.MaxX || ay > rp->Layer->bounds.MaxY || ax < rp->Layer->bounds.MinX || ay < rp->Layer->bounds.MinY))
        return;
    if (rp->DrawMode & COMPLEMENT) pen = pixel(rp->BitMap, ax, ay) ^ 0xff;
    plot(rp->BitMap, ax, ay, pen, rp->Mask);
}

int16_t InitBitMap(struct BitMap *bm, int32_t depth, int32_t width, int32_t height)
{
    bm->BytesPerRow = (uint16_t)(((width + 15) >> 4) << 1);
    bm->Rows = (uint16_t)height;
    bm->Depth = (uint8_t)depth;
    bm->Flags = 0; bm->pad = 0;
    return 0;
}

/* ---- View, ViewPort, ColorMap, copper ---- */
int16_t InitView(struct View *view) { memset(view, 0, sizeof *view); return 0; }
int16_t InitVPort(struct ViewPort *vp) { memset(vp, 0, sizeof *vp); return 0; }

int32_t GetColorMap(int32_t entries)
{
    struct ColorMap *cm = calloc(1, sizeof *cm);
    cm->Count = (uint16_t)entries;
    cm->ColorTable = calloc((size_t)entries, sizeof(uint16_t));
    return (int32_t)(intptr_t)cm;
}
int16_t FreeColorMap(struct ColorMap *cm) { if (cm) { free(cm->ColorTable); free(cm); } return 0; }

/* struct cprlist: Next, start, MaxCount */
#pragma pack(push, 2)
struct cprlist { struct cprlist *Next; uint16_t *start; int16_t MaxCount; };
#pragma pack(pop)

int16_t MakeVPort(struct View *view, struct ViewPort *vp) { (void)view; (void)vp; return 0; }

int16_t MrgCop(struct View *view)
{
    struct cprlist *list = view->LOFCprList;
    struct ColorMap *cm = view->ViewPort ? view->ViewPort->ColorMap : NULL;
    if (!list) {
        list = calloc(1, sizeof *list);
        list->start = calloc(2 * 34, sizeof(uint16_t));
        list->MaxCount = 34;
        view->LOFCprList = list;
    }
    list->start[0] = 0x0100; list->start[1] = 0;                 /* BPLCON0: depth from the bitmap */
    for (int n = 0; n < 32; n++) {
        list->start[2 + 2 * n] = (uint16_t)(0x0180 + 2 * n);
        list->start[3 + 2 * n] = cm && n < cm->Count ? cm->ColorTable[n] : 0;
    }
    list->start[66] = 0xffff; list->start[67] = 0xfffe;          /* end of list */
    return 0;
}

int16_t LoadView(struct View *view) { platform_set_view(view); return 0; }
int16_t FreeVPortCopLists(struct ViewPort *vp) { (void)vp; return 0; }
int16_t FreeCprList(void *list) { (void)list; return 0; }
int16_t WaitBOVP(struct ViewPort *vp) { (void)vp; platform_wait_ticks(0); return 0; }
int16_t FreeSprite(int32_t sprite) { (void)sprite; return 0; }

/* The palette the display shows: the copper list's colour MOVEs, else the ColorMap. */
int platform_palette(const struct View *view, uint16_t colours[32])
{
    const struct cprlist *list = view ? view->LOFCprList : NULL;
    const struct ColorMap *cm = view && view->ViewPort ? view->ViewPort->ColorMap : NULL;
    for (int n = 0; n < 32; n++)
        colours[n] = list ? list->start[3 + 2 * n] : cm && n < cm->Count ? cm->ColorTable[n] : 0;
    return 0;
}

/* ---- RastPort state ---- */
int16_t SetAPen(struct RastPort *rp, int32_t pen) { rp->FgPen = (int8_t)pen; return 0; }
int16_t SetBPen(struct RastPort *rp, int32_t pen) { rp->BgPen = (int8_t)pen; return 0; }
int16_t SetDrMd(struct RastPort *rp, int32_t mode) { rp->DrawMode = (int8_t)mode; return 0; }
int16_t Move(struct RastPort *rp, int32_t x, int32_t y) { rp->cp_x = (int16_t)x; rp->cp_y = (int16_t)y; return 0; }

int16_t Draw(struct RastPort *rp, int32_t x1, int32_t y1)
{
    int x0 = rp->cp_x, y0 = rp->cp_y, dx = abs((int)x1 - x0), dy = -abs((int)y1 - y0);
    int sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1, err = dx + dy;
    for (;;) {
        rp_plot(rp, x0, y0, (uint8_t)rp->FgPen);
        if (x0 == x1 && y0 == y1) break;
        int e2 = 2 * err;
        if (e2 >= dy) { err += dy; x0 += sx; }
        if (e2 <= dx) { err += dx; y0 += sy; }
    }
    rp->cp_x = (int16_t)x1; rp->cp_y = (int16_t)y1;
    return 0;
}

void RectFill(struct RastPort *rp, int32_t x0, int32_t y0, int32_t x1, int32_t y1)
{
    for (int y = (int)y0; y <= y1; y++)
        for (int x = (int)x0; x <= x1; x++)
            rp_plot(rp, x, y, (uint8_t)rp->FgPen);
}

int16_t WritePixel(struct RastPort *rp, int32_t x, int32_t y) { rp_plot(rp, (int)x, (int)y, (uint8_t)rp->FgPen); return 0; }

int16_t SetRast(struct RastPort *rp, int32_t pen)
{
    struct BitMap *bm = rp->BitMap;
    for (int p = 0; p < bm->Depth; p++)
        if (bm->Planes[p]) memset(bm->Planes[p], pen & (1 << p) ? 0xff : 0, (size_t)bm->BytesPerRow * bm->Rows);
    return 0;
}

/* ---- blitter ---- */
/* Minterm with A = 1 (the mask channel): result = bit (4 + 2*B + C) of the minterm. */
static int minterm_bit(int minterm, int b, int c) { return (minterm >> (4 + 2 * b + c)) & 1; }

int16_t BltBitMap(struct BitMap *src, int32_t sx, int32_t sy, struct BitMap *dst, int32_t dx, int32_t dy,
                  int32_t w, int32_t h, int32_t minterm, int32_t mask, int32_t temp)
{
    (void)temp;
    for (int p = 0; p < dst->Depth && p < 8; p++) {
        uint8_t *row;
        if (!(mask & (1 << p)) || !dst->Planes[p]) continue;
        row = malloc((size_t)w * (size_t)h);
        for (int y = 0; y < h; y++)                              /* read first: overlapping copies */
            for (int x = 0; x < w; x++) {
                int X = (int)sx + x, Y = (int)sy + y;
                row[y * w + x] = p < src->Depth && src->Planes[p] && X >= 0 && Y >= 0 && X < src->BytesPerRow * 8 && Y < src->Rows
                    && (src->Planes[p][Y * src->BytesPerRow + (X >> 3)] & (0x80 >> (X & 7)));
            }
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++) {
                int X = (int)dx + x, Y = (int)dy + y;
                uint8_t *b, bit;
                if (X < 0 || Y < 0 || X >= dst->BytesPerRow * 8 || Y >= dst->Rows) continue;
                b = &dst->Planes[p][Y * dst->BytesPerRow + (X >> 3)];
                bit = (uint8_t)(0x80 >> (X & 7));
                if (minterm_bit((int)minterm, row[y * w + x], (*b & bit) != 0)) *b |= bit; else *b &= (uint8_t)~bit;
            }
        free(row);
    }
    return 0;
}

int16_t BltBitMapRastPort(struct BitMap *src, int32_t sx, int32_t sy, struct RastPort *rp, int32_t dx, int32_t dy,
                          int32_t w, int32_t h, int32_t minterm)
{
    return BltBitMap(src, sx, sy, rp->BitMap, dx + origin_x(rp), dy + origin_y(rp), w, h, minterm, 0xff, 0);
}

int16_t BltClear(int32_t memory, int32_t count, int32_t flags)
{
    uint32_t bytes = flags & 2 ? ((uint32_t)count >> 16) * ((uint32_t)count & 0xffff) : (uint32_t)count;
    memset((void *)(intptr_t)memory, 0, bytes);
    return 0;
}

/* BltMaskBitMapRastPort (graphics LVO -636), reached through the game's own glue
   resident_glue_4692 = F_h00_4692: where the one-plane mask has a 1 the minterm combines
   source and destination; elsewhere the destination stays. */
int16_t F_h00_4692(struct BitMap *src, int32_t sx, int32_t sy, struct RastPort *rp, int32_t dx, int32_t dy,
                   int32_t w, int32_t h, int32_t minterm, const uint8_t *mask)
{
    struct BitMap *dst = rp->BitMap;
    int mod = (int)(((src->BytesPerRow * 8) + 15) >> 4) << 1;     /* the mask is as wide as the source */
    dx += origin_x(rp); dy += origin_y(rp);
    for (int y = 0; y < h; y++)
        for (int x = 0; x < w; x++) {
            int X = (int)sx + x, Y = (int)sy + y, DX = (int)dx + x, DY = (int)dy + y;
            if (!(mask[Y * mod + (X >> 3)] & (0x80 >> (X & 7)))) continue;
            if (DX < 0 || DY < 0 || DX >= dst->BytesPerRow * 8 || DY >= dst->Rows) continue;
            for (int p = 0; p < dst->Depth; p++) {
                uint8_t *b = dst->Planes[p] ? &dst->Planes[p][DY * dst->BytesPerRow + (DX >> 3)] : NULL;
                uint8_t bit = (uint8_t)(0x80 >> (DX & 7));
                int s = p < src->Depth && src->Planes[p] && (src->Planes[p][Y * src->BytesPerRow + (X >> 3)] & (0x80 >> (X & 7)));
                if (!b) continue;
                if (minterm_bit((int)minterm, s, (*b & bit) != 0)) *b |= bit; else *b &= (uint8_t)~bit;
            }
        }
    return 0;
}

/* ---- text: an 8x8 font, Topaz 8 metrics (baseline 6) ---- */
extern const uint8_t platform_font8x8[256][8];
static struct TextFont topaz8 = { .tf_YSize = 8, .tf_XSize = 8, .tf_Baseline = 6, .tf_LoChar = 32, .tf_HiChar = 255 };

int32_t OpenFont(struct TextAttr *attr) { (void)attr; return (int32_t)(intptr_t)&topaz8; }
int16_t CloseFont(struct TextFont *font) { (void)font; return 0; }
int16_t SetFont(struct RastPort *rp, struct TextFont *font)
{
    rp->Font = font; rp->TxHeight = font->tf_YSize; rp->TxWidth = font->tf_XSize; rp->TxBaseline = font->tf_Baseline;
    return 0;
}

int16_t Text(struct RastPort *rp, const char *text, int32_t count)
{
    int top = rp->cp_y - rp->TxBaseline;
    for (int i = 0; i < count; i++) {
        const uint8_t *glyph = platform_font8x8[(uint8_t)text[i]];
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 8; x++) {
                int on = (glyph[y] >> (7 - x)) & 1;
                if (rp->DrawMode & INVERSVID) on = !on;
                if (on) rp_plot(rp, rp->cp_x + x, top + y, (uint8_t)rp->FgPen);
                else if (rp->DrawMode & JAM2) rp_plot(rp, rp->cp_x + x, top + y, (uint8_t)rp->BgPen);
            }
        rp->cp_x = (int16_t)(rp->cp_x + 8);
    }
    return 0;
}

/* ---- layers.library: one full-screen layer over the game's bitmap ---- */
int32_t NewLayerInfo(void) { return (int32_t)(intptr_t)calloc(1, 128); }
int16_t DisposeLayerInfo(int32_t info) { free((void *)(intptr_t)info); return 0; }

int32_t CreateUpfrontLayer(int32_t info, struct BitMap *bm, int32_t x0, int32_t y0, int32_t x1, int32_t y1,
                           int32_t flags, struct BitMap *super)
{
    struct Layer *layer = calloc(1, sizeof *layer);
    struct RastPort *rp = calloc(1, sizeof *rp);
    (void)info; (void)flags;
    layer->bounds = (struct Rectangle){ (int16_t)x0, (int16_t)y0, (int16_t)x1, (int16_t)y1 };
    layer->rp = rp; layer->SuperBitMap = super;
    rp->Layer = layer; rp->BitMap = bm; rp->Mask = 0xff; rp->FgPen = 1; rp->DrawMode = JAM2;
    return (int32_t)(intptr_t)layer;
}
int16_t DeleteLayer(int32_t info, struct Layer *layer) { (void)info; if (layer) { free(layer->rp); free(layer); } return 0; }
