;:ts=8
	public	_F_h11_5FB2
_F_h11_5FB2:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	muls.w	#52,d0
	lea	_G_h01_8BEC,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.w	_G_h01_94BE,d0
	ext.l	d0
	jsr	.Fflt#
	move.l	-4(a5),a0
	move.w	44(a0),d1
	ext.l	d1
	move.l	d0,-(sp)
	move.l	d1,d0
	jsr	.Fflt#
	move.l	d0,d1
	move.l	(sp)+,d0
	jsr	.Fsub#
	move.l	-4(a5),a0
	move.l	34(a0),a1
	move.w	8(a1),d1
	ext.l	d1
	move.l	d0,-(sp)
	move.l	d1,d0
	jsr	.Fflt#
	move.l	d0,d1
	move.l	(sp)+,d0
	jsr	.Fmul#
	move.l	#$d0000047,d1
	jsr	.Fdiv#
	jsr	.Ffix#
	move.w	d0,-6(a5)
	clr.w	-8(a5)
	move.l	-4(a5),a0
	move.l	34(a0),a1
	cmp.w	#2,4(a1)
	bne	.4
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	sub.w	_G_h01_37F0,d0
	move.l	-4(a5),a0
	sub.w	44(a0),d0
	cmp.w	#45,d0
	ble	.5
	add.w	#5,-6(a5)
	move.w	#-5,-8(a5)
.5
.4
	move.w	-6(a5),d0
	sub.w	_G_h01_37EE,d0
	add.w	d0,_G_h01_94C0
	move.w	-8(a5),d0
	sub.w	_G_h01_37F0,d0
	add.w	d0,_G_h01_94BE
	move.w	-6(a5),_G_h01_37EE
	move.w	-8(a5),_G_h01_37F0
.6
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-8
.3	reg	
	public	.begin
	dseg
	public	_G_h01_94C0
	public	_G_h01_94BE
	public	_G_h01_94B0
	public	_G_h01_8BEC
	public	_G_h01_37F0
	public	_G_h01_37EE
	end
