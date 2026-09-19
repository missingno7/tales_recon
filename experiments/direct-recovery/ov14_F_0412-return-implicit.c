struct Item { int pad; int value; };
struct Record { struct Item *item; int pad; char a; char b; char tail[4]; };
extern struct Record G_h01_4528[36];
recovered(skip)
char skip;
{
 char i, chosen;
 int best, value;
 best=0;
 chosen=35;
 for(i=1;i<35;i++) {
  if(i!=skip && !G_h01_4528[i].a && !G_h01_4528[i].b) {
   value=G_h01_4528[i].item->value;
   if(value>best) { best=value; chosen=i; }
  }
 }
 return chosen;
}
