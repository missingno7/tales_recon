/* Direct reconstruction candidate for ov11_F_3F90. */
struct Event {
    char pad0[4];
    int value4;
    int value8;
    int padA;
    int valueC;
    int valueE;
};

extern int G_h01_94B0;
extern int G_h01_94BE;
extern int G_h01_A152;
extern int G_h01_A154;
extern int G_h01_A158;
extern struct Event G_h01_A15E[1];
extern int F_h11_25D6();

int recovered(a)
int a;
{
    int result;
    int page;
    int index;
    int screen_x;
    struct Event *event;

    result=-1;
    page=a/128+1;
    if (a%128<G_h01_A154)
        --page;
    screen_x=(page-1)*128+G_h01_A154;
    index=(G_h01_A158+page)%G_h01_A152;
    event=&G_h01_A15E[index];
    if (event->value4==1 && event->valueC<event->valueE)
        if (F_h11_25D6(event->value8+screen_x,
                        (G_h01_94B0>>8)+G_h01_94BE,
                        event->valueC+screen_x+10))
            result=index;
    return result;
}
