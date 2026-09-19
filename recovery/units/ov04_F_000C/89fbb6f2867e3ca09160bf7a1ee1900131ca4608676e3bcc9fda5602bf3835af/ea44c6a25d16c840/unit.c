struct LinkEntry {
    char *target;
    char pad[8];
};

struct TargetEntry {
    char pad[40];
};

struct ShortTargetEntry {
    char pad[6];
};

struct FlagEntry {
    char value;
    char pad[11];
};

extern struct LinkEntry G_h01_4524[35];
extern struct LinkEntry G_h01_4528[35];
extern char G_h01_470A;
extern char G_h01_4C82;
extern struct FlagEntry G_h01_452E[35];
extern struct FlagEntry G_h01_452F[35];



recovered()
{
    int i;

    for (i = 0; i < 35; i++) {
        G_h01_4524[i].target = (char *)&G_h01_470A + (long)i * 40;
        G_h01_4528[i].target = (char *)&G_h01_4C82 + (long)i * 6;
        G_h01_452E[i].value = 0;
        G_h01_452F[i].value = 0;
    }
    F_h04_0104();
    F_h04_037E();
}

F_h04_0088(n,p) int n,*p; { char i; if(n>=35)return 0; for(i=0;i<35;i++)if(*p++==n)return 0; return 1; }

F_h04_00C4(a,b)
int a,b;
{
    a += b;
    if (a >= 35) a -= 35;
    return a;
}

F_h04_00E6(a)
int a;
{
    ++a;
    if (a >= 35) a = 1;
    return a;
}

/* Direct recovery candidate for ov04_F_0104. */
struct Location {
    char pad[30];
    int selected;
    int a;
    int b;
    int c;
    int d;
};

extern long G_h01_46DA;
extern char G_h01_470A;
extern int F_h00_0FDE();
extern long F_h00_86DC();
extern int F_h00_2816();
extern long F_h00_291E();
extern long F_h00_0976();
extern int F_h00_704E();
extern int F_h00_7AF0();
extern int F_h00_3C0E();
extern unsigned int F_h00_463E();
extern int F_h00_868C();




F_h04_0104()
{
    int count;
    struct Location *location;
    long state;
    long page;
    long saved;
    int choices[35];
    char text[81];
    int row;
    int picked;

    page = 0;
    row = 0;
    picked = 0;
    for (count = 1; count < 35; ++count)
        choices[count] = 36;
    saved = G_h01_46DA;
    F_h00_0FDE(1);
    G_h01_46DA = F_h00_86DC("DT1:loc.arc", 1005L);
    F_h00_2816(G_h01_46DA);
    page = 0;
    page = F_h00_291E(0, page);
    choices[0] = 0;
    location = (struct Location *)&G_h01_470A;
    state = *(long *)((char *)page + 2);
    state = F_h00_0976(state, text);
    F_h00_704E(text, "%d %d %d %d", &location->a, &location->b,
        &location->c, &location->d);
    location->selected = 0;
    state = F_h00_0976(state, text);
    F_h00_7AF0(location, text);
    F_h00_3C0E(page);
    row = F_h00_463E();
    row = (unsigned)row % 30;
    picked = F_h00_463E();
    picked = (unsigned)picked % 5;
    for (count = 1; count < 35; ++count) {
        while (!F_h04_0088(row, choices))
            row = F_h04_00E6(row);
        choices[(unsigned)row] = row;
        location = (struct Location *)(&G_h01_470A + (long)count * 40);
        page = 0;
        page = F_h00_291E(row, page);
        state = *(long *)((char *)page + 2);
        state = F_h00_0976(state, text);
        F_h00_704E(text, "%d %d %d %d", &location->a, &location->b,
            &location->c, &location->d);
        state = F_h00_0976(state, text);
        F_h00_7AF0(location, text);
        location->selected = row;
        F_h00_3C0E(page);
        row = F_h04_00C4(row, picked);
    }
    F_h00_868C(G_h01_46DA);
    G_h01_46DA = saved;
    F_h00_2816(G_h01_46DA);
}

struct Loot {
    char padding[38];
    int value;
};

struct Slot {
    int value;
    char text[4];
};

struct Object {
    char padding[2];
    long name;
};

extern long G_h01_46DA;
extern char G_h01_4705;
extern char G_h01_470A;
extern struct Loot G_h01_4732[35];
extern char G_h01_4C82;

extern int F_h00_0FDE();
extern long F_h00_86DC();
extern int F_h00_2816();
extern unsigned int F_h00_463E();
extern long F_h00_291E();
extern long F_h00_0976();
extern int F_h00_704E();
extern int F_h00_3C0E();
extern int F_h00_868C();

F_h04_037E()
{
    int i;
    int probe;
    struct Slot *slot;
    struct Loot *loot;
    long unused;
    long name;
    long result;
    long saved;
    char buffer[81];
    int value;

    result = 0;
    value = 0;
    saved = G_h01_46DA;
    F_h00_0FDE(1);
    G_h01_46DA = F_h00_86DC("DT1:loot.arc", 0x3edL);
    F_h00_2816(G_h01_46DA);
    slot = (struct Slot *)&G_h01_4C82;
    slot->value = 0;
    for (i = 1; i < 35; ++i) {
        loot = (struct Loot *)((char *)&G_h01_470A + (long)i * 40);
        if (loot->value)
            value = loot->value;
        else {
            value = (unsigned)F_h00_463E() % 37 + 1;
again:
            loot = G_h01_4732;
            probe = 1;
            do {
                if (loot->value == value)
                    break;
                ++probe;
                ++loot;
            } while (probe < 35);
            if (probe >= 35) {
                loot = (struct Loot *)((char *)&G_h01_470A + (long)i * 40);
                loot->value = value;
            }
            else {
                if ((unsigned)(value + 1) >= 37)
                    value = 1;
                else
                    ++value;
                goto again;
            }
        }
        slot = (struct Slot *)((char *)&G_h01_4C82 + (long)i * 6);
        if (value == 9)
            G_h01_4705 = ((char *)&i)[1];
        --value;
        result = 0;
        result = F_h00_291E(value, result);
        name = ((struct Object *)result)->name;
        name = F_h00_0976(name, buffer);
        F_h00_704E(buffer, "%d", slot->text);
        slot->value = value;
        F_h00_3C0E(result);
    }
    F_h00_868C(G_h01_46DA);
    G_h01_46DA = saved;
    F_h00_2816(G_h01_46DA);
}

