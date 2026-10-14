;:ts=8
	public	_F_h11_0BB6
_F_h11_0BB6:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	move.w	d0,-6(a5)
	move.w	_G_h01_94C0,d0
	add.w	#14,d0
	asr.w	#5,d0
	cmp.w	#3,d0
	bge	.4
	move.w	_G_h01_94BA,d0
	ext.l	d0
	asl.l	#3,d0
	move.w	_G_h01_94C0,d1
	add.w	#14,d1
	asr.w	#5,d1
	ext.l	d1
	asl.l	#1,d1
	add.l	d1,d0
	lea	_G_h01_8B1C,a0
	move.w	(a0,d0.l),-2(a5)
	beq	.5
	move.w	-2(a5),d0
	ext.l	d0
	asl.l	#1,d0
	lea	_G_h01_940C,a0
	tst.w	(a0,d0.l)
	beq	.5
	move.w	_G_h01_94BA,d0
	muls.w	#53,d0
	move.w	d0,-4(a5)
	move.w	_G_h01_94C0,d0
	add.w	#14,d0
	asr.w	#5,d0
	asl.w	#5,d0
	add.w	#48,d0
	move.w	d0,-8(a5)
	move.w	-4(a5),d0
	add.w	#33,d0
	move.w	d0,-(sp)
	move.w	-6(a5),-(sp)
	move.w	-4(a5),d0
	add.w	#15,d0
	move.w	d0,-(sp)
	jsr	_F_h11_25D6
	add.w	#6,sp
	tst.w	d0
	beq	.6
	move.w	-8(a5),-(sp)
	move.w	_G_h01_94C0,d0
	add.w	#18,d0
	move.w	d0,-(sp)
	move.w	-8(a5),d0
	sub.w	#15,d0
	move.w	d0,-(sp)
	jsr	_F_h11_25D6
	add.w	#6,sp
	tst.w	d0
	beq	.6
	move.w	#32,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
	move.w	-2(a5),d0
	ext.l	d0
	asl.l	#1,d0
	lea	_G_h01_940C,a0
	clr.w	(a0,d0.l)
	add.l	#50,_G_h01_46E6
	move.w	#3,_G_h01_8A3C
.6
.5
.4
	move.w	_G_h01_94AE,d0
	ext.l	d0
	bra	.7
.9
.10
.13
	tst.w	_G_h01_94B4
	beq	.14
	bra	.12
.14
	move.w	_G_h01_94BA,d0
	ext.l	d0
	asl.l	#3,d0
	move.w	_G_h01_94C0,d1
	add.w	#14,d1
	asr.w	#5,d1
	ext.l	d1
	asl.l	#1,d1
	add.l	d1,d0
	lea	_G_h01_8B1C,a0
	tst.w	(a0,d0.l)
	bne	.15
	cmp.w	#3,_G_h01_94BC
	bge	.15
	move.w	_G_h01_94BA,d0
	sub.w	#1,d0
	ext.l	d0
	asl.l	#3,d0
	move.w	_G_h01_94C0,d1
	add.w	#14,d1
	asr.w	#5,d1
	ext.l	d1
	asl.l	#1,d1
	add.l	d1,d0
	lea	_G_h01_8B1C,a0
	tst.w	(a0,d0.l)
	beq	.16
	move.w	-6(a5),d0
	add.w	#1,d0
	move.w	d0,-(sp)
	move.w	_G_h01_94BA,d0
	sub.w	#1,d0
	move.w	d0,-(sp)
	clr.w	-(sp)
	jsr	_F_h11_5A12
	add.w	#4,sp
	move.w	(sp)+,d1
	cmp.w	d0,d1
	bge	.16
	bra	.12
.16
	move.w	_G_h01_94BA,d0
	add.w	#1,d0
	ext.l	d0
	asl.l	#3,d0
	move.w	_G_h01_94C0,d1
	add.w	#14,d1
	asr.w	#5,d1
	ext.l	d1
	asl.l	#1,d1
	add.l	d1,d0
	lea	_G_h01_8B1C,a0
	tst.w	(a0,d0.l)
	beq	.17
	move.w	-6(a5),d0
	add.w	#4,d0
	move.w	d0,-(sp)
	move.w	_G_h01_94BA,d0
	add.w	#1,d0
	move.w	d0,-(sp)
	clr.w	-(sp)
	jsr	_F_h11_5A62
	add.w	#4,sp
	move.w	(sp)+,d1
	cmp.w	d0,d1
	ble	.17
	bra	.12
.17
	move.w	#2,_G_h01_94AE
	move.w	#2,-(sp)
	jsr	_F_h11_4B0C
	add.w	#2,sp
.15
.11
.12
	bra	.8
.7
	sub.l	#1,d0
	beq	.9
	sub.l	#4,d0
	beq	.10
.8
.18
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-8
.3	reg	
	public	_F_h11_4B0C
	public	_F_h11_5A62
	public	_F_h11_5A12
	public	_F_h00_57D2
	public	_F_h11_25D6
	public	.begin
	dseg
	public	_G_h01_46E6
	public	_G_h01_940C
	public	_G_h01_8B1C
	public	_G_h01_8A3C
	public	_G_h01_94C0
	public	_G_h01_94BE
	public	_G_h01_94BC
	public	_G_h01_94BA
	public	_G_h01_94B4
	public	_G_h01_94B0
	public	_G_h01_94AE
	end
