;:ts=8
	public	_F_h11_6FFE
_F_h11_6FFE:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	#1,-6(a5)
	lea	_G_h01_A6A8,a0
	move.l	a0,-4(a5)
	bra	.7
.6
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	(a1),d0
	muls.w	#53,d0
	add.w	#12,d0
	move.w	d0,4(a0)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	2(a1),d0
	asl.w	#5,d0
	add.w	#21,d0
	move.w	d0,6(a0)
	move.w	#9,-(sp)
	move.w	-6(a5),-(sp)
	jsr	_F_h11_717A
	add.w	#4,sp
.4
	add.w	#1,-6(a5)
	add.l	#10,-4(a5)
.7
	cmp.w	#3,-6(a5)
	blt	.6
.5
	move.l	_G_h01_9F76,a0
	clr.b	52(a0)
.8
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-6
.3	reg	
	public	_F_h11_717A
	public	.begin
	dseg
	public	_G_h01_9F76
	public	_G_h01_A6A8
	end
