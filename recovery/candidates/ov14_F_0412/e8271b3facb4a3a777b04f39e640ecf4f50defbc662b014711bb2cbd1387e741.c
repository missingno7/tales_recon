struct Item {
    char pad[2];
    int value;
};

extern char G_h01_4528[432];
extern char G_h01_452E[432];
extern char G_h01_452F[432];

char recovered(skip)
char skip;
{
    char chosen,i;
    int best,value;

    best=0;
    chosen=35;
    for (i=1;i<35;i++) {
        if (i!=skip && !G_h01_452E[i*12] && !G_h01_452F[i*12]) {
            value=(*(struct Item **)(G_h01_4528+i*12))->value;
            if (value>best) {
                best=value;
                chosen=i;
            }
        }
    }
    return chosen;
}
