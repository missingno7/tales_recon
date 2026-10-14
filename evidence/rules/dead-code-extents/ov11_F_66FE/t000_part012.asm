;:ts=8
	public	_F_h11_21F8
_F_h11_21F8:
	link	a5,#.2
	movem.l	.3,-(sp)
	clr.w	-2(a5)
.6
	move.w	-2(a5),d0
	ext.l	d0
	asl.l	#4,d0
	lea	_G_h01_9F0C,a0
	move.l	_G_h01_9F9E,(a0,d0.l)
.4
	add.w	#1,-2(a5)
	cmp.w	#4,-2(a5)
	blt	.6
.5
	clr.w	_G_h01_9F10
	move.w	#1,_G_h01_9F20
	move.w	#2,_G_h01_9F30
	move.w	#1,_G_h01_9F40
	clr.w	_G_h01_9FCC
	clr.w	_G_h01_9FC0
	clr.w	_G_h01_9FC2
	move.b	_G_h01_46E0,d0
	ext.w	d0
	ext.l	d0
	bra	.7
.9
	move.w	#350,_G_h01_9F4C
	bra	.8
.10
	move.w	#200,_G_h01_9F4C
	bra	.8
.11
	move.w	#100,_G_h01_9F4C
	bra	.8
.7
	tst.l	d0
	beq	.9
	sub.l	#1,d0
	beq	.10
	sub.l	#1,d0
	beq	.11
.8
.12
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-2
.3	reg	
	public	.begin
	dseg
	public	_G_h01_46E0
	public	_G_h01_9FCC
	public	_G_h01_9FC2
	public	_G_h01_9FC0
	public	_G_h01_9F4C
	public	_G_h01_9F40
	public	_G_h01_9F30
	public	_G_h01_9F20
	public	_G_h01_9F10
	public	_G_h01_9F9E
	public	_G_h01_9F0C
	end
