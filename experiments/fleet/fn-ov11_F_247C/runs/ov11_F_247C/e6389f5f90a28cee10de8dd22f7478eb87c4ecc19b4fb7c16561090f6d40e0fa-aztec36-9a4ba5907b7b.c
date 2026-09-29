struct Record { int ignored; int value1; int value2; int value3; int value4; int value5; int value6; };
extern struct Record G_h01_8A66[1];
extern int F_h11_5C42();
extern int F_h11_54F8();
extern int F_h11_2E26();
extern int F_h11_66FE();
extern int F_h11_717A();

recovered(a,b,c)
int a,c;
long b;
{
    struct Record *p,*last;

    if (((int *)&b)[0]<0) ((int *)&b)[0]=0;
    p=&G_h01_8A66[((int *)&b)[0]/104];
    last=&G_h01_8A66[(((int *)&b)[0]+c)/104];
    while (p<=last) {
        if (p->ignored) F_h11_5C42(p->ignored,a);
        if (p->value1) F_h11_54F8(p->value1,a);
        if (p->value5) F_h11_2E26(p->value5,a);
        if (p->value4) F_h11_66FE(p->value4,a);
        if (p->value6) F_h11_717A(p->value6,a);
        p++;
    }
}
