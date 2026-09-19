struct Record {
    int unused0;
    int unused1;
    int first;
    int second;
    int count;
};
struct Output {
    int first;
    int second;
};

extern struct Record G_h01_A6A8[];
extern int G_h01_8A3C;
extern int G_h01_8A3E;
extern struct Output *G_h01_9F76;
extern int F_h00_34E0();

recovered(n)
int n;
{
    struct Record *record;

    record=&G_h01_A6A8[n];
    if (G_h01_8A3C<=0 && record->count<=0)
        return;
    G_h01_9F76->first=record->first-G_h01_8A3E;
    G_h01_9F76->second=record->second;
    F_h00_34E0(G_h01_9F76);
    record->count=G_h01_8A3C ? 2 : record->count-1;
}
