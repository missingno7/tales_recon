struct Item {
    char pad[2];
    int value;
};

extern char G_h01_4528[432];
extern char G_h01_452E[432];
extern char G_h01_452F[432];

unsigned char recovered(skip)
char skip;
{
    char i,chosen;
    int best,value;

    best=0;
    chosen=35;
    for (i=1;i<35;i++) {
        if (i!=skip && !G_h01_452E[(long)i*12] && !G_h01_452F[(long)i*12]) {
            value=(*(struct Item **)(G_h01_4528+(long)i*12))->value;
            if (value>best) {
                best=value;
                chosen=i;
            }
        }
    }
    return chosen;
}
