#include <fcntl.h>
#include <exec/alerts.h>
#include <exec/memory.h>
#include <libraries/dosextens.h>
#include <workbench/startup.h>
#include <functions.h>
extern int recovered();
int (*candidate_reference)() = recovered;
main() { return 0; }
long G_h01_B39E;
long G_h01_B3AA;
int G_h01_B3AE;
int G_h01_B3B8;
int G_h01_B3BA;
char ** G_h01_B3B4;
char * G_h01_B3BC;
struct WBStartup * G_h01_B3B0;
struct _dev * G_h01_B3A6;
short G_h01_2EB0;
int F_h00_77A4() { return 0; }
int F_h00_7B24() { return 0; }
int F_h00_869C() { return 0; }
long F_h00_86C0() { return 0; }
long F_h00_86E0() { return 0; }
long F_h00_86EE() { return 0; }
int F_h00_8744() { return 0; }
void * F_h00_892A() { return 0; }
struct Process * F_h00_8964() { return 0; }
void * F_h00_899C() { return 0; }
int F_h00_8A3A() { return 0; }
#asm
	dseg
	public _F_h00_8534
_F_h00_8534:
	dc.w $4ef9
	dc.l _exit_body
	cseg
#endasm
exit_body() { return 0; }
