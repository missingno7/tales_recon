;:ts=8
	public	_recovered
_recovered:
	link	a5,#.2
	movem.l	.3,-(sp)
	pea	65536
	move.w	_G_h01_2EB0,d0
	muls.w	#6,d0
	move.l	d0,-(sp)
	jsr	_F_h00_892A
	move.l	d0,_G_h01_B3A6
	add.w	#8,sp
	bne	.4
	clr.l	-(sp)
	pea	65536
	jsr	_F_h00_8744
	add.w	#8,sp
	public _startup_asm_begin
_startup_asm_begin:
		move.l	_G_h01_B39E,sp		;get back original stack pointer
		rts						;and F_h00_8534
	public _startup_asm_end
_startup_asm_end:
.4
	move.l	_G_h01_B3A6,a0
	clr.w	4(a0)
	move.l	_G_h01_B3A6,a0
	move.w	#1,16(a0)
	move.l	_G_h01_B3A6,a0
	move.w	#1,10(a0)
	move.l	_G_h01_B39E,a0
	move.l	_G_h01_B39E,d0
	sub.l	4(a0),d0
	add.l	#8,d0
	move.l	d0,_G_h01_B3AA
	move.l	_G_h01_B3AA,a0
	move.l	#1296125528,(a0)
	clr.l	-(sp)
	jsr	_F_h00_8964
	move.l	d0,a2
	tst.l	172(a2)
	add.w	#4,sp
	beq	.5
	move.l	12(a5),-(sp)
	move.l	8(a5),-(sp)
	move.l	a2,-(sp)
	jsr	_F_h00_77A4
	move.w	#1,_G_h01_B3AE
	move.l	_G_h01_B3A6,a0
	or.w	#-32768,4(a0)
	move.l	_G_h01_B3A6,a0
	or.w	#-32768,10(a0)
	lea	12(sp),sp
	bra	.6
.5
	pea	92(a2)
	jsr	_F_h00_8A3A
	pea	92(a2)
	jsr	_F_h00_899C
	move.l	d0,_G_h01_B3B0
	move.l	_G_h01_B3B0,a0
	tst.l	36(a0)
	add.w	#8,sp
	beq	.7
	move.l	_G_h01_B3B0,a0
	move.l	36(a0),a1
	move.l	(a1),-(sp)
	jsr	_F_h00_869C
	add.w	#4,sp
.7
	move.l	_G_h01_B3B0,-(sp)
	move.l	a2,-(sp)
	jsr	_F_h00_7B24
	move.l	_G_h01_B3B0,_G_h01_B3B4
	add.w	#8,sp
.6
	jsr	_F_h00_86C0
	move.l	_G_h01_B3A6,a0
	move.l	d0,(a0)
	jsr	_F_h00_86EE
	move.l	_G_h01_B3A6,a0
	move.l	d0,6(a0)
	beq	.8
	pea	1005
	pea	.1+0
	jsr	_F_h00_86E0
	move.l	_G_h01_B3A6,a0
	move.l	d0,12(a0)
	add.w	#8,sp
.8
	move.l	_G_h01_B3B4,-(sp)
	move.w	_G_h01_B3B8,-(sp)
	jsr	_F_h03_0000
	clr.w	-(sp)
	jsr	_F_h00_8534
	add.w	#8,sp
.9
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	a2
.1
	dc.b	42,0
	ds	0
	public	_F_h00_7B24
	public	_F_h00_869C
	public	_F_h00_8A3A
	public	_F_h00_77A4
	public	_F_h00_8744
	public	_F_h00_86E0
	public	_F_h00_86EE
	public	_F_h00_86C0
	public	_F_h00_892A
	public	_F_h00_899C
	public	_F_h00_8964
	public	_F_h03_0000
	public	_F_h00_8534
	public	.begin
	dseg
	public	_G_h01_2EB0
	public	_G_h01_B3A6
	public	_G_h01_B3B0
	public	_G_h01_B3B4
	public	_G_h01_B3B8
	public	_G_h01_B3AE
	public	_G_h01_B3AA
	public	_G_h01_B39E
	end
