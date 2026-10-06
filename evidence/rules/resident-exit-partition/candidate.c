/* Experimental complete SDK-derived mixed C/assembly object.
   Mechanical access views claim no original DATA/COMMON provider or types. */
struct DevView { long fd; short mode; };
extern struct DevView *G_h01_B3A6;
extern short G_h01_2EB0;
extern long G_h01_B3C8;
extern long G_h01_B3CE;
extern long G_h01_B3D2;
extern long G_h01_B3D6;
extern long G_h01_B3B0;
extern char *G_h01_B3BC;
extern int G_h01_B3BA;
extern int G_h01_B3B8;
extern char **G_h01_B3B4;
extern long G_h01_B39E;
extern int F_h00_8640();
extern int F_h00_8980();
extern int F_h00_8788();
extern int F_h00_8974();
extern int F_h00_8A12();
recovered(code)
{
	long ret = code;
	register int fd;

	if (G_h01_B3A6) {
		for (fd = 0 ; fd < G_h01_2EB0 ; fd++)
			F_h00_8640(fd);
		F_h00_8980(G_h01_B3A6, G_h01_2EB0*(long)sizeof(struct DevView));
	}
	if (G_h01_B3C8)
		(*(int (*)())G_h01_B3C8)();
	if (G_h01_B3CE)
		F_h00_8788(G_h01_B3CE);
	if (G_h01_B3D2)
		F_h00_8788(G_h01_B3D2);
	if (G_h01_B3D6)
		F_h00_8788(G_h01_B3D6);
	{
#asm
	public	_runtime_asm_begin0
_runtime_asm_begin0:
	mc68881
	move.l	4,a6				;get ExecBase
	btst.b	#4,$129(a6)			;check for 68881 flag in AttnFlags
	beq		1$					;skip if not
	move.l	a5,-(sp)
	lea		2$,a5
	jsr		-30(a6)				;do it in supervisor mode
	move.l	(sp)+,a5
	bra		1$
2$
	clr.l	-(sp)
	frestore (sp)+				;reset the ffp stuff
	rte							;and return
1$
	public	_runtime_asm_end0
_runtime_asm_end0:
#endasm
	}
	if (G_h01_B3B0 == 0) {
		if (G_h01_B3BC) {
			F_h00_8980(G_h01_B3BC, (long)G_h01_B3BA);
			F_h00_8980(G_h01_B3B4, (long)(G_h01_B3B8+1)*sizeof(*G_h01_B3B4));
		}
	}
	else {
		F_h00_8974();
		F_h00_8A12(G_h01_B3B0);
	}
	{
#asm
	public	_runtime_asm_begin1
_runtime_asm_begin1:
		move.l	-4(a5),d0		;pick up return exit code
		move.l	_G_h01_B39E#,sp		;get back original stack pointer
		rts						;and exit
	public	_runtime_asm_end1
_runtime_asm_end1:
#endasm
	}
}

