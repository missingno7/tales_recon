/* Provisional source for normal ov11 layout evidence; never canonical by itself. */
extern int G_h01_8B1C[41][4];
extern int F_h11_5962();

recovered(x,y,width,height,mode)
int x,y,width,height,mode;
{
    int tile,y_end,x_end,y_start,x_start;
    if (mode==10) {
        x_end=x+width;
        y_end=y+height;
        x_start=(x-24)/53;
        y_start=(y-48)>>5;
        x_end=(x_end+24)/53;
        y_end=(y_end-16)>>5;
    } else {
        x_end=x+width;
        y_end=y+height;
        x_start=x/53;
        y_start=(y-48)>>5;
        x_end=x_end/53;
        y_end=(y_end-48)>>5;
    }
    if (x_start<0) x_start=0;
    if (y_start<0) y_start=0;
    for (x=x_start;x<=x_end;x++)
        for (y=y_start;y<=y_end;y++) {
            tile=G_h01_8B1C[x][y];
            if (tile) F_h11_5962(tile,mode);
        }
}
