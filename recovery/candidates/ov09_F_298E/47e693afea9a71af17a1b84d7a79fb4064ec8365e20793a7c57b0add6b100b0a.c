struct Table {
    int first;
    int second;
    char pad[2];
};

struct Event {
    char kind;
    char pad;
    int row;
    char zero;
    char one;
    char flags;
    char pad2;
    int first;
    int second;
};

extern long F_h00_463E();
extern int F_h00_57D2();
extern char G_h01_7192;
extern int G_h01_4262;
extern int G_h01_4264[6];
extern unsigned char G_h01_4272[96];
extern char G_h01_0468[16];
extern struct Event G_h01_4332;
extern struct Event G_h01_433E;
extern struct Event G_h01_434A;
extern char G_h01_46E0;
extern char G_h01_4188;
extern int G_h01_4274[96];
extern int G_h01_4276[96];

recovered(mode)
char mode;
{
    int row,value;
    struct Event *event;

again:
    if ((unsigned)F_h00_463E()%100 < G_h01_7192)
        row=G_h01_4262;
    else
        row=G_h01_4264[(unsigned)F_h00_463E()%6];

    if (!mode) {
        value=(unsigned)F_h00_463E()%5;
        if (G_h01_4272[(row-14)*6] & G_h01_0468[value]) {
            if (value==4)
                value=13;
            event=&G_h01_4332;
            event->kind=value+1;
            event->row=row;
            event->zero=0;
            event->one=1;
            if (!G_h01_46E0 && G_h01_4188)
                event->flags=2;
            else
                event->flags=1;
            event->first=G_h01_4274[row-14].first;
            event->second=G_h01_4274[row-14].second;
            F_h00_57D2(103);
        }
        return;
    }
    if (mode==1) {
        value=(int)F_h00_463E()&3;
        if (G_h01_4272[(row-14)*6] & G_h01_0468[value+5]) {
            event=&G_h01_433E;
            event->kind=value+5;
            event->row=row;
            event->zero=0;
            event->one=1;
            if (!G_h01_46E0 && G_h01_4188!=1)
                event->flags=2;
            else
                event->flags=1;
            event->first=G_h01_4274[row-14].first;
            event->second=G_h01_4274[row-14].second;
            F_h00_57D2(105);
        }
        return;
    }
    if (mode==2) {
        value=(unsigned)F_h00_463E()%5;
        if (G_h01_4272[(row-14)*6] & G_h01_0468[value+9]) {
            event=&G_h01_434A;
            event->kind=value+9;
            event->row=row;
            event->zero=0;
            event->one=1;
            if (!G_h01_46E0 && G_h01_4188!=2)
                event->flags=2;
            else
                event->flags=1;
            event->first=G_h01_4274[row-14].first;
            event->second=G_h01_4274[row-14].second;
            F_h00_57D2(104);
        }
        return;
    }
    goto again;
}
