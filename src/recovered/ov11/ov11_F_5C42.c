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
extern int jg_queue_background_restore_rectangle();
extern int jg_set_platform_record_state();

recovered(index,mode)
int index;
int mode;
{
    struct ClusterRecord *record;

    record=&jg_platform_records[index];
    record->state30=2;
    if (record->value32==0 || mode==3) record->value32=mode;
    if (mode==3) {
        jg_queue_background_restore_rectangle(record->value2c,record->value2e-6,72,32,24);
        if (record->value14) jg_set_platform_record_state(record->value14,2);
        if (record->value16) jg_set_platform_record_state(record->value16,2);
    }
}
