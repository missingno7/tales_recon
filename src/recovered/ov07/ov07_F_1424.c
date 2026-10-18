struct Record {
    int amount;
    int flag;
    unsigned char state;
    char pad;
    int category;
    int f8;
    int f10;
    int f12;
    char rest[32];
};

struct Input {
    char pad[2];
    long text;
};

extern struct Record investment_market_state[16];
extern int G_h01_1466;
extern char *G_h01_46D6;
extern long arc_file;
extern long G_h01_6EAC;
extern struct Input *G_h01_6EA8;
extern int request_disk();
extern long Open();
extern int arc_read_index();
extern long F_h00_291E();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int poll_controller_and_keyboard_input();
extern int Delay();
extern int F_h00_3C0E();
extern int Close();
extern int F_h00_35DC();
extern int strcat();
extern int invest_draw_news_bulletin();
extern int F_h07_18F8();
char *F_h07_2050();

recovered(x, y)
long x;
long y;
{
    long l1;
    int i1;
    int i;
    char *q;
    char *p;
    char buf1[32];
    char buf2[40];
    int r;

    for (i = 0; i < 15; i++) {
        if (investment_market_state[i].state == 0)
            continue;
        G_h01_6EAC = arc_file;
        request_disk(1);
        arc_file = Open("DT1:invest.arc", 1005L);
        arc_read_index(arc_file);
        G_h01_6EA8 = 0;
        G_h01_6EA8 = F_h00_291E(i, G_h01_6EA8);
        switch (investment_market_state[i].state) {
        case 1:
            invest_draw_news_bulletin(i, x, y);
            F_h07_18F8(i, 2, 32, 35);
            buf1[0] = 0;
            p = F_h07_2050((long)investment_market_state[i].f12);
            strcat(buf1, "STOCK IS UP BY ");
            strcat(buf1, p);
            strcat(buf1, "%");
            F_h00_35DC(80, 100, buf1, 14, 0);
            investment_market_state[i].state = 5;
            F_h00_307C();
            G_h01_46D6 = (char *)&G_h01_1466;
            F_h00_31AA(&G_h01_1466);
            do {
                r = poll_controller_and_keyboard_input();
                Delay(5L);
            } while ((r & 0x80) == 0);
            break;
        case 2:
            invest_draw_news_bulletin(i, x, y);
            F_h07_18F8(i, 3, 32, 35);
            buf1[0] = 0;
            p = F_h07_2050((long)investment_market_state[i].f12);
            strcat(buf1, "STOCK IS DOWN BY ");
            strcat(buf1, p);
            strcat(buf1, "%");
            F_h00_35DC(80, 100, buf1, 14, 0);
            investment_market_state[i].state = 5;
            F_h00_307C();
            G_h01_46D6 = (char *)&G_h01_1466;
            F_h00_31AA(&G_h01_1466);
            do {
                r = poll_controller_and_keyboard_input();
                Delay(5L);
            } while ((r & 0x80) == 0);
            break;
        case 3:
            invest_draw_news_bulletin(i, x, y);
            F_h07_18F8(i, 2, 32, 35);
            F_h00_35DC(48, 100, "MAJOR PRICE CHANGE EXPECTED", 14, 0);
            buf2[0] = 0;
            q = F_h07_2050((long)investment_market_state[i].f10);
            strcat(buf2, "ON OR AROUND DAY ");
            strcat(buf2, q);
            F_h00_35DC(56, 110, buf2, 14, 0);
            investment_market_state[i].state = 0x83;
            F_h00_307C();
            G_h01_46D6 = (char *)&G_h01_1466;
            F_h00_31AA(&G_h01_1466);
            do {
                r = poll_controller_and_keyboard_input();
                Delay(5L);
            } while ((r & 0x80) == 0);
            break;
        case 4:
            invest_draw_news_bulletin(i, x, y);
            F_h07_18F8(i, 3, 32, 35);
            F_h00_35DC(48, 100, "MAJOR PRICE CHANGE EXPECTED", 14, 0);
            buf2[0] = 0;
            q = F_h07_2050((long)investment_market_state[i].f10);
            strcat(buf2, "ON OR AROUND DAY ");
            strcat(buf2, q);
            F_h00_35DC(56, 110, buf2, 14, 0);
            investment_market_state[i].state = 0x84;
            F_h00_307C();
            G_h01_46D6 = (char *)&G_h01_1466;
            F_h00_31AA(&G_h01_1466);
            do {
                r = poll_controller_and_keyboard_input();
                Delay(5L);
            } while ((r & 0x80) == 0);
            break;
        default:
            break;
        }
        F_h00_3C0E(G_h01_6EA8);
        Close(arc_file);
        arc_file = G_h01_6EAC;
        request_disk(1);
        arc_read_index(arc_file);
    }
}
