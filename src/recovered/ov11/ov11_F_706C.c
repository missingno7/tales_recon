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

extern struct Record jg_end_trigger_records[1];
extern int G_h01_8A3C;
extern int G_h01_8A3E;
extern struct Output *G_h01_9F76;
extern int draw_masked_sprite();

recovered(n)
int n;
{
    struct Record *record;

    record=&jg_end_trigger_records[n];
    if (G_h01_8A3C>0 || record->count>0) {
        G_h01_9F76->first=record->first-G_h01_8A3E;
        G_h01_9F76->second=record->second;
        draw_masked_sprite(G_h01_9F76);
        record->count=G_h01_8A3C ? 2 : record->count-1;
    }
}
