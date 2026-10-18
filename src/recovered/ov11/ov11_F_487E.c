extern int BltBitMap();
extern int jg_draw_visible_platforms();
extern int jg_advance_hazard_motion();
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern long G_h01_A460;
extern int G_h01_8A6E[1];
extern int G_h01_8A3E;
extern int G_h01_94AE;
extern int G_h01_A45E;

recovered(x,y,width,height)
int x,y,width,height;
{
    int last,column,step,local_y,progress,spare;

    local_y=y;
    progress=0;
    last=(x+48)%104;
    while (progress<width) {
        step=(104-last<width-progress)?(104-last):(width-progress);
        BltBitMap((long)G_h01_A460,(long)last,(long)0,
            (long)active_screen_bitmap,(long)local_y,(long)0,(long)step,
            (long)176,(long)192,(long)255,(long)0);
        progress+=step;
        local_y+=step;
        last=0;
    }
    jg_draw_visible_platforms();

    last=x/104;
    column=(x+320)/104;
    for (;last<=column;last++) {
        if (*((int *)((char *)G_h01_8A6E+((long)last*14))) && G_h01_94AE!=45)
            jg_advance_hazard_motion(*((int *)((char *)G_h01_8A6E+((long)last*14))));
    }
    if (height) {
        BltBitMap((long)active_screen_bitmap,(long)y,(long)0,
            (long)archive_image_bitmap,(long)y,(long)0,(long)width,
            (long)200,(long)192,(long)255,(long)0);
        G_h01_A45E=G_h01_8A3E;
    }
}
