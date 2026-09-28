extern int F_h00_8A46();
extern int F_h11_55B8();
extern int F_h11_645E();
extern long G_h01_46D2;
extern long G_h01_46CE;
extern long G_h01_A460;
extern int G_h01_8A6E[1];
extern int G_h01_94AE;

recovered(x,y,width,height)
int x,y,width,height;
{
    int first,last,step,column,limit;

    first=(x+48)/104;
    last=(y+48)/104;
    step=0;
    limit=width;
    if (last<limit) {
        step=104-(x%104);
        if (step<0) step=0;
    }
    F_h00_8A46((long)G_h01_A460,(long)last,(long)0,(long)G_h01_46D2,(long)y,(long)0,(long)step,(long)176,(long)192,(long)255,(long)0);
    while (step<limit) {
        y+=step;
        step=104;
        F_h00_8A46((long)G_h01_A460,(long)last,(long)0,(long)G_h01_46D2,(long)y,(long)0,(long)step,(long)176,(long)192,(long)255,(long)0);
    }
    F_h11_55B8();
    column=(x+320)/104;
    for (first=first;first<=column;first++) {
        if (G_h01_8A6E[first*7] && G_h01_94AE!=45)
            F_h11_645E(G_h01_8A6E[first*7]);
    }
    if (height) {
        F_h00_8A46((long)G_h01_A460,(long)y,(long)0,(long)G_h01_46CE,(long)x,(long)0,(long)height,(long)200,(long)192,(long)255,(long)0);
        G_h01_A460=G_h01_94AE;
    }
}
