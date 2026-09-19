/* Candidate member of the ov11_F_5962 / ov11_F_5C42 cluster. */
struct ClusterRecord {
    char pad0[8];
    int value8;
    int value10;
    char pad12[18];
    int state30;
    int value32;
    char pad34[6];
    int state40;
    int value42;
    char tail[8];
};
extern struct ClusterRecord G_h01_8BEC[1];
extern int F_h11_5C42();
extern int F_h11_66FE();
recovered(index,mode)
int index; int mode;
{
 struct ClusterRecord *record;
 record=&G_h01_8BEC[index];
 record->state40=2;
 if (record->value42==0 || mode==2) record->value42=mode;
 if (mode!=3 && record->value8) F_h11_5C42(index,2);
 if (mode!=8 && record->value10) F_h11_66FE(record->value10,2);
}