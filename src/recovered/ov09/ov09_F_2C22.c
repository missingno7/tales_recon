extern int F_h00_35DC();
extern int F_h00_307C();
extern int Delay();
extern int shutdown_av();
recovered() {
 F_h00_35DC(8,8,"OUT OF MEMORY",15,0);
 F_h00_307C(); Delay(150L); shutdown_av("Out of Memory");
}
