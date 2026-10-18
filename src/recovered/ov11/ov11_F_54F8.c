struct Record {
	char pad0[12];
	int state;
	int value;
	char pad10[10];
	int x;
	int y;
	char gap[4];
	int first;
	int second;
	int third;
};

extern struct Record jg_scenery_object_records[1];
extern int jg_queue_background_restore_rectangle();
extern int jg_set_platform_record_state();

recovered(index,mode)
int index,mode;
{
	struct Record *record;
	record=&jg_scenery_object_records[index];
	record->state=2;
	if (record->value==0 || mode==5) record->value=mode;
	if (mode==5) {
		jg_queue_background_restore_rectangle(record->x,record->y,64,48,11);
		if (record->first) jg_set_platform_record_state(record->first,5);
		if (record->second) jg_set_platform_record_state(record->second,5);
		if (record->third) jg_set_platform_record_state(record->third,5);
	}
}