struct Record { char a,b; char reserved[10]; };
extern struct Record player_treasure_collected[36];
recovered(a)
char a;
{
 int i;
 for(i=1;i<35;++i) { if (i==a || player_treasure_collected[i].a || player_treasure_collected[i].b) continue; break; }
 return i;
}
