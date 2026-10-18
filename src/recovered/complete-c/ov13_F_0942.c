/* Structural candidate. The original BRA at 0D7C makes the alert block
 * unreachable; the producing source form remains unproved. */
extern int play_sound();
extern long F_h00_291E();
extern int F_h00_35DC();
extern unsigned int F_h00_463E();
extern int BltBitMap();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int clear_input_direction_and_fire_state();
extern int poll_controller_and_keyboard_input();
extern int Delay();
extern int F_h00_3B84();
extern int F_h00_330E();
extern int F_h13_0746();
extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern char G_h01_14E6[1];
recovered() {
 char chosen[5],other[5];
 int key,otherkey,index,command,inner,x,y;
 char *image;
 int alerts;
 alerts=0; play_sound(33); chosen[4]=0; other[4]=0;
 image=0L; image=F_h00_291E(40,image);
 F_h00_35DC(64,24,"This is Gyro Gearloose's",16,0);
 F_h00_35DC(40,32,"SUPER ANTI-SPY SECURITY SYSTEM.",12,0);
 F_h00_35DC(80,40,"Decode the following ",16,0);
 F_h00_35DC(72,48,"message to prove that",16,0);
 F_h00_35DC(64,56,"you are not a Beagle Boy.",16,0);
 for(index=0;index<4;index++) {
  key=F_h00_463E()%26;
  for(command=0;command<index;command++) { if(chosen[command]==key+65) { break; } }
  if(command<index) index--;
  else {
   chosen[index]=key+65;
   BltBitMap(image,(long)(unsigned int)(key<<3),0L,G_h01_46D2,(long)(144+(index<<3)),72L,8L,8L,192L,255L,0L);
  }
 }
 key=F_h00_463E()%10;
 for(index=0;index<10;index++) {
  if(index==key) {
   x=(index&1)?168:120;
   if(index<2)y=88;else if(index<4)y=96;else if(index<6)y=104;else if(index<8)y=112;else y=120;
   F_h00_35DC(x,y,chosen,1,0);
  } else {
   for(command=0;command<4;command++) {
    otherkey=F_h00_463E()%26;
    for(inner=0;inner<command;inner++) { if(other[inner]==otherkey+65) { break; } }
    if(inner<command)command--;else other[command]=otherkey+65;
   }
   x=(index&1)?168:120;
   if(index<2)y=88;else if(index<4)y=96;else if(index<6)y=104;else if(index<8)y=112;else y=120;
   F_h00_35DC(x,y,other,1,0);
  }
 }
 play_sound(0);
 BltBitMap(G_h01_46D2,0L,0L,G_h01_46CE,0L,0L,320L,200L,192L,255L,0L);
 F_h00_307C(); G_h01_46D6=G_h01_14E6; F_h00_31AA(G_h01_14E6); play_sound(111);
 BltBitMap(G_h01_46CE,0L,0L,G_h01_46D2,0L,0L,320L,200L,192L,255L,0L);
 F_h00_307C(); clear_input_direction_and_fire_state(); index=0; F_h13_0746(index); command=0;
 for(;;) {
  command=0; command=poll_controller_and_keyboard_input();
  if(command==3) { if(++index>9)index=0; }
  else if(command==7) { if(--index<0)index=9; }
  else if(command==5) { index+=2;if(index>9)index=0; }
  else if(command==1) { index-=2;if(index<0)index=9; }
  if(command) { F_h13_0746(index); Delay(5L); }
  clear_input_direction_and_fire_state();
  if(command&128) {
   if(index!=key) ;
   if(0) {
   if(!alerts) {
    F_h00_307C(); F_h00_35DC(48,144,"Possible Beagle Boy Break-In",0,14);
    play_sound(70);F_h00_307C();Delay(25L);alerts++;
   } else if(alerts==1) {
    F_h00_35DC(48,144,"                            ",0,0);
    for(inner=0;inner<3;inner++) {
     F_h00_307C();F_h00_35DC(96,144,"BEAGLE BOY ALERT",1,4);
     play_sound(70);F_h00_307C();Delay(25L);
     F_h00_307C();F_h00_35DC(96,144,"                ",0,0);
     F_h00_307C();Delay(25L);
    }
    alerts++;break;
   } else break;
   } else break;
  }
  Delay(1L);
 }
 F_h00_3B84(image); F_h00_330E(); play_sound(33); clear_input_direction_and_fire_state();
 if(index!=key)return 1;
 return 1;
}
