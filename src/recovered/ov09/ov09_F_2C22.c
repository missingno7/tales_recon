extern int draw_text();
extern int switch_display_buffer();
extern int Delay();
extern int shutdown_av();
recovered() {
 draw_text(8,8,"OUT OF MEMORY",15,0);
 switch_display_buffer(); Delay(150L); shutdown_av("Out of Memory");
}
