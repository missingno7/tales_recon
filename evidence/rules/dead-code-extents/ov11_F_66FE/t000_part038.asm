;:ts=8
	public	_F_h11_45EC
_F_h11_45EC:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.l	8(a5),a0
	move.l	8(a5),a1
	move.w	10(a1),d0
	sub.w	#1,d0
	move.w	6(a0),d1
	cmp.w	d0,d1
	blt	.4
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
	end
