;:ts=8
	public	_F_h11_3532
_F_h11_3532:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	ext.l	d0
	asl.l	#6,d0
	lea	_G_h01_9FCE,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	cmp.w	#1,46(a0)
	bne	.4
	move.l	-4(a5),a0
	tst.w	8(a0)
	beq	.5
	move.l	-4(a5),a0
	tst.w	48(a0)
	bne	.5
	move.l	-4(a5),a0
	move.w	_G_h01_8A3E,d0
	sub.w	#16,d0
	move.w	50(a0),d1
	cmp.w	d0,d1
	bgt	.6
	move.l	-4(a5),a0
	move.w	#13,44(a0)
	move.l	-4(a5),a0
	clr.w	46(a0)
	clr.w	_G_h01_7A92
	move.l	-4(a5),a0
	move.w	32(a0),-(sp)
	move.l	-4(a5),a0
	move.w	30(a0),-(sp)
	move.w	#13,-(sp)
	move.l	-4(a5),a0
	add.l	#2,a0
	move.l	a0,-(sp)
	move.w	#2,-(sp)
	jsr	_F_h11_41F6
	lea	12(sp),sp
	bra	.7
.6
	move.l	-4(a5),a0
	move.w	_G_h01_8A3E,d0
	add.w	#320,d0
	move.w	50(a0),d1
	cmp.w	d0,d1
	blt	.8
	move.l	-4(a5),a0
	clr.w	46(a0)
	bra	.7
.8
	tst.w	_G_h01_A14E
	bne	.9
	move.w	#1,_G_h01_A14E
	move.l	-4(a5),a0
	sub.w	#32,50(a0)
	bra	.7
.9
	move.l	-4(a5),a0
	sub.w	#8,50(a0)
.7
	bra	.10
.5
	move.l	-4(a5),a0
	cmp.w	#3,48(a0)
	bne	.10
	move.l	-4(a5),a0
	cmp.w	#2,8(a0)
	ble	.10
	move.l	-4(a5),a0
	add.w	#8,52(a0)
	move.l	-4(a5),a0
	cmp.w	#169,52(a0)
	blt	.10
	move.l	-4(a5),a0
	move.w	#16,44(a0)
	move.l	-4(a5),a0
	clr.w	46(a0)
	move.l	-4(a5),a0
	move.w	32(a0),-(sp)
	move.l	-4(a5),a0
	move.w	30(a0),-(sp)
	move.w	#16,-(sp)
	move.l	-4(a5),a0
	add.l	#2,a0
	move.l	a0,-(sp)
	move.w	#2,-(sp)
	jsr	_F_h11_41F6
	lea	12(sp),sp
.10
	move.w	8(a5),d0
	add.w	#12,d0
	move.w	d0,-(sp)
	move.w	#16,-(sp)
	move.w	#24,-(sp)
	move.l	-4(a5),a0
	move.w	60(a0),-(sp)
	move.l	-4(a5),a0
	move.w	56(a0),-(sp)
	jsr	_F_h11_4696
	lea	10(sp),sp
	move.w	#11,-(sp)
	move.w	#16,-(sp)
	move.w	#24,-(sp)
	move.l	-4(a5),a0
	move.w	60(a0),-(sp)
	move.l	-4(a5),a0
	move.w	56(a0),-(sp)
	jsr	_F_h11_583A
	lea	10(sp),sp
	move.l	-4(a5),a0
	move.w	56(a0),d0
	ext.l	d0
	divs.w	#104,d0
	move.w	d0,-6(a5)
	move.w	-6(a5),d0
	muls.w	#14,d0
	lea	_G_h01_8A68,a0
	tst.w	(a0,d0.l)
	beq	.11
	move.w	#11,-(sp)
	move.w	-6(a5),d0
	muls.w	#14,d0
	lea	_G_h01_8A68,a0
	move.w	(a0,d0.l),-(sp)
	jsr	_F_h11_54F8
	add.w	#4,sp
.11
.4
.12
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-6
.3	reg	
	public	_F_h11_54F8
	public	_F_h11_583A
	public	_F_h11_4696
	public	_F_h11_41F6
	public	.begin
	dseg
	public	_G_h01_A14E
	public	_G_h01_8A68
	public	_G_h01_8A3E
	public	_G_h01_7A92
	public	_G_h01_9FCE
	end
