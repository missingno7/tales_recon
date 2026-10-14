;:ts=8
	public	_F_h11_5F2A
_F_h11_5F2A:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	10(a5),-(sp)
	move.w	16(a5),-(sp)
	move.w	8(a5),-(sp)
	jsr	_F_h11_25D6
	add.w	#6,sp
	tst.w	d0
	bne	.5
	move.w	10(a5),-(sp)
	move.w	18(a5),-(sp)
	move.w	8(a5),-(sp)
	jsr	_F_h11_25D6
	add.w	#6,sp
	tst.w	d0
	beq	.4
.5
	move.w	14(a5),-(sp)
	move.w	20(a5),-(sp)
	move.w	12(a5),-(sp)
	jsr	_F_h11_25D6
	add.w	#6,sp
	tst.w	d0
	bne	.6
	move.w	14(a5),-(sp)
	move.w	22(a5),-(sp)
	move.w	12(a5),-(sp)
	jsr	_F_h11_25D6
	add.w	#6,sp
	tst.w	d0
	beq	.4
.6
	move.l	#1,d0
	bra	.7
.4
	move.l	#0,d0
.7
.8
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	
	public	_F_h11_25D6
	public	.begin
	dseg
	end
