struct Header {
    int first;
    int second;
};

extern int draw_masked_sprite();
extern int draw_decimal_value();
extern long total_money;

recovered(p)
struct Header *p;
{
    p->first = 40;
    p->second = 172;
    draw_masked_sprite(p);
    draw_decimal_value(176, 175, total_money, 1, 9, 1);
}
