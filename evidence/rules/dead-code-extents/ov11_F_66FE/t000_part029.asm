;:ts=8
	public	_F_h11_3A24
_F_h11_3A24:
	link	a5,#.2
	movem.l	.3,-(sp)
	clr.w	-2(a5)
	bra	.7
.6
	move.w	-2(a5),d0
	ext.l	d0
	asl.l	#5,d0
	lea	_G_h01_A15E,a0
	add.l	a0,d0
	move.l	d0,-6(a5)
	move.l	-6(a5),a0
	move.w	6(a0),d0
	ext.l	d0
	bra	.8
.10
	move.l	-6(a5),a0
	move.w	#4,14(a0)
	move.l	-6(a5),a0
	move.w	#32,10(a0)
	move.l	-6(a5),a0
	move.w	#80,8(a0)
	bra	.9
.11
	move.l	-6(a5),a0
	move.w	#3,14(a0)
	move.l	-6(a5),a0
	cmp.w	#20,10(a0)
	move.l	-6(a5),a0
	move.w	#80,8(a0)
	bra	.9
.12
	move.w	#4555,-(sp)
	jsr	_F_h00_3674
	add.w	#2,sp
	bra	.9
.8
	sub.l	#17,d0
	beq	.11
	sub.l	#1,d0
	beq	.10
	bra	.12
.9
	move.l	-6(a5),a0
	move.l	-6(a5),a1
	move.w	10(a1),d0
	ext.l	d0
	divs.w	#4,d0
	move.w	#154,d1
	sub.w	d0,d1
	sub.w	#1,d1
	move.w	d1,2(a0)
	move.l	-6(a5),a0
	move.l	-6(a5),a1
	move.w	2(a0),24(a1)
	move.l	-6(a5),a0
	move.l	-6(a5),a1
	move.w	24(a0),26(a1)
	jsr	_F_h00_463E
	swap	d0
	clr.w	d0
	swap	d0
	divu.w	#10,d0
	swap	d0
	cmp.w	#5,d0
	bcc	.13
	move.l	-6(a5),a0
	clr.w	12(a0)
	move.l	-6(a5),a0
	move.w	#3,16(a0)
	bra	.14
.13
	move.l	-6(a5),a0
	move.l	-6(a5),a1
	move.w	14(a1),d0
	sub.w	#1,d0
	move.w	d0,12(a0)
	move.l	-6(a5),a0
	move.w	#2,16(a0)
.14
	move.w	#6,-(sp)
	move.w	-2(a5),-(sp)
	jsr	_F_h11_40E0
	add.w	#4,sp
.4
	add.w	#1,-2(a5)
.7
	move.w	-2(a5),d0
	cmp.w	_G_h01_A152,d0
	blt	.6
.5
	move.w	#2,_G_h01_A15A
	jsr	_F_h00_463E
	swap	d0
	clr.w	d0
	swap	d0
	divu.w	_G_h01_A152,d0
	swap	d0
	move.w	d0,_G_h01_A158
	move.b	_G_h01_46E0,d0
	ext.w	d0
	ext.l	d0
	bra	.15
.17
	move.w	#1,_G_h01_A150
	bra	.16
.18
	move.w	#2,_G_h01_A150
	bra	.16
.19
	move.w	#3,_G_h01_A150
	bra	.16
.15
	tst.l	d0
	beq	.17
	sub.l	#1,d0
	beq	.18
	sub.l	#1,d0
	beq	.19
.16
.20
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-6
.3	reg	
	public	_F_h11_40E0
	public	_F_h00_3674
	public	_F_h00_463E
	public	.begin
	dseg
	public	_G_h01_46E0
	public	_G_h01_A15A
	public	_G_h01_A158
	public	_G_h01_A150
	public	_G_h01_A152
	public	_G_h01_A15E
	end
