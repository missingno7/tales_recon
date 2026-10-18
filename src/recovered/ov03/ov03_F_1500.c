extern long screen_rast_port;
extern char game_day;
extern long total_money;
extern long G_h01_46EA;
extern long G_h01_46EE;
extern long G_h01_46F2;
extern int F_h00_307C();
extern int FreeSeg();
extern int SetRast();
extern int F_h06_0000();

recovered()
{
    SetRast(screen_rast_port,0L);
    G_h01_46EE += total_money;
    if (game_day >= 30)
        G_h01_46F2 += G_h01_46EA;
    F_h06_0000();
    FreeSeg(F_h06_0000);
    total_money = 0L;
    SetRast(screen_rast_port,0L);
    F_h00_307C();
}
