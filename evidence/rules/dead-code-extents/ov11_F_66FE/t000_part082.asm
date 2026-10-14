;:ts=8
	public	_F_h11_6F78
_F_h11_6F78:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	muls.w	#34,d0
	lea	_G_h01_A554,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.b	_G_h01_46E0,d0
	ext.w	d0
	ext.l	d0
	bra	.4
.6
	move.w	14(a5),d0
	muls.w	#3,d0
	move.w	d0,14(a5)
	bra	.5
.7
	move.w	14(a5),d0
	muls.w	#2,d0
	move.w	d0,14(a5)
	bra	.5
.8
	bra	.5
.4
	tst.l	d0
	beq	.6
	sub.l	#1,d0
	beq	.7
	sub.l	#1,d0
	beq	.8
.5
	tst.w	8(a5)
	ble	.9
	move.w	14(a5),d0
	ext.l	d0
	move.l	d0,-(sp)
	move.l	-4(a5),a0
	move.w	20(a0),-(sp)
	move.l	-4(a5),a0
	move.w	18(a0),-(sp)
	move.w	12(a5),-(sp)
	move.w	10(a5),-(sp)
	jsr	_F_h11_2562
	add.w	#8,sp
	move.l	(sp)+,d1
	cmp.l	d0,d1
	ble	.9
	move.l	#1,d0
	bra	.10
.9
	move.l	#0,d0
.10
.11
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	
	public	_F_h11_2562
	public	.begin
	dseg
	public	_G_h01_A554
	public	_G_h01_46E0
	end
