;:ts=8
	global	__cln,4
	public	__exit
__exit:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	ext.l	d0
	move.l	d0,-4(a5)
	tst.l	__devtab
	beq	.4
	move.l	#0,d4
	bra	.8
.7
	move.w	d4,-(sp)
	jsr	_close
	add.w	#2,sp
.5
	add.w	#1,d4
.8
	cmp.w	__numdev,d4
	blt	.7
.6
	move.w	__numdev,d0
	muls.w	#6,d0
	move.l	d0,-(sp)
	move.l	__devtab,-(sp)
	jsr	__FreeMem
	add.w	#8,sp
.4
	tst.l	__cln
	beq	.9
	move.l	__cln,a0
	jsr	(a0)
.9
	tst.l	_MathTransBase
	beq	.10
	move.l	_MathTransBase,-(sp)
	jsr	__CloseLibrary
	add.w	#4,sp
.10
	tst.l	_MathBase
	beq	.11
	move.l	_MathBase,-(sp)
	jsr	__CloseLibrary
	add.w	#4,sp
.11
	tst.l	_MathIeeeDoubBasBase
	beq	.12
	move.l	_MathIeeeDoubBasBase,-(sp)
	jsr	__CloseLibrary
	add.w	#4,sp
.12
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
	tst.l	_WBenchMsg
	bne	.13
	tst.l	__arg_lin
	beq	.14
	move.w	__arg_len,d0
	ext.l	d0
	move.l	d0,-(sp)
	move.l	__arg_lin,-(sp)
	jsr	__FreeMem
	move.w	__argc,d0
	add.w	#1,d0
	ext.l	d0
	asl.l	#2,d0
	move.l	d0,-(sp)
	move.l	__argv,-(sp)
	jsr	__FreeMem
	lea	16(sp),sp
.14
	bra	.15
.13
	jsr	__Forbid
	move.l	_WBenchMsg,-(sp)
	jsr	__ReplyMsg
	add.w	#4,sp
.15
		move.l	-4(a5),d0		;pick up return exit code
		move.l	__savsp#,sp		;get back original stack pointer
		rts						;and exit
.16
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	d4
	public	__ReplyMsg
	public	__Forbid
	public	__CloseLibrary
	public	__FreeMem
	public	_close
	public	.begin
	dseg
	public	_MathIeeeDoubBasBase
	public	_MathTransBase
	public	_MathBase
	public	_WBenchMsg
	public	__arg_lin
	public	__argv
	public	__arg_len
	public	__argc
	public	__numdev
	public	__devtab
	end
