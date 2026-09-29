struct Record { int ignored; int value1; int value2; int value3; int value4; int value5; int value6; };
extern struct Record G_h01_8A66[1];
extern int F_h11_5C42();
extern int F_h11_54F8();
extern int F_h11_2E26();
extern int F_h11_66FE();
extern int F_h11_717A();

recovered(a,b,c)
int a,b,c;
{
    struct Record *p,*last;

    if (b<0) b=0;
    p=&G_h01_8A66[b/104];
    last=&G_h01_8A66[(b+c)/104];
    while (p<=last) {
        if (((int *)p)[0]) F_h11_5C42(((int *)p)[0],a);
        if (((int *)p)[1]) F_h11_54F8(((int *)p)[1],a);
        if (((int *)p)[5]) F_h11_2E26(((int *)p)[5],a);
        if (((int *)p)[4]) F_h11_66FE(((int *)p)[4],a);
        if (((int *)p)[6]) F_h11_717A(((int *)p)[6],a);
        p++;
    }
}
