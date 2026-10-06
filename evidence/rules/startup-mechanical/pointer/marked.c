/* SDK-derived complete mixed startup experiment; original provider/TU unknown. */
#include <fcntl.h>
#include <exec/alerts.h>
#include <exec/memory.h>
#include <libraries/dosextens.h>
#include <workbench/startup.h>
#include <functions.h>
extern long G_h01_B39E;
extern long G_h01_B3AA;
extern int G_h01_B3AE;
extern int G_h01_B3B8;
extern int G_h01_B3BA;
extern char ** G_h01_B3B4;
extern char * G_h01_B3BC;
extern struct WBStartup * G_h01_B3B0;
extern struct _dev * G_h01_B3A6;
extern short G_h01_2EB0;
extern int F_h00_8534();
extern int F_h03_0000();
recovered(alen, aptr)
long alen;
char *aptr;
{
	register struct Process *pp, *F_h00_8964();
	void *_OpenLibrary(), *F_h00_899C(), *F_h00_892A();
	long F_h00_86C0(), F_h00_86EE(), F_h00_86E0();

#ifdef DETACH
	void do_detach();

	do_detach(&alen, &aptr);
#endif

	if ((G_h01_B3A6 = F_h00_892A(G_h01_2EB0*(long)sizeof(struct _dev),
													MEMF_CLEAR)) == 0) {
		F_h00_8744(AG_NoMemory, 0L);
#asm
	public _startup_asm_begin
_startup_asm_begin:
		move.l	_G_h01_B39E,sp		;get back original stack pointer
		rts						;and F_h00_8534
	public _startup_asm_end
_startup_asm_end:
#endasm
	}

	G_h01_B3A6[0].mode = O_RDONLY;
	G_h01_B3A6[1].mode = G_h01_B3A6[2].mode = O_WRONLY;

	G_h01_B3AA = G_h01_B39E - *((long *)G_h01_B39E+1) + 8;
	*(long *)G_h01_B3AA = 0x4d414e58L;

	pp = F_h00_8964(0L);
#ifdef DETACH
	if (alen) {
#else
	if (pp->pr_CLI) {
#endif
		F_h00_77A4(pp, alen, aptr);
		G_h01_B3AE = 1;
#ifndef DETACH
		G_h01_B3A6[0].mode |= O_STDIO;		/* shouldn't close if CLI */
		G_h01_B3A6[1].mode |= O_STDIO;
#endif
	}
	else {
		F_h00_8A3A(&pp->pr_MsgPort);
		G_h01_B3B0 = F_h00_899C(&pp->pr_MsgPort);
		if (G_h01_B3B0->sm_ArgList)
			F_h00_869C(G_h01_B3B0->sm_ArgList->wa_Lock);
		F_h00_7B24(pp, G_h01_B3B0);
		G_h01_B3B4 = (char **)G_h01_B3B0;
	}
	G_h01_B3A6[0].fd = F_h00_86C0();
	if (G_h01_B3A6[1].fd = F_h00_86EE())
		G_h01_B3A6[2].fd = F_h00_86E0("*", MODE_OLDFILE);
	F_h03_0000(G_h01_B3B8, G_h01_B3B4);
	F_h00_8534(0);
}
