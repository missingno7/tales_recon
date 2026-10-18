struct ClusterRecord {
    char pad0[8];
    int value8;
    int value10;
    char pad12[2];
    int value14;
    int value16;
    char pad18[12];
    int state30;
    int value32;
    char pad34[6];
    int state40;
    int value42;
    int value2c;
    int value2e;
    char tail[4];
};

extern struct ClusterRecord jg_platform_records[1];
extern int jg_set_platform_render_state();
extern int jg_set_hazard_record_state();

recovered(index,mode)
int index;
int mode;
{
    struct ClusterRecord *record;

    record=&jg_platform_records[index];
    record->state40=2;
    if (record->value42==0 || mode==2) record->value42=mode;
    if (mode!=3 && record->value8) jg_set_platform_render_state(index,2);
    if (mode!=8 && record->value10) jg_set_hazard_record_state(record->value10,2);
}
