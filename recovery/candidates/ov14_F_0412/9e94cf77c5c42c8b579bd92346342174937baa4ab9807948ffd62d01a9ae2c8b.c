struct Item {
    char pad[2];
    int value;
};
struct FlagRecord {
    char flag;
    char pad[11];
};
struct PointerRecord {
    struct Item *item;
    char pad[8];
};

extern struct PointerRecord G_h01_4528[36];
extern struct FlagRecord G_h01_452E[36];
extern struct FlagRecord G_h01_452F[36];

unsigned char recovered(skip)
char skip;
{
    char i,chosen;
    int best,value;

    best=0;
    chosen=35;
    for (i=1;i<35;i++) {
        if (i!=skip && !G_h01_452E[i].flag && !G_h01_452F[i].flag) {
            value=G_h01_4528[i].item->value;
            if (value>best) {
                best=value;
                chosen=i;
            }
        }
    }
    return chosen;
}
