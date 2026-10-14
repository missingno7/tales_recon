;:ts=8
	public	_F_h11_25D6
_F_h11_25D6:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	10(a5),d0
	cmp.w	8(a5),d0
	blt	.4
	move.w	10(a5),d0
	cmp.w	12(a5),d0
	bgt	.4
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
	public	_F_h11_25F8
_F_h11_25F8:
	link	a5,#.7
	movem.l	.8,-(sp)
	move.w	16(a5),-(sp)
	move.w	12(a5),-(sp)
	move.w	8(a5),-(sp)
	jsr	_F_h11_25D6
	add.w	#6,sp
	tst.w	d0
	beq	.9
	move.w	18(a5),-(sp)
	move.w	14(a5),-(sp)
	move.w	10(a5),-(sp)
	jsr	_F_h11_25D6
	add.w	#6,sp
	tst.w	d0
	beq	.9
	move.l	#1,d0
	bra	.10
.9
	move.l	#0,d0
.10
.11
	movem.l	(sp)+,.8
	unlk	a5
	rts
.7	equ	0
.8	reg	
	public	.begin
	dseg
	end
