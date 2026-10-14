;:ts=8
	public	_F_h11_5D14
_F_h11_5D14:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	muls.w	#52,d0
	lea	_G_h01_8BEC,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	clr.w	-10(a5)
	move.l	-4(a5),a0
	move.w	48(a0),-12(a5)
	move.l	-4(a5),a0
	move.w	48(a0),d0
	ext.l	d0
	bra	.4
.6
	move.w	_G_h01_94C0,d0
	add.w	#14,d0
	asr.w	#5,d0
	move.l	-4(a5),a0
	cmp.w	2(a0),d0
	bne	.7
	move.l	-4(a5),a0
	move.w	(a0),d0
	cmp.w	_G_h01_94BA,d0
	bne	.7
	move.w	#1,_G_h01_94B4
	move.w	8(a5),_G_h01_94D6
	move.w	#3,-12(a5)
	move.w	#1,-10(a5)
.7
	bra	.5
.8
	move.l	-4(a5),a0
	move.w	(a0),d0
	cmp.w	_G_h01_94BA,d0
	beq	.11
	cmp.w	#18,_G_h01_94AE
	bne	.10
.11
	tst.w	_G_h01_94B6
	beq	.9
.10
	move.w	#1,-12(a5)
	clr.w	_G_h01_94B4
	clr.w	_G_h01_94D6
	clr.w	_G_h01_37F0
	clr.w	_G_h01_37EE
	move.w	#1,-10(a5)
	bra	.12
.9
	move.w	#1,-10(a5)
	move.l	-4(a5),a0
	pea	18(a0)
	move.w	#24,-(sp)
	jsr	_F_h11_4474
	add.w	#6,sp
.12
	bra	.5
.13
	bra	.5
.4
	sub.l	#1,d0
	beq	.6
	sub.l	#2,d0
	beq	.8
	bra	.13
.5
	move.l	-4(a5),a0
	move.w	48(a0),d0
	cmp.w	-12(a5),d0
	beq	.14
	move.l	-4(a5),a0
	move.w	-12(a5),48(a0)
	move.l	-4(a5),a0
	move.w	46(a0),-(sp)
	move.l	-4(a5),a0
	move.w	44(a0),-(sp)
	move.w	-12(a5),-(sp)
	move.l	-4(a5),a0
	pea	18(a0)
	move.w	#24,-(sp)
	jsr	_F_h11_41F6
	lea	12(sp),sp
.14
	tst.w	_G_h01_8A3C
	beq	.15
	clr.w	-(sp)
	move.w	8(a5),-(sp)
	jsr	_F_h11_5C42
	add.w	#4,sp
	bra	.16
.15
	tst.w	-10(a5)
	beq	.17
	move.w	#3,-(sp)
	move.w	8(a5),-(sp)
	jsr	_F_h11_5C42
	add.w	#4,sp
	bra	.18
.17
	tst.w	_G_h01_7A92
	beq	.19
	pea	-8(a5)
	pea	-6(a5)
	move.w	_G_h01_7A92,-(sp)
	jsr	_F_h11_37A0
	lea	10(sp),sp
	tst.w	d0
	beq	.19
	move.l	-4(a5),a0
	move.w	46(a0),d0
	add.w	#32,d0
	move.w	d0,-(sp)
	move.l	-4(a5),a0
	move.w	44(a0),d0
	add.w	#64,d0
	move.w	d0,-(sp)
	move.w	-8(a5),-(sp)
	move.w	-6(a5),-(sp)
	move.l	-4(a5),a0
	move.w	46(a0),d0
	sub.w	#6,d0
	move.w	d0,-(sp)
	move.l	-4(a5),a0
	move.w	44(a0),-(sp)
	jsr	_F_h11_25F8
	lea	12(sp),sp
	tst.w	d0
	beq	.19
	move.w	#3,-(sp)
	move.w	8(a5),-(sp)
	jsr	_F_h11_5C42
	add.w	#4,sp
.19
.18
.16
.20
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-12
.3	reg	
	public	_F_h11_5C42
	public	_F_h11_4474
	public	_F_h11_41F6
	public	_F_h11_37A0
	public	_F_h11_25F8
	public	.begin
	dseg
	public	_G_h01_37F0
	public	_G_h01_37EE
	public	_G_h01_94D6
	public	_G_h01_94C0
	public	_G_h01_94BA
	public	_G_h01_94B6
	public	_G_h01_94B4
	public	_G_h01_94AE
	public	_G_h01_8BEC
	public	_G_h01_8A3C
	public	_G_h01_7A92
	end
