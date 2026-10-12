extern unsigned char G_h01_5390;
extern long G_h01_5388;
extern long G_h01_53E0;
extern long G_h01_53A6;
extern long G_h01_53B4;
extern long G_h01_53A2;
extern long G_h01_46CA;
extern long G_h01_46D2;
extern int F_h00_8C04();
extern int F_h00_8B32();

recovered()
{
    G_h01_53A6 = ((long *)&G_h01_53E0)[G_h01_5390];
    G_h01_5390 ^= 1;
    ((long *)G_h01_46CA)[1] = ((long *)&G_h01_5388)[G_h01_5390];
    G_h01_46D2 = ((long *)&G_h01_5388)[G_h01_5390];
    F_h00_8C04(&G_h01_53B4);
    F_h00_8B32(&G_h01_53A2);
}
