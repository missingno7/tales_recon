/* resident_F_5392 candidate v1 (baseline, no parent).
   Mechanical access view: the long global input_device_io_request addresses a record whose
   word at +0x1c is set to 10 and whose long at +0x28 receives the address of
   input_device_handler_interrupt_record. That pointer value is then passed to four tail routines, and
   input_device_message_port is passed to the last one. Names are mechanical offsets. */
struct RecView { char pad0[28]; short field_1c; char pad1[10]; long field_28; };

extern long input_device_message_port;
extern long input_device_io_request;
extern long input_device_handler_interrupt_record;
extern int DoIO();
extern int CloseDevice();
extern int F_h00_8894();
extern int F_h00_8820();

recovered()
{
	((struct RecView *)input_device_io_request)->field_1c = 10;
	((struct RecView *)input_device_io_request)->field_28 = (long)&input_device_handler_interrupt_record;
	DoIO(input_device_io_request);
	CloseDevice(input_device_io_request);
	F_h00_8894(input_device_io_request);
	F_h00_8820(input_device_message_port);
}
