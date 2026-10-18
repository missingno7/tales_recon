extern long grid_background_bitmap;
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern long grid_collision_map;
extern int G_h01_349A;
extern int G_h01_349C;
extern char G_h01_34CE;
extern int BltBitMap();
extern int draw_masked_sprite();

recovered(a)
int a;
{
    int block, digit, y, x;
    char *p;

    x=160;
    y=(a%5)*40;
    block=0;
    do {
        BltBitMap(grid_background_bitmap,0L,(long)y,active_screen_bitmap,
            0L,0L,320L,40L,192L,255L,0L);
        if (a+block<25) {
            p=(char *)(grid_collision_map+(long)(a+block)*21);
            G_h01_349A=0;
            digit=0;
            do {
                if (*p!='F') {
                    G_h01_34CE=*p-'0';
                    G_h01_349C=0;
                    draw_masked_sprite(&G_h01_349A);
                }
                ++p;
                G_h01_349A+=16;
            } while (++digit<20);
        }
        BltBitMap(active_screen_bitmap,0L,0L,archive_image_bitmap,
            0L,(long)x,320L,40L,192L,255L,0L);
        x-=40;
        y+=40;
        if (y>160)
            y=0;
    } while (++block<5);
}