;:ts=8
	public	_F_h11_62B4
_F_h11_62B4:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	#1,_G_h01_37F2
	move.b	_G_h01_46E0,d0
	ext.w	d0
	ext.l	d0
	bra	.4
.6
	move.w	#35,-4(a5)
	bra	.5
.7
	move.w	#25,-4(a5)
	bra	.5
.8
	move.w	#15,-4(a5)
	bra	.5
.4
	tst.l	d0
	beq	.6
	sub.l	#1,d0
	beq	.7
	sub.l	#1,d0
	beq	.8
.5
	move.w	#1,-2(a5)
	bra	.12
.11
	move.w	#2,-(sp)
	move.w	-2(a5),-(sp)
	jsr	_F_h11_5962
	add.w	#4,sp
	move.w	-2(a5),d0
	muls.w	#52,d0
	lea	_G_h01_8BEC+8,a0
	tst.w	(a0,d0.l)
	beq	.13
	move.w	-2(a5),d0
	muls.w	#52,d0
	lea	_G_h01_8BEC+48,a0
	move.w	#1,(a0,d0.l)
	move.w	-2(a5),d0
	muls.w	#52,d0
	lea	_G_h01_8BEC+44,a0
	move.l	d0,-(sp)
	move.w	-2(a5),d0
	muls.w	#52,d0
	lea	_G_h01_8BEC,a1
	move.w	(a1,d0.l),d1
	and.w	#1,d1
	bchg.l	#0,d1
	tst.w	d1
	bne	.14
	move.l	#4,d0
	bra	.15
.14
	move.l	#-8,d0
.15
	move.w	-2(a5),d1
	muls.w	#52,d1
	lea	_G_h01_8BEC,a1
	move.w	(a1,d1.l),d2
	muls.w	#53,d2
	add.w	d2,d0
	move.l	(sp)+,d1
	sub.w	#1,d0
	move.w	d0,(a0,d1.l)
	move.w	-2(a5),d0
	muls.w	#52,d0
	lea	_G_h01_8BEC+46,a0
	move.w	-2(a5),d1
	muls.w	#52,d1
	lea	_G_h01_8BEC+2,a1
	move.w	(a1,d1.l),d2
	asl.w	#5,d2
	add.w	#48,d2
	move.w	d2,(a0,d0.l)
	move.w	#3,-(sp)
	move.w	-2(a5),-(sp)
	jsr	_F_h11_5C42
	add.w	#4,sp
	move.w	-2(a5),d0
	muls.w	#52,d0
	lea	_G_h01_8BEC+46,a0
	move.w	(a0,d0.l),-(sp)
	move.w	-2(a5),d0
	muls.w	#52,d0
	lea	_G_h01_8BEC+44,a0
	move.w	(a0,d0.l),-(sp)
	move.w	#1,-(sp)
	move.w	-2(a5),d0
	muls.w	#52,d0
	lea	_G_h01_8BEC+18,a0
	add.l	a0,d0
	move.l	d0,-(sp)
	move.w	#24,-(sp)
	jsr	_F_h11_41F6
	lea	12(sp),sp
	bra	.16
.13
	tst.w	8(a5)
	beq	.17
	jsr	_F_h00_463E
	swap	d0
	clr.w	d0
	swap	d0
	divu.w	#100,d0
	swap	d0
	cmp.w	#25,d0
	bcc	.17
	move.w	-2(a5),d0
	ext.l	d0
	asl.l	#1,d0
	lea	_G_h01_940C,a0
	move.w	#1,(a0,d0.l)
.17
.16
.9
	add.w	#1,-2(a5)
.12
	move.w	-2(a5),d0
	cmp.w	_G_h01_37EC,d0
	blt	.11
.10
	clr.w	_G_h01_37F0
	clr.w	_G_h01_37EE
	tst.w	8(a5)
	beq	.18
	clr.w	-(sp)
	move.w	#1,-(sp)
	jsr	_F_h11_5A62
	add.w	#4,sp
	move.w	d0,-6(a5)
	clr.w	-(sp)
	move.w	#1,-(sp)
	jsr	_F_h11_5A12
	add.w	#4,sp
	move.w	d0,-6(a5)
.18
.19
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-6
.3	reg	
	public	_F_h00_463E
	public	_F_h11_41F6
	public	_F_h11_5C42
	public	_F_h11_5A62
	public	_F_h11_5A12
	public	_F_h11_5962
	public	.begin
	dseg
	public	_G_h01_940C
	public	_G_h01_8BEC
	public	_G_h01_46E0
	public	_G_h01_37F2
	public	_G_h01_37F0
	public	_G_h01_37EE
	public	_G_h01_37EC
	end
