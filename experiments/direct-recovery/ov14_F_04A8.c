struct Record { char first, second; char reserved[10]; };
extern struct Record G_h01_452E[36];
extern char F_h03_154E();
char recovered(a) char a;
{
    char i, best;
    int score, value;
    best = 35;
    score = 16000;
    for (i=1; i<35; ++i) {
        if (i == a || G_h01_452E[i].first || G_h01_452E[i].second) continue;
        value = F_h03_154E(a,i);
        if (value < score) {
            score = value;
            best = i;
        }
    }
    return best;
}
