/* Candidate for ov07_F_0612: state machine over key codes (historical reconstruction candidate). */
struct Input { char f0[2]; long text; };
struct Slot { int f0; int f2; char rest[50]; };
struct Holding { int shares; char rest[44]; };
struct Symbol { int code; char rest[44]; };
struct PortfolioRow { char data[46]; };

extern struct Input *G_h01_6EA8;
extern long G_h01_6EAC;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern long arc_file;
extern long total_money;
extern char G_h01_33E2;
extern struct PortfolioRow investment_company_table[16];
extern struct Holding G_h01_4D84[16];
extern struct Symbol G_h01_4D88[16];
extern int request_disk();
extern int arc_read_index();
extern long Open();
extern long F_h00_291E();
extern int F_h00_307C();
extern int F_h00_34E0();
extern int F_h00_35DC();
extern int F_h00_3C0E();
extern int poll_controller_and_keyboard_input();
extern int play_sound();
extern int Close();
extern int strlen();
extern int BltBitMap();
extern int F_h00_09C0();
extern int F_h07_0F30();
extern int F_h07_0E06();
extern int F_h07_0E7C();
extern int invest_calculate_share_price();
extern int F_h07_18F8();

recovered(arg, p)
int arg;
struct Slot *p;
{
    char scratch[72];
    int s4a;
    int s4c;
    int xs[4];
    int s56;
    int s58;
    int u1;
    int key;
    int u2;
    int s60;
    int s62;
    int s64;
    int s66;
    int s68;
    char buf[2];

    buf[1] = 0;
    while ((poll_controller_and_keyboard_input() & 0x80) == 0x80)
        ;
    s4a = 4;
    s4c = 7;
    xs[0] = 0xc0;
    xs[1] = 0xe0;
    xs[2] = 0x100;
    xs[3] = 0x120;
    s56 = 0;
    s62 = 0;
    s58 = 0;
    u1 = -1;
    u2 = 1;
    s64 = 1;
    BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
    G_h01_6EAC = arc_file;
    request_disk(1);
    arc_file = Open("DT1:invest.arc", 1005L);
    arc_read_index(arc_file);
    G_h01_6EA8 = 0;
    G_h01_6EA8 = F_h00_291E(arg, G_h01_6EA8);

    while (s58 == 0) {
        key = (unsigned char)poll_controller_and_keyboard_input();
        if (key & 0x40) {
            s58 = 1;
        } else if (key & 0x80) {
            if (s66 == 0) {
                play_sound(36);
                s66 = 1;
                switch (s56) {
                case 3:
                    s58 = 2;
                    break;
                case 0:
                    s58 = 1;
                    break;
                case 1:
                    s4a = 5;
                    if (s60 == 0) {
                        s62 = 5;
                    } else if (G_h01_4D84[arg].shares >= 99) {
                        s62 = 6;
                    } else if (total_money - s60 >= 0) {
                        total_money -= s60;
                        G_h01_4D84[arg].shares++;
                        s62 = 3;
                        G_h01_33E2 = 1;
                        s66 = 0;
                    } else {
                        s62 = 1;
                    }
                    break;
                case 2:
                    s4c = 6;
                    if (G_h01_4D84[arg].shares > 0) {
                        total_money += s60;
                        G_h01_4D84[arg].shares--;
                        s62 = 2;
                        G_h01_33E2 = 1;
                        s66 = 0;
                    } else {
                        s62 = 4;
                    }
                    break;
                default:
                    break;
                }
                s64 = 1;
            }
        } else {
            key &= 0x3f;
            switch (key) {
            case 7:
                if (s66 != 0)
                    break;
                play_sound(36);
                s66 = 1;
                s56 -= 1;
                if (s56 < 0)
                    s56 = 2;
                s64 = 1;
                break;
            case 3:
                if (s66 != 0)
                    break;
                s66 = 1;
                play_sound(36);
                s56 += 1;
                if (s56 > 2)
                    s56 = 0;
                s64 = 1;
                break;
            default:
                if (s66 != 0)
                    s64 = 1;
                s4a = 4;
                s4c = 7;
                s62 = 0;
                s66 = 0;
                break;
            }
        }
        if (s64 != 0) {
            p[3].f0 = 0xc0;
            p[3].f2 = 0xaf;
            F_h00_34E0(&p[3]);
            p[s4a].f0 = 0xe0;
            p[s4a].f2 = 0xaf;
            F_h00_34E0(&p[s4a]);
            p[s4c].f0 = 0x100;
            p[s4c].f2 = 0xaf;
            F_h00_34E0(&p[s4c]);
            F_h07_0F30(xs[s56]);
            s68 = strlen(&investment_company_table[arg]);
            F_h00_35DC(160 - s68 * 4, 8, &investment_company_table[arg], 7, 9);
            F_h07_0E06(p);
            F_h07_0E7C(&p[2]);
            F_h00_35DC(35, 23, "       COMPANY DESCRIPTION      ", 1, 7);
            F_h07_18F8(arg, 1, 32, 35);
            F_h00_35DC(32, 100, " TOTAL MONEY       CHART TYPE  ", 1, 7);
            buf[0] = G_h01_4D88[arg].code + 'A';
            F_h00_35DC(224, 113, buf, 1, 0);
            F_h00_35DC(96, 113, ".00", 14, 0);
            F_h00_09C0(96, 113, total_money, 14, 0, 1);
            F_h00_35DC(32, 127, " PRICE PER SHARE  SHARES OWNED  ", 1, 7);
            F_h00_09C0(232, 140, (long)G_h01_4D84[arg].shares, 14, 0, 1);
            F_h00_35DC(96, 140, ".00", 1, 0);
            s60 = invest_calculate_share_price(arg);
            F_h00_09C0(96, 140, (long)s60, 1, 0, 1);
            switch (s62) {
            case 1:
                F_h00_35DC(32, 150, "    NOT ENOUGH MONEY TO BUY     ", 1, 9);
                break;
            case 0:
                F_h00_35DC(35, 150, "                                ", 0, 0);
                break;
            case 3:
                F_h00_35DC(35, 150, "      ONE SHARE PURCHASED       ", 1, 15);
                play_sound(62);
                break;
            case 2:
                F_h00_35DC(35, 150, "         ONE SHARE SOLD         ", 1, 15);
                play_sound(63);
                break;
            case 4:
                F_h00_35DC(35, 150, "        NO SHARES TO SELL       ", 1, 9);
                break;
            case 5:
                F_h00_35DC(35, 150, "COMPANY BANKRUPT, NO MORE SHARES", 1, 9);
                break;
            case 6:
                F_h00_35DC(35, 150, "       SHARE LIMIT REACHED      ", 1, 9);
                break;
            default:
                break;
            }
            F_h00_307C();
            BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
            s64 = 0;
        }
    }
    F_h00_3C0E(G_h01_6EA8);
    Close(arc_file);
    arc_file = G_h01_6EAC;
    request_disk(1);
    arc_read_index(arc_file);
    return s58 - 1;
}
