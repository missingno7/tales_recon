struct Table {
    int first;
    int second;
    char pad[2];
};

extern long F_h00_463E();
extern int F_h00_57D2();
extern char G_h01_7192;
extern int G_h01_4262;
extern int G_h01_4264[6];
extern unsigned char G_h01_4272[96];
extern char G_h01_0468[16];
extern char G_h01_4332;
extern char G_h01_433E;
extern char G_h01_434A;
extern char G_h01_46E0;
extern char G_h01_4188;
extern struct Table G_h01_4274[64];

recovered(mode)
char mode;
{
    unsigned row;
    int value;
    register char *event;

again:
    if ((unsigned)F_h00_463E()%100 < G_h01_7192)
        row=G_h01_4262;
    else
        row=G_h01_4264[(unsigned)F_h00_463E()%6];

    if (!mode) {
        value=(unsigned)F_h00_463E()%5;
        if (!(*((unsigned char *)G_h01_4272+(row-14)*6) & G_h01_0468[value]))
            goto mode0_done;
        if (value==4)
            value=13;
        event=&G_h01_4332;
        event[0]=value+1;
        *(int *)(event+2)=row;
        event[4]=0;
        event[5]=1;
        if (!G_h01_46E0 && G_h01_4188)
            event[6]=2;
        else
            event[6]=1;
        *(int *)(event+8)=G_h01_4274[row-14].first;
        *(int *)(event+10)=G_h01_4274[row-14].second;
        F_h00_57D2(103);
        goto done;
mode0_done:
        goto done;
    }
    if (mode==1) {
        value=(int)F_h00_463E()&3;
        if (!(*((unsigned char *)G_h01_4272+(row-14)*6) & G_h01_0468[value+5]))
            goto mode1_done;
        event=&G_h01_433E;
        event[0]=value+5;
        *(int *)(event+2)=row;
        event[4]=0;
        event[5]=1;
        if (!G_h01_46E0 && G_h01_4188!=1)
            event[6]=2;
        else
            event[6]=1;
        *(int *)(event+8)=G_h01_4274[row-14].first;
        *(int *)(event+10)=G_h01_4274[row-14].second;
        F_h00_57D2(105);
        goto done;
mode1_done:
        goto done;
    }
    if (mode==2) {
        value=(unsigned)F_h00_463E()%5;
        if (!(*((unsigned char *)G_h01_4272+(row-14)*6) & G_h01_0468[value+9]))
            goto mode2_done;
        event=&G_h01_434A;
        event[0]=value+9;
        *(int *)(event+2)=row;
        event[4]=0;
        event[5]=1;
        if (!G_h01_46E0 && G_h01_4188!=2)
            event[6]=2;
        else
            event[6]=1;
        *(int *)(event+8)=G_h01_4274[row-14].first;
        *(int *)(event+10)=G_h01_4274[row-14].second;
        F_h00_57D2(104);
        goto done;
mode2_done:
        goto done;
    }
    goto again;

done:
    ;
}
