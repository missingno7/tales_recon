extern int poll_controller_and_keyboard_input();
extern int Delay();
recovered(n)
int n;
{
 char c;
 int i,found;
 found=0;
 for(i=0;i<n;i++) {
  c=poll_controller_and_keyboard_input();
  if(c & 64) { found=1; break; }
  Delay(5L);
 }
 return found;
}
