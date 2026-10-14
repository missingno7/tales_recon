;:ts=8
	public	_F_h11_3B92
_F_h11_3B92:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	_G_h01_8A3E,d0
	ext.l	d0
	divs.w	#128,d0
	move.w	d0,-2(a5)
	move.w	_G_h01_A158,d0
	add.w	-2(a5),d0
	ext.l	d0
	divs.w	_G_h01_A152,d0
	swap	d0
	move.w	d0,-4(a5)
	clr.w	-6(a5)
.6
	move.w	-4(a5),d0
	add.w	-6(a5),d0
	ext.l	d0
	divs.w	_G_h01_A152,d0
	swap	d0
	ext.l	d0
	asl.l	#5,d0
	lea	_G_h01_A15E,a0
	add.l	a0,d0
	move.l	d0,-14(a5)
	move.l	-14(a5),a0
	cmp.w	#1,4(a0)
	bne	.7
	move.w	-2(a5),d0
	add.w	-6(a5),d0
	sub.w	#1,d0
	asl.w	#7,d0
	add.w	_G_h01_A154,d0
	move.w	d0,-16(a5)
	move.l	-14(a5),a0
	move.w	2(a0),-18(a5)
	tst.w	_G_h01_7A92
	beq	.8
	pea	-10(a5)
	pea	-8(a5)
	move.w	_G_h01_7A92,-(sp)
	jsr	_F_h11_37A0
	lea	10(sp),sp
	tst.w	d0
	beq	.8
	move.l	-14(a5),a0
	move.w	10(a0),d0
	add.w	-18(a5),d0
	move.w	d0,-(sp)
	move.l	-14(a5),a0
	move.w	8(a0),d0
	add.w	-16(a5),d0
	move.w	d0,-(sp)
	move.w	-10(a5),-(sp)
	move.w	-8(a5),-(sp)
	move.l	-14(a5),a0
	move.w	-18(a5),d0
	sub.w	10(a0),d0
	move.w	d0,-(sp)
	move.w	-16(a5),-(sp)
	jsr	_F_h11_25F8
	lea	12(sp),sp
	tst.w	d0
	beq	.8
	move.w	#7,-(sp)
	move.w	-4(a5),d0
	add.w	-6(a5),d0
	ext.l	d0
	divs.w	_G_h01_A152,d0
	swap	d0
	move.w	d0,-(sp)
	jsr	_F_h11_40E0
	add.w	#4,sp
.8
	move.l	-14(a5),a0
	tst.w	28(a0)
	ble	.9
	move.l	-14(a5),a0
	move.l	-14(a5),a1
	move.w	12(a0),d0
	cmp.w	14(a1),d0
	bge	.9
	move.l	-14(a5),a0
	move.w	6(a0),d0
	ext.l	d0
	bra	.10
.12
	move.l	-14(a5),a0
	move.l	#0,d0
	move.b	13(a0),d0
	move.l	_G_h01_9F66,a0
	move.b	d0,52(a0)
	move.l	_G_h01_9F66,a0
	move.w	-16(a5),d0
	sub.w	_G_h01_8A3E,d0
	move.w	d0,(a0)
	move.l	_G_h01_9F66,a0
	move.w	-18(a5),2(a0)
	move.l	_G_h01_9F66,a0
	cmp.w	#320,(a0)
	bge	.13
	move.l	_G_h01_9F66,-(sp)
	jsr	_F_h00_34E0
	add.w	#4,sp
.13
	bra	.11
.14
	move.l	-14(a5),a0
	move.l	#0,d0
	move.b	13(a0),d0
	move.l	_G_h01_9F8A,a0
	move.b	d0,52(a0)
	move.l	_G_h01_9F8A,a0
	move.w	-16(a5),d0
	sub.w	_G_h01_8A3E,d0
	move.w	d0,(a0)
	move.l	_G_h01_9F8A,a0
	move.w	-18(a5),2(a0)
	move.l	_G_h01_9F8A,a0
	cmp.w	#320,(a0)
	bge	.15
	move.l	_G_h01_9F8A,-(sp)
	jsr	_F_h00_34E0
	add.w	#4,sp
.15
	bra	.11
.10
	sub.l	#17,d0
	beq	.14
	sub.l	#1,d0
	beq	.12
.11
	move.l	-14(a5),a0
	sub.w	#1,28(a0)
	move.l	-14(a5),a0
	tst.w	28(a0)
	bne	.16
	move.l	-14(a5),a0
	clr.w	30(a0)
.16
.9
	move.l	-14(a5),a0
	move.l	-14(a5),a1
	move.w	20(a0),22(a1)
	move.l	-14(a5),a0
	move.l	-14(a5),a1
	move.w	24(a0),26(a1)
	move.l	-14(a5),a0
	move.w	-16(a5),20(a0)
	move.l	-14(a5),a0
	move.w	-18(a5),24(a0)
.7
.4
	add.w	#1,-6(a5)
	cmp.w	#4,-6(a5)
	blt	.6
.5
.17
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-18
.3	reg	
	public	_F_h00_34E0
	public	_F_h11_40E0
	public	_F_h11_25F8
	public	_F_h11_37A0
	public	.begin
	dseg
	public	_G_h01_A158
	public	_G_h01_A154
	public	_G_h01_A152
	public	_G_h01_8A3E
	public	_G_h01_7A92
	public	_G_h01_9F8A
	public	_G_h01_9F66
	public	_G_h01_A15E
	end
