struct AnimRecord {
    char prefix[22];
    int animation;
    int flags;
    int x;
    int y;
    int row;
    int column;
    int value;
    int extra;
    int tail;
};

extern struct AnimRecord G_h01_3724[1];
extern long G_h01_9F82;
extern int G_h01_9C8C[1];
extern int G_h01_9CBC[1];
extern int G_h01_9C92[1];
extern int G_h01_9CC2[1];
extern int G_h01_9C90;
extern int G_h01_9CA0;
extern int G_h01_9CB0;
extern int G_h01_9CC0;
extern int G_h01_9CD0;
extern int G_h01_9CE0;
extern int G_h01_9CEC[1];
extern int G_h01_9CF0;
extern int G_h01_9D00;
extern int G_h01_9D10;
extern int G_h01_9D20;
extern int G_h01_371C;
extern int G_h01_371E;
extern int G_h01_3720;
extern int G_h01_3722;
extern char G_h01_46E0;
extern int F_h11_54F8();
extern int F_h11_41F6();

recovered()
{
    int i,state;
    struct AnimRecord *record;

    for (i=0;i<3;i++) {
        G_h01_9C8C[i*8]=G_h01_9F82;
        G_h01_9CBC[i*8]=G_h01_9F82;
        G_h01_9C92[i*8]=1;
        G_h01_9CC2[i*8]=1;
    }
    G_h01_9C90=6;
    G_h01_9CA0=7;
    G_h01_9CB0=6;
    G_h01_9CC0=2;
    G_h01_9CD0=3;
    G_h01_9CE0=2;
    for (i=0;i<4;i++)
        G_h01_9CEC[i*8]=G_h01_9F82;
    G_h01_9CF0=0;
    G_h01_9D00=1;
    G_h01_9D10=4;
    G_h01_9D20=5;
    for (i=0;i<5;i++) {
        record=&G_h01_3724[i];
        record->x=record->row*53;
        record->y=record->column*32+32;
        record->animation=14;
        F_h11_54F8(i,5);
        F_h11_41F6(record,11,record->x,record->y,14,5);
    }
    state=G_h01_46E0;
    if (state==0) {
        G_h01_371C=80;
        G_h01_371E=75;
        G_h01_3720=20;
    } else if (state==1) {
        G_h01_371C=70;
        G_h01_371E=85;
        G_h01_3720=20;
    } else if (state==2) {
        G_h01_371C=60;
        G_h01_371E=90;
        G_h01_3720=10;
    }
    G_h01_3722=G_h01_3720*3;
}
