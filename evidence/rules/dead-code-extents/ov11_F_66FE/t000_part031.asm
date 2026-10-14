;:ts=8
	public	_F_h11_3D9A
_F_h11_3D9A:
	link	a5,#.2
	movem.l	.3,-(sp)
	tst.w	_G_h01_8A42
	beq	.4
	move.w	#3,_G_h01_A15A
	bra	.5
.4
	tst.w	_G_h01_A15A
	bgt	.6
	move.w	#2,_G_h01_A15A
.6
.5
	sub.w	#1,_G_h01_A15A
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
	clr.w	-10(a5)
.9
	move.w	-4(a5),d0
	add.w	-10(a5),d0
	ext.l	d0
	divs.w	_G_h01_A152,d0
	swap	d0
	ext.l	d0
	asl.l	#5,d0
	lea	_G_h01_A15E,a0
	add.l	a0,d0
	move.l	d0,-8(a5)
	move.w	-4(a5),d0
	add.w	-10(a5),d0
	ext.l	d0
	divs.w	_G_h01_A152,d0
	swap	d0
	move.w	d0,-12(a5)
	tst.w	_G_h01_A15A
	bne	.10
	move.l	-8(a5),a0
	tst.w	4(a0)
	beq	.11
	move.l	-8(a5),a0
	move.l	-8(a5),a1
	move.w	20(a0),d0
	add.w	8(a1),d0
	cmp.w	#1168,d0
	ble	.11
	move.l	-8(a5),a0
	move.l	-8(a5),a1
	move.w	12(a0),d0
	cmp.w	14(a1),d0
	bge	.12
	move.l	-8(a5),a0
	add.w	#1,12(a0)
.12
	bra	.13
.11
	move.l	-8(a5),a0
	cmp.w	#1,4(a0)
	bne	.14
	jsr	_F_h00_463E
	and.w	#15,d0
	move.l	-8(a5),a0
	cmp.w	18(a0),d0
	bcc	.14
	move.l	-8(a5),a0
	cmp.w	#2,16(a0)
	bne	.15
	move.l	-8(a5),a0
	tst.w	12(a0)
	bgt	.16
	jsr	_F_h00_463E
	and.w	#15,d0
	cmp.w	_G_h01_A150,d0
	bcc	.16
	move.l	-8(a5),a0
	move.w	#3,16(a0)
	bra	.17
.16
	move.l	-8(a5),a0
	tst.w	12(a0)
	ble	.18
	move.l	-8(a5),a0
	sub.w	#1,12(a0)
.18
.17
	bra	.19
.15
	move.l	-8(a5),a0
	cmp.w	#3,16(a0)
	bne	.20
	move.l	-8(a5),a0
	move.l	-8(a5),a1
	move.w	12(a0),d0
	cmp.w	14(a1),d0
	blt	.21
	jsr	_F_h00_463E
	and.w	#15,d0
	cmp.w	_G_h01_A150,d0
	bcc	.21
	move.l	-8(a5),a0
	move.w	#2,16(a0)
	bra	.22
.21
	move.l	-8(a5),a0
	move.l	-8(a5),a1
	move.w	12(a0),d0
	cmp.w	14(a1),d0
	bge	.23
	move.l	-8(a5),a0
	add.w	#1,12(a0)
.23
.22
.20
.19
.14
.13
	move.w	#6,-(sp)
	move.w	-12(a5),-(sp)
	jsr	_F_h11_40E0
	add.w	#4,sp
.10
	move.w	_G_h01_94C0,d0
	add.w	#16,d0
	asr.w	#5,d0
	cmp.w	#3,d0
	blt	.24
	move.w	#10,-(sp)
	move.w	-12(a5),-(sp)
	jsr	_F_h11_40E0
	add.w	#4,sp
	bra	.25
.24
	tst.w	_G_h01_8A3C
	beq	.26
	move.w	#6,-(sp)
	move.w	-12(a5),-(sp)
	jsr	_F_h11_40E0
	add.w	#4,sp
.26
.25
.7
	add.w	#1,-10(a5)
	cmp.w	#5,-10(a5)
	blt	.9
.8
	tst.w	_G_h01_A15A
	bne	.27
	add.w	#4,_G_h01_A154
	cmp.w	#128,_G_h01_A154
	blt	.28
	clr.w	_G_h01_A154
	sub.w	#1,_G_h01_A158
	tst.w	_G_h01_A158
	bge	.29
	move.w	_G_h01_A152,d0
	sub.w	#1,d0
	move.w	d0,_G_h01_A158
.29
.28
.27
.30
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-12
.3	reg	
	public	_F_h11_40E0
	public	_F_h00_463E
	public	.begin
	dseg
	public	_G_h01_A15A
	public	_G_h01_A158
	public	_G_h01_A154
	public	_G_h01_A152
	public	_G_h01_A150
	public	_G_h01_94C0
	public	_G_h01_8A42
	public	_G_h01_8A3E
	public	_G_h01_8A3C
	public	_G_h01_A15E
	end
