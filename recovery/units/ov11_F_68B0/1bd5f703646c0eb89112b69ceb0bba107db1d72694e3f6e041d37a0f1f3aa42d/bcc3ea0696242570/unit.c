struct State {
    int value0;
    int value2;
    int unused4;
    int value6;
    int value8;
    int code;
    int unusedc;
    int unusede;
    char *address;
    int value14;
};

struct Target {
    char padding[6];
    int value6;
};

extern char G_h01_9F0C[1];
extern char G_h01_9C2C[1];
extern char G_h01_9CBC[1];
extern char G_h01_9CFC[1];
extern char G_h01_9CEC[1];
extern char G_h01_9EBC[1];
extern char G_h01_9EAC[1];
extern char G_h01_9D9C[1];
extern char G_h01_9E5C[1];
extern char G_h01_9D6C[1];
extern char G_h01_9D3C[1];
extern char G_h01_9D4C[1];
extern char G_h01_9D2C[1];
extern int F_h00_57D2();
extern int F_h00_86A8();

F_h11_41F6(mode, state, kind, value0, value2)
int mode;
struct State *state;
int kind;
int value0;
int value2;
{
    state->value6 = 0;
    state->value14 = kind;
    state->value0 = value0;
    state->value2 = value2;

    switch (mode) {
    case 33:
        state->address = G_h01_9F0C;
        state->code = 4;
        F_h00_57D2(89);
        break;
    case 24:
        switch (kind) {
        case 1:
            state->code = 1;
            state->address = G_h01_9C2C;
            break;
        case 3:
            state->code = 6;
            state->address = G_h01_9C2C;
            break;
        }
        break;
    case 11:
        switch (kind) {
        case 14:
            state->code = 0;
            state->address = G_h01_9CEC;
            break;
        case 18:
            state->code = 0;
            state->address = G_h01_9CFC;
            break;
        case 19:
            state->code = 3;
            state->address = G_h01_9CBC;
            break;
        }
        break;
    case 8:
        switch (kind) {
        case 20:
            state->code = 1;
            state->address = G_h01_9EAC;
            break;
        case 45:
            state->code = 5;
            state->address = G_h01_9EBC;
            break;
        }
        break;
    case 2:
        switch (kind) {
        case 12:
            state->code = 2;
            state->address = G_h01_9D4C;
            break;
        case 11:
            state->code = 2;
            state->address = G_h01_9D2C;
            break;
        case 15:
            state->code = 3;
            state->address = G_h01_9D6C;
            break;
        case 13:
            state->code = 0;
            state->address = G_h01_9D3C;
            break;
        case 18:
            state->code = 12;
            state->address = G_h01_9D9C;
            F_h00_57D2(0);
            F_h00_86A8((long)5);
            F_h00_57D2(97);
            break;
        case 17:
            state->code = 5;
            state->address = G_h01_9E5C;
            break;
        case 16:
            state->code = 0;
            state->address = G_h01_9E5C;
            break;
        }
        break;
    }
    state->value8 = ((struct Target *)state->address)->value6;
}
struct Display {
    long value0;
    int value4;
    int value6;
    char padding[8];
};

struct Record {
    int input0;
    int input2;
    char padding0[28];
    int value20;
    int value22;
    int value24;
    int value26;
};

extern char G_h01_9EAC[1];
extern long G_h01_9F7E;
extern struct Record G_h01_A464[6];
extern int F_h11_41F6();

recovered()
{
    int i;
    struct Record *record;

    i = 0;
    do {
        ((struct Display *)G_h01_9EAC)[i].value0 = G_h01_9F7E;
        ++i;
    } while (i < 6);

    ((struct Display *)G_h01_9EAC)[0].value4 = 0;
    ((struct Display *)G_h01_9EAC)[1].value4 = 1;
    ((struct Display *)G_h01_9EAC)[1].value6 = 1;
    ((struct Display *)G_h01_9EAC)[2].value4 = 2;
    ((struct Display *)G_h01_9EAC)[2].value6 = 1;
    ((struct Display *)G_h01_9EAC)[3].value4 = 3;
    ((struct Display *)G_h01_9EAC)[3].value6 = 4;
    ((struct Display *)G_h01_9EAC)[4].value4 = 2;
    ((struct Display *)G_h01_9EAC)[4].value6 = 1;
    ((struct Display *)G_h01_9EAC)[5].value4 = 1;
    ((struct Display *)G_h01_9EAC)[5].value6 = 1;

    i = 0;
    do {
        record = &G_h01_A464[i];
        record->value22 = record->input0 * 53;
        record->value24 = record->input2 * 32 + 33;
        record->value20 = 20;
        record->value26 = 20;
        F_h11_41F6(8, (char *)record + 10, 20,
                    record->value22, record->value24);
        ++i;
    } while (i < 6);
}

