;:ts=8
	public	_F_h11_5AB0
_F_h11_5AB0:
	link	a5,#.2
	movem.l	.3,-(sp)
	clr.w	-2(a5)
	move.w	_G_h01_94BA,-4(a5)
	cmp.w	#1,8(a5)
	bne	.4
	add.w	#1,-4(a5)
	bra	.5
.4
	tst.w	8(a5)
	bne	.6
	sub.w	#1,-4(a5)
.6
.5
	tst.w	-4(a5)
	blt	.7
	cmp.w	#40,-4(a5)
	ble	.8
.7
	bra	.9
.8
	tst.w	8(a5)
	beq	.11
	cmp.w	#1,8(a5)
	bne	.10
.11
	cmp.w	#2,10(a5)
	bne	.12
	move.w	_G_h01_94BC,d0
	sub.w	#1,d0
	move.w	d0,-6(a5)
	tst.w	d0
	blt	.13
	move.w	-4(a5),d0
	ext.l	d0
	asl.l	#3,d0
	move.w	-6(a5),d1
	ext.l	d1
	asl.l	#1,d1
	add.l	d1,d0
	lea	_G_h01_8B1C,a0
	tst.w	(a0,d0.l)
	beq	.14
	move.l	12(a5),a0
	move.w	-6(a5),(a0)
	move.w	#1,-2(a5)
.14
.13
	bra	.15
.12
	cmp.w	#3,10(a5)
	bne	.16
	move.w	_G_h01_94BC,d0
	add.w	#1,d0
	move.w	d0,-6(a5)
	cmp.w	#3,d0
	bge	.17
	move.w	-4(a5),d0
	ext.l	d0
	asl.l	#3,d0
	move.w	-6(a5),d1
	ext.l	d1
	asl.l	#1,d1
	add.l	d1,d0
	lea	_G_h01_8B1C,a0
	tst.w	(a0,d0.l)
	beq	.18
	move.l	12(a5),a0
	move.w	-6(a5),(a0)
	move.w	#1,-2(a5)
.18
.17
.16
.15
	bra	.19
.10
	cmp.w	#2,8(a5)
	bne	.20
	tst.w	_G_h01_94BC
	ble	.21
	move.w	-4(a5),d0
	ext.l	d0
	asl.l	#3,d0
	move.w	_G_h01_94BC,d1
	sub.w	#1,d1
	ext.l	d1
	asl.l	#1,d1
	add.l	d1,d0
	lea	_G_h01_8B1C,a0
	tst.w	(a0,d0.l)
	beq	.22
	move.l	12(a5),a0
	move.w	_G_h01_94BC,d0
	sub.w	#1,d0
	move.w	d0,(a0)
	move.w	#1,-2(a5)
.22
.21
.20
.19
.9
	move.w	-2(a5),d0
.23
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-6
.3	reg	
	public	.begin
	dseg
	public	_G_h01_8B1C
	public	_G_h01_94BC
	public	_G_h01_94BA
	end
