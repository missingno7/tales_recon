struct Record {
    int value;
    char rest[12];
};

extern struct Record G_h01_34EC[40];

F_h11_4848()
{
    struct Record *p;

    for (p = G_h01_34EC; p - G_h01_34EC < 40; p++)
        p->value = 0;
}
