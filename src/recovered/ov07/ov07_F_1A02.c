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

extern struct Record investment_market_state[16];
extern unsigned char market_price_history[16][31];
extern char difficulty_level;
extern char game_day;
extern long total_money;
extern long G_h01_46EA;
extern long G_h01_46EE;
extern long G_h01_46F2;
extern char market_update_day;
extern int F_h00_463E();

recovered()
{
    int i;
    int t4;
    int cat;
    int v8;
    int q;
    int vC;
    int vE;
    int v10;
    int k;
    int v14;
    int t22;

    for (; market_update_day < game_day; ) {
        market_update_day++;
        for (i = 0; i < 15; i++) {
            if ((investment_market_state[i].state & 0x7f) == 3) {
                t22 = (F_h00_463E() & 3) * ((difficulty_level >> 1) + 1);
                if ((F_h00_463E() & 0xff) > 127)
                    t22 = -t22;
                if (market_update_day >= (char)investment_market_state[i].f10 + t22) {
                    investment_market_state[i].state = 1;
                    investment_market_state[i].amount += investment_market_state[i].amount * investment_market_state[i].f12 / 100;
                    investment_market_state[i].f8 = market_update_day;
                }
            }
            if ((investment_market_state[i].state & 0x7f) == 4) {
                if (market_update_day >= (char)investment_market_state[i].f10) {
                    investment_market_state[i].state = 2;
                    investment_market_state[i].amount += investment_market_state[i].amount * investment_market_state[i].f12 / 100;
                    investment_market_state[i].f12 *= -1;
                    investment_market_state[i].f8 = market_update_day;
                    if (investment_market_state[i].amount < 0)
                        investment_market_state[i].amount = 0;
                }
            }
        }
        for (i = 0; i < 15; i++) {
            t4 = 0;
            q = 0;
            if (investment_market_state[i].state == 0) {
                cat = investment_market_state[i].category;
                if (market_update_day < 30) {
                    vC = market_price_history[cat][market_update_day - 1];
                    vE = market_price_history[cat][market_update_day];
                    if (vC <= vE)
                        v8 = 1;
                    else
                        v8 = -1;
                    k = 0;
                    v10 = v8;
                    while (k < 15 && market_update_day + k < 31 && v8 == v10) {
                        if (market_price_history[cat][market_update_day + k - 1] <= market_price_history[cat][market_update_day + k])
                            v10 = 1;
                        else
                            v10 = -1;
                        k++;
                    }
                    if (v8 != v10 && v10 == 1) {
                        t4 = 5 * (3 - difficulty_level) + (market_update_day >> 2);
                        if (!investment_market_state[i].flag)
                            t4 = t4 >> 2;
                        if (t4 > (F_h00_463E() & 0xff)) {
                            if (G_h01_46EE + total_money < G_h01_46F2 + G_h01_46EA)
                                v14 = (F_h00_463E() & 0xf) + 110;
                            else
                                v14 = (F_h00_463E() & 7) + 105;
                            investment_market_state[i].f12 = v14 - market_price_history[cat][market_update_day - 1];
                            investment_market_state[i].state = 3;
                            investment_market_state[i].f8 = market_update_day;
                            investment_market_state[i].f10 = (3 - difficulty_level) * 3 + market_update_day + (k >> 1);
                            if (investment_market_state[i].f10 > 30)
                                investment_market_state[i].f10 = 30;
                        }
                    }
                    if (v8 != v10 && v10 == -1) {
                        q = 5 * (difficulty_level + 1) + (market_update_day >> 2);
                        if (!investment_market_state[i].flag)
                            q = q >> 2;
                        if (q > (F_h00_463E() & 0xff)) {
                            if (G_h01_46EE + total_money < G_h01_46F2 + G_h01_46EA)
                                v14 = (F_h00_463E() & 7) + 5;
                            else
                                v14 = (F_h00_463E() & 0xf) + 10;
                            investment_market_state[i].f12 = -(market_price_history[cat][market_update_day - 1] + v14);
                            investment_market_state[i].state = 4;
                            investment_market_state[i].f8 = market_update_day;
                            investment_market_state[i].f10 = (3 - difficulty_level) * 3 + market_update_day + (k >> 1);
                            if (investment_market_state[i].f10 > 30)
                                investment_market_state[i].f10 = 30;
                        }
                    }
                }
            }
        }
    }
}
