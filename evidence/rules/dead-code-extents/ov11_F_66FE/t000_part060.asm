;:ts=8
	public	_F_h11_5BC4
_F_h11_5BC4:
	link	a5,#.2
	movem.l	.3,-(sp)
	clr.w	-2(a5)
.6
	clr.w	-4(a5)
.9
	move.w	-2(a5),d0
	ext.l	d0
	asl.l	#3,d0
	move.w	-4(a5),d1
	ext.l	d1
	asl.l	#1,d1
	add.l	d1,d0
	lea	_G_h01_8B1C,a0
	tst.w	(a0,d0.l)
	beq	.10
	move.l	8(a5),a0
	move.w	-2(a5),(a0)
	move.l	12(a5),a0
	move.w	-4(a5),(a0)
.11
	movem.l	(sp)+,.3
	unlk	a5
	rts
.10
.7
	add.w	#1,-4(a5)
	cmp.w	#3,-4(a5)
	blt	.9
.8
.4
	add.w	#1,-2(a5)
	cmp.w	#6,-2(a5)
	blt	.6
.5
	bra	.11
.2	equ	-4
.3	reg	
	public	.begin
	dseg
	public	_G_h01_8B1C
	end
