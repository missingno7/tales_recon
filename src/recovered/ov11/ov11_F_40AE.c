/* Direct reconstruction candidate for ov11_F_40AE. */
struct Event {
    char pad0[2];
    int value2;
    char pad4[2];
    int kind;
    int value8;
    int value10;
    int value12;
    int value14;
    int value16;
    char pad18[6];
    int value18;
    int value1a;
    char rest[4];
};

extern short G_h01_A156;
extern struct Event jg_event_records[1];
extern int play_sound();
extern int Delay();

recovered(index)
int index;
{
    struct Event *record;

    record = &jg_event_records[index];
    G_h01_A156 = 0;
    Delay(5L);
    play_sound(91);
}
