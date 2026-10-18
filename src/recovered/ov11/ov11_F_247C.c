struct Record { int ignored; int value1; int value2; int value3; int value4; int value5; int value6; };
extern struct Record jg_entity_row_dispatch_records[1];
extern int jg_set_platform_render_state();
extern int jg_set_p_section_object_state();
extern int jg_set_actor_state();
extern int jg_set_hazard_record_state();
extern int jg_set_end_trigger_effect_state();

recovered(a,b,c)
int a,c;
long b;
{
    struct Record *p,*last;

    if (((int *)&b)[0]<0) ((int *)&b)[0]=0;
    p=&jg_entity_row_dispatch_records[((int *)&b)[0]/104];
    last=&jg_entity_row_dispatch_records[(((int *)&b)[0]+c)/104];
    for (;p<=last;p++) {
        if (p->ignored) jg_set_platform_render_state(p->ignored,a);
        if (p->value1) jg_set_p_section_object_state(p->value1,a);
        if (p->value5) jg_set_actor_state(p->value5,a);
        if (p->value4) jg_set_hazard_record_state(p->value4,a);
        if (p->value6) jg_set_end_trigger_effect_state(p->value6,a);
    }
}
