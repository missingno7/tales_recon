/* Direct reconstruction candidate for ov13_F_012E. */
extern int G_h01_50EE, G_h01_50F0;
extern char G_h01_50F6;
extern int G_h01_5124, G_h01_5126;
extern char G_h01_512C;
extern int G_h01_515A, G_h01_515C;
extern char G_h01_5162;
extern int G_h01_5190, G_h01_5192;
extern char G_h01_5198;
extern int G_h01_5340, G_h01_5342;
extern char G_h01_5348;
extern int F_h00_3AE4();

recovered()
{
    F_h00_3AE4(&G_h01_50F6, G_h01_50EE, G_h01_50F0);
    F_h00_3AE4(&G_h01_512C, G_h01_5124, G_h01_5126);
    F_h00_3AE4(&G_h01_5162, G_h01_515A, G_h01_515C);
    F_h00_3AE4(&G_h01_5198, G_h01_5190, G_h01_5192);
    F_h00_3AE4(&G_h01_5348, G_h01_5340, G_h01_5342);
}
