struct UiState {
    int x0;
    int y0;
    char pad0[48];
    char text0;
    char pad1;
    int x1;
    int y1;
    char pad2[48];
    char flag0;
    char pad3;
    int x2;
    int y2;
    char pad4[48];
    char flag1;
    char pad5;
    int x3;
    int y3;
    char pad6[48];
    char flag2;
    char pad7[379];
    int x4;
    int y4;
    char pad8[48];
    char flag3;
};

extern int G_h01_1422;
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern struct UiState G_h01_50E6;
extern int request_disk();
extern int load_arc_record();
extern int BltBitMap();
extern int draw_masked_sprite();

recovered(a,b,c)
int a,b,c;
{
    request_disk(1);
    if (!a && c) {
        load_arc_record(3,archive_image_bitmap);
        load_arc_record(4,&G_h01_50E6.x1);
        load_arc_record(5,&G_h01_50E6.x4);
        load_arc_record(6,&G_h01_50E6.x2);
        load_arc_record(7,&G_h01_50E6.x3);
        load_arc_record(8,&G_h01_50E6.x0);
    }
        G_h01_50E6.x4=33;
        G_h01_50E6.y4=48;
        G_h01_50E6.flag3=0;
        G_h01_50E6.x1=120;
        G_h01_50E6.y1=8;
        G_h01_50E6.flag0=a;
        G_h01_50E6.x2=136;
        G_h01_50E6.y2=32;
        G_h01_50E6.flag1=0;
        G_h01_50E6.x3=120;
        G_h01_50E6.y3=48;
        G_h01_50E6.flag2=0;
        G_h01_50E6.x0=216;
        G_h01_50E6.y0=32;
        G_h01_50E6.text0=b;
    BltBitMap(archive_image_bitmap,0L,0L,active_screen_bitmap,
        0L,0L,320L,200L,192L,255L,0L);
    draw_masked_sprite(&G_h01_50E6.x0);
    draw_masked_sprite(&G_h01_50E6.x1);
    if (!G_h01_1422)
        draw_masked_sprite(&G_h01_50E6.x4);
    if (!a) {
        draw_masked_sprite(&G_h01_50E6.x2);
        draw_masked_sprite(&G_h01_50E6.x3);
    }
}
