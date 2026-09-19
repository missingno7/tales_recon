struct Record { char first, second; char reserved[10]; };
extern struct Record G_h01_452E[36];
extern char F_h03_154E();
struct Value { int unused; int amount; };
struct Owner { struct Value *value; char reserved[8]; };
extern struct Owner G_h01_4528[36];
char recovered(a) char a;
{
    char i, best;
    int score, ratio, distance, amount;
    best = 35;
    score = 0;
    for (i=1; i<35; ++i) {
        if (i == a || G_h01_452E[i].first || G_h01_452E[i].second) continue;
        distance = F_h03_154E(a,i);
        amount = G_h01_4528[i].value->amount;
        ratio = amount / distance;
        if (ratio > score) {
            score = ratio;
            best = i;
        }
    }
    return best;
}
