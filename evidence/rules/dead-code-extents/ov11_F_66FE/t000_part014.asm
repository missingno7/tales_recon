;:ts=8
	public	_F_h11_2562
_F_h11_2562:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	sub.w	12(a5),d0
	tst.w	d0
	bge	.4
	move.w	8(a5),d0
	sub.w	12(a5),d0
	neg.w	d0
	bra	.5
.4
	move.w	8(a5),d0
	sub.w	12(a5),d0
.5
	ext.l	d0
	move.l	d0,-4(a5)
	move.w	10(a5),d0
	sub.w	14(a5),d0
	tst.w	d0
	bge	.6
	move.w	10(a5),d0
	sub.w	14(a5),d0
	neg.w	d0
	bra	.7
.6
	move.w	10(a5),d0
	sub.w	14(a5),d0
.7
	ext.l	d0
	move.l	d0,-8(a5)
	move.l	-4(a5),d1
	move.l	-4(a5),d0
	jsr	.mulu#
	move.l	-8(a5),d1
	move.l	d0,-(sp)
	move.l	-8(a5),d0
	jsr	.mulu#
	move.l	d0,d1
	move.l	(sp)+,d0
	add.l	d1,d0
.8
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-8
.3	reg	
	public	.begin
	dseg
	end
