struct Record {
    int field0;
    char unused0[22];
    int field24;
    int field26;
    int field28;
    int field30;
    int field32;
    int field34;
    char unused1[28];
};

struct TableCell {
    int value;
    char unused[12];
};

#define R(record, offset) (*((int *)((char *)(record) + (offset))))

extern struct Record G_h01_9FCE[1];
extern int G_h01_7A92;
extern int G_h01_8A3E;
extern struct TableCell G_h01_8A68[1];
extern int G_h01_A14E;
extern int F_h11_41F6();
extern int F_h11_4696();
extern int F_h11_583A();
extern int F_h11_54F8();

recovered(index)
int index;
{
    struct Record *record;
    int row;

    record = &G_h01_9FCE[index];
    if (R(record, 46) != 1)
        return;

    if (R(record, 8) != 0 && R(record, 48) == 0) {
        if (R(record, 50) <= G_h01_8A3E - 16) {
            R(record, 44) = 13;
            R(record, 46) = 0;
            G_h01_7A92 = 0;
            F_h11_41F6(2, (char *)record + 2, 13,
                       R(record, 30), R(record, 32));
        } else if (R(record, 50) < G_h01_8A3E + 320) {
            if (G_h01_A14E)
                R(record, 50) -= 8;
            else {
                G_h01_A14E = 1;
                R(record, 50) -= 32;
            }
        } else
            R(record, 46) = 0;
    }

    if (R(record, 48) == 3 && R(record, 8) > 2) {
        R(record, 52) += 8;
        if (R(record, 52) >= 169) {
            R(record, 44) = 16;
            R(record, 46) = 0;
            F_h11_41F6(2, (char *)record + 2, 16,
                       R(record, 30), R(record, 32));
            F_h11_4696(R(record, 56), R(record, 60), 24, 16,
                       index + 12);
            F_h11_583A(R(record, 56), R(record, 60), 24, 16, 11);
        }
    }

    row = R(record, 56) / 104;
    if (G_h01_8A68[row].value)
        F_h11_54F8(G_h01_8A68[row].value, 11);
}
