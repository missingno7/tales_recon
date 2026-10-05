struct BitMap { unsigned short BytesPerRow; unsigned short Rows; unsigned char Flags; unsigned char Depth; unsigned short pad; unsigned char *Planes[8]; };
struct RasInfo { struct RasInfo *Next; struct BitMap *BitMap; short RxOffset; short RyOffset; };
extern struct BitMap specimen_second;
extern struct BitMap specimen_first;
extern struct RasInfo specimen_info;
recovered() { return sizeof(struct RasInfo); }
bitmap_size() { return sizeof(struct BitMap); }
ras_bitmap_offset() { return (long)&((struct RasInfo *)0)->BitMap; }
ras_rx_offset() { return (long)&((struct RasInfo *)0)->RxOffset; }
ras_ry_offset() { return (long)&((struct RasInfo *)0)->RyOffset; }
bitmap_planes_offset() { return (long)&((struct BitMap *)0)->Planes; }
