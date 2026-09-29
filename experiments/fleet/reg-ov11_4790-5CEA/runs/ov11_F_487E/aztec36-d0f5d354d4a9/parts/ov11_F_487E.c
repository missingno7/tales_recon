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
    int last,progress,step,column;

    last=(x+48)%104;
    progress=0;
    while (progress<width) {
        if (104-last<width-progress)
            step=104-last;
        else
            step=width-progress;
        F_h00_8A46((long)G_h01_A460,(long)last,(long)0,
            (long)G_h01_46D2,(long)y,(long)0,(long)step,
            (long)176,(long)192,(long)255,(long)0);
        progress+=step;
        y+=step;
        last=0;
    }
    F_h11_55B8();

    last=x/104;
    column=(x+320)/104;
    while (last<=column) {
        if (G_h01_8A6E[last*7] && G_h01_94AE!=45)
            F_h11_645E(G_h01_8A6E[last*7]);
        last++;
    }
    if (height) {
        F_h00_8A46((long)G_h01_46D2,(long)y,(long)0,
            (long)G_h01_46CE,(long)y,(long)0,(long)height,
            (long)200,(long)192,(long)255,(long)0);
        G_h01_A45E=G_h01_94AE;
    }
}
