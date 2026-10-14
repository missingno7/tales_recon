;:ts=8
	public	_F_h11_4696
_F_h11_4696:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	16(a5),d0
	muls.w	#14,d0
	lea	_G_h01_34EC,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	cmp.w	#2,_G_h01_8A3C
	bge	.4
	move.w	_G_h01_8A3E,d0
	sub.w	d0,8(a5)
	tst.w	8(a5)
	bge	.5
	move.w	8(a5),d0
	add.w	d0,12(a5)
	tst.w	12(a5)
	bgt	.6
.7
	movem.l	(sp)+,.3
	unlk	a5
	rts
.6
	clr.w	8(a5)
	bra	.8
.5
	cmp.w	#320,8(a5)
	blt	.9
	bra	.7
.9
	move.w	8(a5),d0
	add.w	12(a5),d0
	cmp.w	#320,d0
	ble	.10
	move.w	#320,d0
	sub.w	8(a5),d0
	add.w	#8,d0
	move.w	d0,12(a5)
.10
.8
	tst.w	10(a5)
	bge	.11
	move.w	10(a5),d0
	add.w	d0,14(a5)
	tst.w	14(a5)
	bgt	.12
	bra	.7
.12
	clr.w	10(a5)
	bra	.13
.11
	cmp.w	#176,10(a5)
	ble	.14
	bra	.7
.14
	move.w	10(a5),d0
	add.w	14(a5),d0
	cmp.w	#176,d0
	ble	.15
	move.w	#176,d0
	sub.w	10(a5),d0
	move.w	d0,14(a5)
.15
.13
	tst.w	14(a5)
	bgt	.16
	bra	.7
.16
	tst.w	12(a5)
	bgt	.17
	bra	.7
.17
	move.l	-4(a5),a0
	move.w	#2,(a0)
	move.l	-4(a5),a0
	move.w	8(a5),2(a0)
	move.l	-4(a5),a0
	move.w	10(a5),4(a0)
	move.l	-4(a5),a0
	move.w	12(a5),6(a0)
	move.l	-4(a5),a0
	move.w	14(a5),8(a0)
	move.l	-4(a5),a0
	move.w	16(a5),10(a0)
.4
	bra	.7
.2	equ	-4
.3	reg	
	public	.begin
	dseg
	public	_G_h01_8A3E
	public	_G_h01_8A3C
	public	_G_h01_34EC
	end
