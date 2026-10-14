;:ts=8
	public	_F_h11_583A
_F_h11_583A:
	link	a5,#.2
	movem.l	.3,-(sp)
	cmp.w	#10,16(a5)
	bne	.4
	move.w	8(a5),d0
	add.w	12(a5),d0
	move.w	d0,-8(a5)
	move.w	10(a5),d0
	add.w	14(a5),d0
	move.w	d0,-10(a5)
	move.w	8(a5),d0
	sub.w	#24,d0
	ext.l	d0
	divs.w	#53,d0
	move.w	d0,8(a5)
	move.w	10(a5),d0
	sub.w	#48,d0
	asr.w	#5,d0
	move.w	d0,10(a5)
	move.w	-8(a5),d0
	add.w	#24,d0
	ext.l	d0
	divs.w	#53,d0
	move.w	d0,-8(a5)
	move.w	-10(a5),d0
	sub.w	#16,d0
	asr.w	#5,d0
	move.w	d0,-10(a5)
	bra	.5
.4
	move.w	8(a5),d0
	add.w	12(a5),d0
	move.w	d0,-8(a5)
	move.w	10(a5),d0
	add.w	14(a5),d0
	move.w	d0,-10(a5)
	move.w	8(a5),d0
	ext.l	d0
	divs.w	#53,d0
	move.w	d0,8(a5)
	move.w	10(a5),d0
	sub.w	#48,d0
	asr.w	#5,d0
	move.w	d0,10(a5)
	move.w	-8(a5),d0
	ext.l	d0
	divs.w	#53,d0
	move.w	d0,-8(a5)
	move.w	-10(a5),d0
	sub.w	#48,d0
	asr.w	#5,d0
	move.w	d0,-10(a5)
.5
	tst.w	8(a5)
	bge	.6
	clr.w	8(a5)
.6
	tst.w	10(a5)
	bge	.7
	clr.w	10(a5)
.7
	move.w	8(a5),-4(a5)
	bra	.11
.10
	move.w	10(a5),-6(a5)
	bra	.15
.14
	move.w	-4(a5),d0
	ext.l	d0
	asl.l	#3,d0
	move.w	-6(a5),d1
	ext.l	d1
	asl.l	#1,d1
	add.l	d1,d0
	lea	_G_h01_8B1C,a0
	move.w	(a0,d0.l),-2(a5)
	tst.w	-2(a5)
	beq	.16
	move.w	16(a5),-(sp)
	move.w	-2(a5),-(sp)
	jsr	_F_h11_5962
	add.w	#4,sp
.16
.12
	add.w	#1,-6(a5)
.15
	move.w	-6(a5),d0
	cmp.w	-10(a5),d0
	ble	.14
.13
.8
	add.w	#1,-4(a5)
.11
	move.w	-4(a5),d0
	cmp.w	-8(a5),d0
	ble	.10
.9
.17
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-10
.3	reg	
	public	_F_h11_5962
_F_h11_5962:
	link	a5,#.18
	movem.l	.19,-(sp)
	move.w	8(a5),d0
	muls.w	#52,d0
	lea	_G_h01_8BEC,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	move.w	#2,40(a0)
	move.l	-4(a5),a0
	tst.w	42(a0)
	beq	.21
	cmp.w	#2,10(a5)
	bne	.20
.21
	move.l	-4(a5),a0
	move.w	10(a5),42(a0)
.20
	cmp.w	#3,10(a5)
	beq	.22
	move.l	-4(a5),a0
	tst.w	8(a0)
	beq	.22
	move.w	#2,-(sp)
	move.w	8(a5),-(sp)
	jsr	_F_h11_5C42
	add.w	#4,sp
.22
	cmp.w	#8,10(a5)
	beq	.23
	move.l	-4(a5),a0
	tst.w	10(a0)
	beq	.23
	move.w	#2,-(sp)
	move.l	-4(a5),a0
	move.w	10(a0),-(sp)
	jsr	_F_h11_66FE
	add.w	#4,sp
.23
.24
	movem.l	(sp)+,.19
	unlk	a5
	rts
.18	equ	-4
.19	reg	
	public	_F_h11_66FE
	public	_F_h11_5C42
	public	.begin
	dseg
	public	_G_h01_8BEC
	public	_G_h01_8B1C
	end
