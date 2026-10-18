struct PortfolioRow {
    char name[34];
    int value;
    char rest[10];
};

extern int draw_text();
extern int draw_decimal_value();
extern int invest_calculate_share_price();
extern struct PortfolioRow investment_company_table[16];

recovered(start, selected)
int start;
int selected;
{
    int i;
    int slot;
    int value;
    char scratch[16];
    int y;
    unsigned char color;

    y = 40;
    for (i = start; i < start + 6; i++) {
        slot = i & 15;
        color = 0;
        if (slot == selected)
            color = 9;
        draw_text(32, y, "                                ", 1, color);
        if (slot == 15)
            draw_text(32, y, "RETURN TO OFFICE", 15, color);
        else {
            value = invest_calculate_share_price(slot);
            draw_decimal_value(248, y, (long)value, 1, color, 1);
            draw_text(32, y, investment_company_table[slot].name, 1, color);
            draw_decimal_value(280, y, (long)investment_company_table[slot].value, 1, color, 1);
        }
        y += 20;
    }
}
