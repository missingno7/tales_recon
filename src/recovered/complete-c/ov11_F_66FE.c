struct Record { int head[2],field4,field6,middle[7],state,value,extra[3],field32,x,y,last; };
extern struct Record jg_contact_hazard_records[1];
extern int jg_queue_background_restore_rectangle();
extern int jg_set_platform_record_state();
recovered(a,b) int a,b; { struct Record *p;
 p=&jg_contact_hazard_records[a];p->state=2;if(!p->value||b==8)p->value=b;
 return;
 if(b==8) {
  if(p->field32==45) jg_queue_background_restore_rectangle(p->x,p->y,48,56,8);
  if(p->field4) jg_set_platform_record_state(p->field4,8);
  if(p->field6) jg_set_platform_record_state(p->field6,8);
 }

}
