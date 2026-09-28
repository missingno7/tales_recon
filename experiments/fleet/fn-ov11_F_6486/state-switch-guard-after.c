struct MotionRecord {
    char prefix[32];
    int field20;
    int field22;
    int field24;
    int field26;
};
extern struct MotionRecord G_h01_A464[1];
extern int G_h01_8A3C;
extern int G_h01_94AE;
extern int F_h11_45EC();
extern int F_h11_66FE();
extern int F_h11_41F6();
extern int F_h11_4B0C();
extern int F_h11_4474();

recovered(index)
int index;
{
    struct MotionRecord *state;
    state = &G_h01_A464[index];
    state->field26--;
    switch (state->field20) {
    case 20:
        break;
    case 45:
        G_h01_8A3C = 3;
        if (F_h11_45EC((char *)state + 10)) {
            state->field20 = 20;
            F_h11_66FE(index, 8);
            F_h11_41F6(8, (char *)state + 10, 20, state->field24, state->field22);
            G_h01_94AE = 2;
            F_h11_4B0C(2);
        } else {
            F_h11_66FE(index, 8);
            F_h11_4474(8, (char *)state + 10);
        }
        break;
    default:
        break;
    }
    if (G_h01_8A3C != 0)
        F_h11_66FE(index, 8);
    if (state->field26 <= 0)
        state->field26 = 20;
}
