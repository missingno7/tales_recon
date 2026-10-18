/* Structural candidate. The original BRA at 0D7C makes the alert block
 * unreachable; the producing source form remains unproved. */
extern int play_sound();
extern long load_arc_record();
extern int draw_text();
extern unsigned int F_h00_463E();
extern int BltBitMap();
extern int switch_display_buffer();
extern int fade_palette_to_target();
extern int clear_input_direction_and_fire_state();
extern int poll_controller_and_keyboard_input();
extern int Delay();
extern int free_bitmap();
extern int fade_palette_to_black();
extern int draw_office_choice_outline();
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern char *palette_fade_target;
extern char G_h01_14E6[1];
recovered() {
 char chosen[5],other[5];
 int key,otherkey,index,command,inner,x,y;
 char *image;
 int alerts;
 alerts=0; play_sound(33); chosen[4]=0; other[4]=0;
 image=0L; image=load_arc_record(40,image);
 draw_text(64,24,"This is Gyro Gearloose's",16,0);
 draw_text(40,32,"SUPER ANTI-SPY SECURITY SYSTEM.",12,0);
 draw_text(80,40,"Decode the following ",16,0);
 draw_text(72,48,"message to prove that",16,0);
 draw_text(64,56,"you are not a Beagle Boy.",16,0);
 for(index=0;index<4;index++) {
  key=F_h00_463E()%26;
  for(command=0;command<index;command++) { if(chosen[command]==key+65) { break; } }
  if(command<index) index--;
  else {
   chosen[index]=key+65;
   BltBitMap(image,(long)(unsigned int)(key<<3),0L,active_screen_bitmap,(long)(144+(index<<3)),72L,8L,8L,192L,255L,0L);
  }
 }
 key=F_h00_463E()%10;
 for(index=0;index<10;index++) {
  if(index==key) {
   x=(index&1)?168:120;
   if(index<2)y=88;else if(index<4)y=96;else if(index<6)y=104;else if(index<8)y=112;else y=120;
   draw_text(x,y,chosen,1,0);
  } else {
   for(command=0;command<4;command++) {
    otherkey=F_h00_463E()%26;
    for(inner=0;inner<command;inner++) { if(other[inner]==otherkey+65) { break; } }
    if(inner<command)command--;else other[command]=otherkey+65;
   }
   x=(index&1)?168:120;
   if(index<2)y=88;else if(index<4)y=96;else if(index<6)y=104;else if(index<8)y=112;else y=120;
   draw_text(x,y,other,1,0);
  }
 }
 play_sound(0);
 BltBitMap(active_screen_bitmap,0L,0L,archive_image_bitmap,0L,0L,320L,200L,192L,255L,0L);
 switch_display_buffer(); palette_fade_target=G_h01_14E6; fade_palette_to_target(G_h01_14E6); play_sound(111);
 BltBitMap(archive_image_bitmap,0L,0L,active_screen_bitmap,0L,0L,320L,200L,192L,255L,0L);
 switch_display_buffer(); clear_input_direction_and_fire_state(); index=0; draw_office_choice_outline(index); command=0;
 for(;;) {
  command=0; command=poll_controller_and_keyboard_input();
  if(command==3) { if(++index>9)index=0; }
  else if(command==7) { if(--index<0)index=9; }
  else if(command==5) { index+=2;if(index>9)index=0; }
  else if(command==1) { index-=2;if(index<0)index=9; }
  if(command) { draw_office_choice_outline(index); Delay(5L); }
  clear_input_direction_and_fire_state();
  if(command&128) {
   if(index!=key) ;
   if(0) {
   if(!alerts) {
    switch_display_buffer(); draw_text(48,144,"Possible Beagle Boy Break-In",0,14);
    play_sound(70);switch_display_buffer();Delay(25L);alerts++;
   } else if(alerts==1) {
    draw_text(48,144,"                            ",0,0);
    for(inner=0;inner<3;inner++) {
     switch_display_buffer();draw_text(96,144,"BEAGLE BOY ALERT",1,4);
     play_sound(70);switch_display_buffer();Delay(25L);
     switch_display_buffer();draw_text(96,144,"                ",0,0);
     switch_display_buffer();Delay(25L);
    }
    alerts++;break;
   } else break;
   } else break;
  }
  Delay(1L);
 }
 free_bitmap(image); fade_palette_to_black(); play_sound(33); clear_input_direction_and_fire_state();
 if(index!=key)return 1;
 return 1;
}
