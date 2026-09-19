extern long G_h01_46CA;
extern char G_h01_46E1;
extern long G_h01_46E6;
extern long G_h01_46EA;
extern long G_h01_46EE;
extern long G_h01_46F2;
extern int F_h00_307C();
extern int F_h00_7522();
extern int F_h00_8BC8();
extern int F_h06_0000();

recovered()
{
    F_h00_8BC8(G_h01_46CA,0L);
    G_h01_46EE += G_h01_46E6;
    if (G_h01_46E1 >= 30)
        G_h01_46F2 += G_h01_46EA;
    F_h06_0000();
    F_h00_7522(F_h06_0000);
    G_h01_46E6 = 0L;
    F_h00_8BC8(G_h01_46CA,0L);
    F_h00_307C();
}
