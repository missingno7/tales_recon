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
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int F_h00_8A46();

recovered()
{
    struct Rect *rect;

    for (rect = G_h01_34EC; rect - G_h01_34EC < 40; rect++)
        if (rect->kind) {
            rect->kind--;
            if (rect->width > 0)
                if (rect->height > 0)
                    F_h00_8A46(G_h01_46CE, rect->x, rect->y,
                        G_h01_46D2, rect->x, rect->y, rect->width,
                        rect->height, 192, 255, 0);
        }
}
