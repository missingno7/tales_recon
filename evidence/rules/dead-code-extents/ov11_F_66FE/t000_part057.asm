;:ts=8
	public	_F_h11_5A12
_F_h11_5A12:
	link	a5,#.2
	movem.l	.3,-(sp)
	tst.w	8(a5)
	beq	.4
	clr.w	-2(a5)
.7
	move.w	-2(a5),d0
	ext.l	d0
	asl.l	#1,d0
	lea	_G_h01_37F4,a0
	move.w	-2(a5),d1
	add.w	#1,d1
	muls.w	#53,d1
	add.w	#2,d1
	move.w	d1,(a0,d0.l)
.5
	add.w	#1,-2(a5)
	cmp.w	#40,-2(a5)
	blt	.7
.6
	bra	.8
.4
	move.w	10(a5),d0
	ext.l	d0
	asl.l	#1,d0
	lea	_G_h01_37F4,a0
	move.l	d0,d1
	move.w	(a0,d1.l),d0
.9
	movem.l	(sp)+,.3
	unlk	a5
	rts
.8
	bra	.9
.2	equ	-2
.3	reg	
	public	.begin
	dseg
	public	_G_h01_37F4
	end
