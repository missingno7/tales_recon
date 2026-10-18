extern int disable_audio_channel_interrupts();
extern int clear_audio_driver_state();
extern int wait_for_next_frame_tick();
extern int remove_input_device_handler();
extern int RemIntServer();
extern int Close();
extern int F_h00_4EC6();
extern long G_h01_A7CE;
extern long G_h01_A7D2;
extern long vertical_blank_interrupt_record;
recovered()
{
 disable_audio_channel_interrupts();
 clear_audio_driver_state();
 wait_for_next_frame_tick();
 RemIntServer(5L,&vertical_blank_interrupt_record);
 remove_input_device_handler();
 F_h00_4EC6();
 Close(G_h01_A7CE);
 Close(G_h01_A7D2);
}
