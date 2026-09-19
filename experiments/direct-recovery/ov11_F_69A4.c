struct Record {
    int unused0, unused2;
    int left, right, top, bottom;
    int initial_x, initial_y, offset_y;
    int x, y, flags;
    int unused24, unused26, unused28;
    int step, active;
};
extern struct Record G_h01_A554[10];
recovered()
{
    struct Record *p;
    int i;
    i = 0;
    do {
        p = &G_h01_A554[i];
        p->x = p->initial_x;
        p->y = p->initial_y + p->offset_y;
        p->left = p->right = p->x;
        p->top = p->bottom = p->y;
        p->flags = 192;
        p->step = 8;
        p->active = 1;
        ++i;
    } while (i < 10);
}
