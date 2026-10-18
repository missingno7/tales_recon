extern int G_h01_B1E8;
extern char *G_h01_3AB4;
extern long arc_file;
extern char G_h01_A9CA[1024];
extern long Read();
extern int report_loader_error();

char
recovered()
{
    long amount;

    if (++G_h01_B1E8 >= 1024) {
        amount = Read(arc_file, G_h01_A9CA, 1024L);
        if (amount <= 0)
            report_loader_error(8000);
        G_h01_B1E8 = 0;
        G_h01_3AB4 = G_h01_A9CA;
    } else
        ++G_h01_3AB4;
    return *G_h01_3AB4;
}
