;:ts=8
	public	_F_h11_51C0
_F_h11_51C0:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	muls.w	#40,d0
	lea	_G_h01_3724,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	clr.w	-6(a5)
	clr.w	-8(a5)
	tst.w	_G_h01_8A3C
	beq	.4
	move.w	_G_h01_3720,_G_h01_3722
	bra	.5
.4
	sub.w	#1,_G_h01_3722
.5
	move.l	-4(a5),a0
	move.w	22(a0),d0
	ext.l	d0
	bra	.6
.8
	tst.w	_G_h01_3722
	bne	.9
	move.l	-4(a5),a0
	move.w	#18,22(a0)
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
.9
	bra	.7
.10
	move.l	-4(a5),a0
	move.w	30(a0),d0
	cmp.w	_G_h01_94BA,d0
	bne	.11
	move.w	_G_h01_94C0,d0
	add.w	#14,d0
	asr.w	#5,d0
	move.l	-4(a5),a0
	cmp.w	32(a0),d0
	bne	.11
	cmp.w	#5,_G_h01_94AE
	beq	.12
	cmp.w	#1,_G_h01_94AE
	beq	.12
	cmp.w	#12,_G_h01_94AE
	bne	.11
.12
	move.w	#14,_G_h01_94AE
	move.w	#14,-(sp)
	jsr	_F_h11_4B0C
	add.w	#2,sp
.11
	tst.w	_G_h01_3722
	bne	.13
	jsr	_F_h00_463E
	ext.l	d0
	divs.w	#100,d0
	swap	d0
	cmp.w	_G_h01_371C,d0
	bge	.14
	move.l	-4(a5),a0
	move.w	#14,22(a0)
	move.w	_G_h01_3720,d0
	muls.w	#3,d0
	move.w	d0,_G_h01_3722
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
	bra	.15
.14
	jsr	_F_h00_463E
	ext.l	d0
	divs.w	#100,d0
	swap	d0
	cmp.w	_G_h01_371E,d0
	bge	.16
	move.l	-4(a5),a0
	move.w	28(a0),d0
	add.w	#64,d0
	move.w	d0,-(sp)
	move.l	-4(a5),a0
	move.w	26(a0),d0
	add.w	#58,d0
	move.w	d0,-(sp)
	move.w	_G_h01_94C0,d0
	add.w	#16,d0
	move.w	d0,-(sp)
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	move.w	d0,-(sp)
	move.l	-4(a5),a0
	move.w	28(a0),d0
	add.w	#12,d0
	move.w	d0,-(sp)
	move.l	-4(a5),a0
	move.w	26(a0),d0
	add.w	#6,d0
	move.w	d0,-(sp)
	jsr	_F_h11_25F8
	lea	12(sp),sp
	tst.w	d0
	beq	.17
	cmp.w	#8,_G_h01_94AE
	beq	.17
	move.l	-4(a5),a0
	move.w	#19,22(a0)
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
	move.w	#99,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
.17
.16
.15
	bra	.7
.18
	cmp.w	#10,_G_h01_94AE
	beq	.19
	move.l	-4(a5),a0
	move.w	28(a0),d0
	add.w	#48,d0
	move.w	d0,-(sp)
	move.l	-4(a5),a0
	move.w	26(a0),d0
	add.w	#64,d0
	move.w	d0,-(sp)
	move.w	_G_h01_94C0,d0
	add.w	#16,d0
	move.w	d0,-(sp)
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	move.w	d0,-(sp)
	move.l	-4(a5),a0
	move.w	28(a0),-(sp)
	move.l	-4(a5),a0
	move.w	26(a0),-(sp)
	jsr	_F_h11_25F8
	lea	12(sp),sp
	tst.w	d0
	beq	.20
	sub.w	#24,_G_h01_94C0
	tst.w	_G_h01_94B6
	beq	.21
	clr.w	_G_h01_94B6
.21
	move.w	#2,_G_h01_94AE
	move.w	#2,-(sp)
	jsr	_F_h11_4B0C
	add.w	#2,sp
.20
.19
	move.l	-4(a5),-(sp)
	jsr	_F_h11_45EC
	add.w	#4,sp
	tst.w	d0
	beq	.22
	move.l	-4(a5),a0
	move.w	#18,22(a0)
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
	bra	.23
.22
	move.w	#1,-6(a5)
	move.l	-4(a5),-(sp)
	move.w	#11,-(sp)
	jsr	_F_h11_4474
	add.w	#6,sp
.23
	bra	.7
.6
	sub.l	#14,d0
	beq	.8
	sub.l	#4,d0
	beq	.10
	sub.l	#1,d0
	beq	.18
.7
.13
	tst.w	_G_h01_8A3C
	beq	.24
	clr.w	-(sp)
	move.w	8(a5),-(sp)
	jsr	_F_h11_54F8
	add.w	#4,sp
	bra	.25
.24
	tst.w	-6(a5)
	bne	.27
	move.w	_G_h01_94C0,d0
	add.w	#16,d0
	move.w	d0,-(sp)
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	move.w	d0,-(sp)
	move.l	-4(a5),a0
	move.w	28(a0),d0
	add.w	#24,d0
	move.w	d0,-(sp)
	move.l	-4(a5),a0
	move.w	26(a0),d0
	add.w	#32,d0
	move.w	d0,-(sp)
	jsr	_F_h11_2562
	add.w	#8,sp
	cmp.l	#10000,d0
	bge	.26
.27
	move.w	#5,-(sp)
	move.w	8(a5),-(sp)
	jsr	_F_h11_54F8
	add.w	#4,sp
	bra	.28
.26
	move.l	-4(a5),a0
	move.w	26(a0),d0
	ext.l	d0
	divs.w	#104,d0
	move.w	d0,-10(a5)
	move.w	-10(a5),d0
	muls.w	#14,d0
	lea	_G_h01_8A6A,a0
	tst.w	(a0,d0.l)
	bne	.30
	move.w	-10(a5),d0
	sub.w	#1,d0
	muls.w	#14,d0
	lea	_G_h01_8A6A,a0
	tst.w	(a0,d0.l)
	beq	.29
.30
	move.l	-4(a5),a0
	add.w	#1,12(a0)
.29
.28
.25
	tst.w	-8(a5)
	beq	.31
	move.l	-4(a5),a0
	move.w	28(a0),-(sp)
	move.l	-4(a5),a0
	move.w	26(a0),-(sp)
	move.l	-4(a5),a0
	move.w	22(a0),-(sp)
	move.l	-4(a5),-(sp)
	move.w	#11,-(sp)
	jsr	_F_h11_41F6
	lea	12(sp),sp
.31
	tst.w	_G_h01_3722
	bgt	.32
	move.w	_G_h01_3720,_G_h01_3722
.32
.33
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-10
.3	reg	
	public	_F_h00_57D2
	public	_F_h00_463E
	public	_F_h11_41F6
	public	_F_h11_2562
	public	_F_h11_4474
	public	_F_h11_45EC
	public	_F_h11_4B0C
	public	_F_h11_25F8
	public	_F_h11_54F8
	public	.begin
	dseg
	public	_G_h01_94C0
	public	_G_h01_94BE
	public	_G_h01_94BA
	public	_G_h01_94B6
	public	_G_h01_94B0
	public	_G_h01_94AE
	public	_G_h01_8A3C
	public	_G_h01_8A6A
	public	_G_h01_3722
	public	_G_h01_3720
	public	_G_h01_371E
	public	_G_h01_371C
	public	_G_h01_3724
	end
