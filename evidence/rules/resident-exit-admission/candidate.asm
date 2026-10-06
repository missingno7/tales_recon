;:ts=8
	public	_recovered
_recovered:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	ext.l	d0
	move.l	d0,-4(a5)
	tst.l	_G_h01_B3A6
	beq	.4
	move.l	#0,d4
	bra	.8
.7
	move.w	d4,-(sp)
	jsr	_F_h00_8640
	add.w	#2,sp
.5
	add.w	#1,d4
.8
	cmp.w	_G_h01_2EB0,d4
	blt	.7
.6
	move.w	_G_h01_2EB0,d0
	muls.w	#6,d0
	move.l	d0,-(sp)
	move.l	_G_h01_B3A6,-(sp)
	jsr	_F_h00_8980
	add.w	#8,sp
.4
	tst.l	_G_h01_B3C8
	beq	.9
	move.l	_G_h01_B3C8,a0
	jsr	(a0)
.9
	tst.l	_G_h01_B3CE
	beq	.10
	move.l	_G_h01_B3CE,-(sp)
	jsr	_F_h00_8788
	add.w	#4,sp
.10
	tst.l	_G_h01_B3D2
	beq	.11
	move.l	_G_h01_B3D2,-(sp)
	jsr	_F_h00_8788
	add.w	#4,sp
.11
	tst.l	_G_h01_B3D6
	beq	.12
	move.l	_G_h01_B3D6,-(sp)
	jsr	_F_h00_8788
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
	tst.l	_G_h01_B3B0
	bne	.13
	tst.l	_G_h01_B3BC
	beq	.14
	move.w	_G_h01_B3BA,d0
	ext.l	d0
	move.l	d0,-(sp)
	move.l	_G_h01_B3BC,-(sp)
	jsr	_F_h00_8980
	move.w	_G_h01_B3B8,d0
	add.w	#1,d0
	ext.l	d0
	asl.l	#2,d0
	move.l	d0,-(sp)
	move.l	_G_h01_B3B4,-(sp)
	jsr	_F_h00_8980
	lea	16(sp),sp
.14
	bra	.15
.13
	jsr	_F_h00_8974
	move.l	_G_h01_B3B0,-(sp)
	jsr	_F_h00_8A12
	add.w	#4,sp
.15
		move.l	-4(a5),d0		;pick up return exit code
		move.l	_G_h01_B39E#,sp		;get back original stack pointer
		rts						;and exit
.16
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	d4
	public	_F_h00_8A12
	public	_F_h00_8974
	public	_F_h00_8788
	public	_F_h00_8980
	public	_F_h00_8640
	public	.begin
	dseg
	public	_G_h01_B3B4
	public	_G_h01_B3B8
	public	_G_h01_B3BA
	public	_G_h01_B3BC
	public	_G_h01_B3B0
	public	_G_h01_B3D6
	public	_G_h01_B3D2
	public	_G_h01_B3CE
	public	_G_h01_B3C8
	public	_G_h01_2EB0
	public	_G_h01_B3A6
	end
