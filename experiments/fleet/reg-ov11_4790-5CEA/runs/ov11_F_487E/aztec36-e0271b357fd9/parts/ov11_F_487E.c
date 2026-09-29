extern int F_h00_8A46();
extern int F_h11_55B8();
extern int F_h11_645E();
extern long G_h01_46CE;
extern long G_h01_46D2;
extern long G_h01_A460;
extern int G_h01_8A6E[1];
extern int G_h01_94AE;
extern int G_h01_A45E;

recovered(x,y,width,height)
int x,y,width,height;
{
    int last,column,step,local_y,progress;

    local_y=y;
    progress=0;
    last=(x+48)%104;
    while (progress<width) {
        step=(104-last<width-progress)?(104-last):(width-progress);
        F_h00_8A46((long)G_h01_A460,(long)last,(long)0,
            (long)G_h01_46D2,(long)local_y,(long)0,(long)step,
            (long)176,(long)192,(long)255,(long)0);
        progress+=step;
        local_y+=step;
        last=0;
    }
    F_h11_55B8();

    last=x/104;
    column=(x+320)/104;
    for (;last<=column;last++) {
        if (*((int *)((char *)G_h01_8A6E+((long)last*14))) && G_h01_94AE!=45)
            F_h11_645E(*((int *)((char *)G_h01_8A6E+((long)last*14))));
    }
    if (height) {
        F_h00_8A46((long)G_h01_46D2,(long)local_y,(long)0,
            (long)G_h01_46CE,(long)local_y,(long)0,(long)height,
            (long)200,(long)192,(long)255,(long)0);
        G_h01_A45E=G_h01_94AE;
    }
}
