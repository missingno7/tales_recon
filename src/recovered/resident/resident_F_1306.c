extern int F_h00_4376();
extern int F_h00_86A8();
recovered(n)
int n;
{
 char c;
 int i,found;
 found=0;
 for(i=0;i<n;i++) {
  c=F_h00_4376();
  if(c & 64) { found=1; break; }
  F_h00_86A8(5L);
 }
 return found;
}
