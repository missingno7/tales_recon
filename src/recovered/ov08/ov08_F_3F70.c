struct Record {
    int value;
    char rest[52];
};

extern struct Record G_h01_6F48[11];
extern struct Record G_h01_6F4A[11];
extern struct Record G_h01_6F50[11];
extern int free_bitmap_planes();

recovered()
{
    int i;

    i = 1;
    do {
        free_bitmap_planes(&G_h01_6F50[i],
                    G_h01_6F48[i].value,
                    G_h01_6F4A[i].value);
        ++i;
    } while (i < 11);
}
