;:ts=8
	public	_F_h11_69A4
_F_h11_69A4:
	link	a5,#.2
	movem.l	.3,-(sp)
	clr.w	-6(a5)
.6
	move.w	-6(a5),d0
	muls.w	#34,d0
	lea	_G_h01_A554,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	12(a0),18(a1)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.l	-4(a5),a6
	move.w	14(a1),d0
	add.w	16(a6),d0
	move.w	d0,20(a0)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	18(a0),6(a1)
	move.l	-4(a5),a1
	move.w	18(a0),4(a1)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	20(a0),10(a1)
	move.l	-4(a5),a1
	move.w	20(a0),8(a1)
	move.l	-4(a5),a0
	move.w	#192,22(a0)
	move.l	-4(a5),a0
	move.w	#8,30(a0)
	move.l	-4(a5),a0
	move.w	#1,32(a0)
	add.w	#1,-6(a5)
.4
	cmp.w	#10,-6(a5)
	blt	.6
.5
.7
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-6
.3	reg	
	public	.begin
	dseg
	public	_G_h01_A554
	end
