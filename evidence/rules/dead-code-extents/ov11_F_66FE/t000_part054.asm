;:ts=8
	public	_F_h11_55B8
_F_h11_55B8:
	link	a5,#.2
	movem.l	.3,-(sp)
	tst.w	_G_h01_37F2
	beq	.4
	clr.w	_G_h01_37F2
	clr.w	-2(a5)
.7
	move.w	-2(a5),d0
	and.w	#1,d0
	bchg.l	#0,d0
	tst.w	d0
	bne	.8
	move.l	#-4,d0
	bra	.9
.8
	move.l	#-24,d0
.9
	move.w	-2(a5),d1
	muls.w	#53,d1
	add.w	d1,d0
	move.w	d0,-10(a5)
	move.w	#2,-4(a5)
.12
	move.w	-2(a5),d0
	ext.l	d0
	asl.l	#3,d0
	move.w	-4(a5),d1
	ext.l	d1
	asl.l	#1,d1
	add.l	d1,d0
	lea	_G_h01_8B1C,a0
	move.w	(a0,d0.l),-8(a5)
	tst.w	-8(a5)
	beq	.13
	move.w	-8(a5),d0
	muls.w	#52,d0
	lea	_G_h01_8BEC,a0
	add.l	a0,d0
	move.l	d0,-16(a5)
	move.l	-16(a5),a0
	tst.w	8(a0)
	bne	.14
	move.w	-4(a5),d0
	asl.w	#5,d0
	add.w	#48,d0
	move.w	d0,-12(a5)
	move.l	-16(a5),a0
	move.w	-10(a5),44(a0)
	move.l	-16(a5),a0
	move.w	-12(a5),46(a0)
.14
.13
.10
	sub.w	#1,-4(a5)
	tst.w	-4(a5)
	bge	.12
.11
.5
	add.w	#1,-2(a5)
	cmp.w	#24,-2(a5)
	blt	.7
.6
.4
	move.w	_G_h01_8A3E,d0
	sub.w	#12,d0
	ext.l	d0
	divs.w	#53,d0
	move.w	d0,-6(a5)
	tst.w	-6(a5)
	bge	.15
	move.l	#0,d0
	bra	.16
.15
	move.w	-6(a5),d0
.16
	move.w	d0,-6(a5)
	move.w	#6,-2(a5)
.19
	move.w	#2,-4(a5)
.22
	move.w	-6(a5),d0
	add.w	-2(a5),d0
	ext.l	d0
	asl.l	#3,d0
	move.w	-4(a5),d1
	ext.l	d1
	asl.l	#1,d1
	add.l	d1,d0
	lea	_G_h01_8B1C,a0
	move.w	(a0,d0.l),-8(a5)
	tst.w	-8(a5)
	beq	.23
	move.w	-8(a5),d0
	muls.w	#52,d0
	lea	_G_h01_8BEC,a0
	add.l	a0,d0
	move.l	d0,-16(a5)
	tst.w	_G_h01_8A3C
	beq	.24
	move.w	#2,-(sp)
	move.w	-8(a5),-(sp)
	jsr	_F_h11_5962
	add.w	#4,sp
.24
	move.l	-16(a5),a0
	tst.w	40(a0)
	ble	.25
	move.l	-16(a5),a0
	tst.w	8(a0)
	bne	.25
	move.l	_G_h01_9F5E,a0
	move.l	-16(a5),a1
	move.w	44(a1),d0
	sub.w	_G_h01_8A3E,d0
	move.w	d0,(a0)
	move.l	-16(a5),a0
	move.l	_G_h01_9F5E,a1
	move.w	46(a0),2(a1)
	move.l	-16(a5),a0
	move.l	_G_h01_9F5E,a1
	move.b	7(a0),52(a1)
	move.l	_G_h01_9F5E,-(sp)
	jsr	_F_h00_34E0
	add.w	#4,sp
	move.l	-16(a5),a0
	sub.w	#1,40(a0)
	move.l	-16(a5),a0
	tst.w	40(a0)
	bne	.26
	move.l	-16(a5),a0
	clr.w	42(a0)
.26
.25
.23
.20
	sub.w	#1,-4(a5)
	tst.w	-4(a5)
	bge	.22
.21
.17
	sub.w	#1,-2(a5)
	tst.w	-2(a5)
	bge	.19
.18
	move.w	#6,-2(a5)
.29
	move.w	-2(a5),d0
	add.w	-6(a5),d0
	muls.w	#53,d0
	sub.w	_G_h01_8A3E,d0
	move.w	d0,-10(a5)
	move.w	#2,-4(a5)
.32
	move.w	-6(a5),d0
	add.w	-2(a5),d0
	ext.l	d0
	asl.l	#3,d0
	move.w	-4(a5),d1
	ext.l	d1
	asl.l	#1,d1
	add.l	d1,d0
	lea	_G_h01_8B1C,a0
	move.w	(a0,d0.l),-8(a5)
	tst.w	-8(a5)
	beq	.33
	move.w	-8(a5),d0
	muls.w	#52,d0
	lea	_G_h01_8BEC,a0
	add.l	a0,d0
	move.l	d0,-16(a5)
	move.l	-16(a5),a0
	tst.w	40(a0)
	ble	.34
	move.w	-4(a5),d0
	asl.w	#5,d0
	add.w	#48,d0
	move.w	d0,-12(a5)
	move.w	-8(a5),d0
	ext.l	d0
	asl.l	#1,d0
	lea	_G_h01_940C,a0
	tst.w	(a0,d0.l)
	ble	.35
	move.l	-16(a5),a0
	tst.w	10(a0)
	bne	.35
	move.l	_G_h01_9FA2,a0
	move.w	-10(a5),d0
	add.w	#16,d0
	move.w	d0,(a0)
	move.l	_G_h01_9FA2,a0
	move.w	-12(a5),d0
	sub.w	#13,d0
	move.w	d0,2(a0)
	move.l	_G_h01_9FA2,-(sp)
	jsr	_F_h00_34E0
	add.w	#4,sp
.35
.34
.33
.30
	sub.w	#1,-4(a5)
	tst.w	-4(a5)
	bge	.32
.31
.27
	sub.w	#1,-2(a5)
	tst.w	-2(a5)
	bge	.29
.28
.36
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-16
.3	reg	
	public	_F_h00_34E0
	public	_F_h11_5962
	public	.begin
	dseg
	public	_G_h01_9FA2
	public	_G_h01_9F5E
	public	_G_h01_940C
	public	_G_h01_8BEC
	public	_G_h01_8B1C
	public	_G_h01_8A3C
	public	_G_h01_8A3E
	public	_G_h01_37F2
	end
