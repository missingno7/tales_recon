struct State {
    int type;
    char mode;
    char clear;
    char enabled;
};

recovered(p)
struct State *p;
{
    if (p->type == 16 || p->type == 32) {
        p->enabled = 1;
        p->mode = 4;
    } else if (p->type == 19 || p->type == 35) {
        p->enabled = 0;
        p->clear = 0;
        p->mode = 3;
    } else {
        p->enabled = 1;
        p->mode = 3;
    }
}
