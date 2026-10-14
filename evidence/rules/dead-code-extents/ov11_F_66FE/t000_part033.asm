;:ts=8
	public	_F_h11_405A
_F_h11_405A:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	ext.l	d0
	asl.l	#5,d0
	lea	_G_h01_A16A,a0
	cmp.w	#4,(a0,d0.l)
	bne	.4
	move.l	#1,d0
	bra	.5
.4
	move.l	#0,d0
.5
.6
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	
	public	.begin
	dseg
	public	_G_h01_A16A
	end
