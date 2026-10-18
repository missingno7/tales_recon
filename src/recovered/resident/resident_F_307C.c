extern unsigned char G_h01_5390;
extern long G_h01_5388;
extern long G_h01_53E0;
extern long G_h01_53A6;
extern long G_h01_53B4;
extern long G_h01_53A2;
extern long screen_rast_port;
extern long G_h01_46D2;
extern int WaitBOVP();
extern int LoadView();

recovered()
{
    G_h01_53A6 = ((long *)&G_h01_53E0)[G_h01_5390];
    G_h01_5390 ^= 1;
    ((long *)screen_rast_port)[1] = ((long *)&G_h01_5388)[G_h01_5390];
    G_h01_46D2 = ((long *)&G_h01_5388)[G_h01_5390];
    WaitBOVP(&G_h01_53B4);
    LoadView(&G_h01_53A2);
}
