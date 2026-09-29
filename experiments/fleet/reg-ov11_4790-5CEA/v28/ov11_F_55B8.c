struct GridRecord {
    char prefix[8];
    int code;
    char pad10[0x1e];
    int y;
    int x;
    int value2c;
    int value2e;
    char tail[4];
};

extern int G_h01_37F2;
extern int G_h01_8A3E;
extern int G_h01_8B1C[41][4];
extern int G_h01_940C[1];
extern int G_h01_94AE;
extern int G_h01_94B0;
extern int G_h01_8BEC[1];
extern int G_h01_9F5E[1];
extern int G_h01_9FA2[1];
extern int F_h11_5962();
extern int F_h00_34E0();

recovered()
{
    int row,column,tile,base,vertical,horizontal;
    struct GridRecord *object;

    if (G_h01_37F2) {
        G_h01_37F2=0;
        for (row=0;row<24;row++) {
            vertical=row*53+((row&1)?-4:-24);
            for (column=2;column>=0;column--) {
                tile=G_h01_8B1C[row][column];
                if (tile) {
                    object=(struct GridRecord *)&G_h01_8BEC[tile*26];
                    if (!object->code) {
                        object->value2c=(column*32)+48;
                        object->value2e=vertical;
                    }
                }
            }
        }
    }
    for (row=0;row<18;row++) {
        for (column=0;column<3;column++) {
            tile=G_h01_8B1C[row][column];
            if (tile) {
                object=(struct GridRecord *)&G_h01_8BEC[tile*26];
                if (object->value2c>0 && !object->code) {
                    base=object->value2e-G_h01_8A3E;
                    horizontal=object->value2c;
                    G_h01_9F5E[0]=base;
                    G_h01_9F5E[1]=horizontal;
                    G_h01_9F5E[2]=object->value2e;
                    G_h01_9F5E[3]=object->prefix[7];
                    F_h00_34E0(G_h01_9F5E);
                    object->value2c--;
                    if (!object->value2c) object->value2e=0;
                }
            }
        }
    }
    vertical=G_h01_94AE;
    horizontal=G_h01_94B0;
    for (row=6;row>=0;row--) {
        for (column=2;column>=0;column--) {
            tile=G_h01_8B1C[row][column];
            if (tile) {
                object=(struct GridRecord *)&G_h01_8BEC[tile*26];
                if (object->value2c>0 && !object->code) {
                    G_h01_9FA2[0]=object->value2e+16;
                    G_h01_9FA2[1]=object->value2c-13;
                    F_h00_34E0(G_h01_9FA2);
                    F_h11_5962(tile,2);
                }
            }
        }
    }
    row=vertical+horizontal;
    G_h01_940C[row]=0;
    if (G_h01_37F2) F_h11_5962(G_h01_37F2,2);
}
