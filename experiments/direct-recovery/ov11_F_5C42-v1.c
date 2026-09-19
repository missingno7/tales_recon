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
    char pad44[12];
    int value2c;
    int value2e;
};
extern struct ClusterRecord G_h01_8BEE[1];
extern int F_h11_4696();
extern int recovered();
F_h11_5C42(index,mode)
int index; int mode;
{
 struct ClusterRecord *record;
 record=&G_h01_8BEE[index];
 record->state30=2;
 if (record->value32==0 || mode==3) record->value32=mode;
 if (mode==3) {
  F_h11_4696(record->value2c,record->value2e-6,72,32,24);
  if (record->pad12[2]) recovered(record->pad12[2],2);
  if (record->pad12[4]) recovered(record->pad12[4],2);
 }
}