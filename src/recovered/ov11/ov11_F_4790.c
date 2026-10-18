/* Direct reconstruction candidate for ov11_F_4790. */
struct Rect {
    int kind;
    int x;
    int y;
    int width;
    int height;
    int index;
    char pad[2];
};

extern struct Rect G_h01_34EC[40];
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern int BltBitMap();

recovered()
{
    struct Rect *rect;

    for (rect = G_h01_34EC; rect - G_h01_34EC < 40; rect++)
        if (rect->kind) {
            rect->kind--;
            if (rect->width > 0)
                if (rect->height > 0)
                    BltBitMap(archive_image_bitmap, (long)rect->x,
                        (long)rect->y, active_screen_bitmap, (long)rect->x,
                        (long)rect->y, (long)rect->width,
                        (long)rect->height, (long)192, (long)255, 0L);
        }
}
