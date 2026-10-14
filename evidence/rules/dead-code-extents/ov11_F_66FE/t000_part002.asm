;:ts=8
	public	_F_h11_063A
_F_h11_063A:
	link	a5,#.2
	movem.l	.3,-(sp)
	clr.w	-6(a5)
	move.w	_G_h01_94AE,-8(a5)
	move.w	_G_h01_94B0,-10(a5)
	move.w	_G_h01_94D6,d0
	muls.w	#52,d0
	lea	_G_h01_8BEC,a0
	add.l	a0,d0
	move.l	d0,-14(a5)
	jsr	_F_h00_4376
	move.w	d0,-2(a5)
	move.w	-2(a5),_G_h01_7A90
	btst.b	#7,-1(a5)
	beq	.4
	bset.b	#7,-1(a5)
.4
	tst.w	_G_h01_34D8+14
	ble	.5
	sub.w	#1,_G_h01_34D8+14
.6
	movem.l	(sp)+,.3
	unlk	a5
	rts
.5
	cmp.w	#5,_G_h01_94AE
	bne	.7
	move.l	#0,d0
	move.w	-2(a5),d0
	bra	.8
.10
	move.w	#1,_G_h01_94AE
	tst.w	_G_h01_94B0
	bne	.11
	move.w	#1,_G_h01_94B0
.11
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	add.w	#20,d0
	move.w	d0,-(sp)
	move.w	_G_h01_94BA,-(sp)
	clr.w	-(sp)
	jsr	_F_h11_5A12
	add.w	#4,sp
	move.w	(sp)+,d1
	cmp.w	d0,d1
	ble	.12
	tst.w	_G_h01_94B4
	beq	.13
	move.l	-14(a5),a0
	move.w	2(a0),d0
	asl.w	#5,d0
	add.w	#16,d0
	move.w	d0,_G_h01_94C0
	move.w	_G_h01_94D6,-(sp)
	jsr	_F_h11_5EC0
	add.w	#2,sp
	bra	.14
.13
	tst.w	_G_h01_94B6
	bne	.15
	move.w	_G_h01_94BA,d0
	add.w	#1,d0
	ext.l	d0
	asl.l	#3,d0
	move.w	_G_h01_94BC,d1
	ext.l	d1
	asl.l	#1,d1
	add.l	d1,d0
	lea	_G_h01_8B1C,a0
	tst.w	(a0,d0.l)
	bne	.15
	pea	-4(a5)
	move.w	#3,-(sp)
	move.w	#1,-(sp)
	jsr	_F_h11_5AB0
	add.w	#8,sp
	tst.w	d0
	bne	.17
	cmp.w	#2,_G_h01_94BC
	bne	.16
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	add.w	#16,d0
	move.w	d0,-(sp)
	jsr	_F_h11_3F90
	add.w	#2,sp
	tst.w	d0
	ble	.16
.17
	move.w	#4,_G_h01_94AE
.16
.15
.14
.12
	bra	.9
.18
	move.w	_G_h01_94BE,d0
	sub.w	#16,d0
	tst.w	d0
	bgt	.19
	move.w	#5,_G_h01_94AE
	bra	.9
.19
	move.w	#1,_G_h01_94AE
	cmp.w	#1,_G_h01_94B0
	bne	.20
	clr.w	_G_h01_94B0
.20
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	sub.w	#18,d0
	move.w	d0,-(sp)
	move.w	_G_h01_94BA,-(sp)
	clr.w	-(sp)
	jsr	_F_h11_5A62
	add.w	#4,sp
	move.w	(sp)+,d1
	cmp.w	d0,d1
	bge	.21
	tst.w	_G_h01_94B4
	beq	.22
	move.w	_G_h01_94BA,d0
	add.w	#1,d0
	ext.l	d0
	asl.l	#3,d0
	move.l	-14(a5),a0
	move.w	2(a0),d1
	ext.l	d1
	asl.l	#1,d1
	add.l	d1,d0
	lea	_G_h01_8B1C,a0
	tst.w	(a0,d0.l)
	beq	.22
	move.l	-14(a5),a0
	move.w	2(a0),d0
	asl.w	#5,d0
	add.w	#16,d0
	move.w	d0,_G_h01_94C0
	move.w	_G_h01_94D6,-(sp)
	jsr	_F_h11_5EC0
	add.w	#2,sp
	bra	.23
.22
	tst.w	_G_h01_94B6
	bne	.24
	move.w	_G_h01_94BA,d0
	sub.w	#1,d0
	ext.l	d0
	asl.l	#3,d0
	move.w	_G_h01_94BC,d1
	ext.l	d1
	asl.l	#1,d1
	add.l	d1,d0
	lea	_G_h01_8B1C,a0
	tst.w	(a0,d0.l)
	bne	.24
	pea	-4(a5)
	move.w	#3,-(sp)
	clr.w	-(sp)
	jsr	_F_h11_5AB0
	add.w	#8,sp
	tst.w	d0
	bne	.26
	cmp.w	#2,_G_h01_94BC
	bne	.25
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	sub.w	#16,d0
	move.w	d0,-(sp)
	jsr	_F_h11_3F90
	add.w	#2,sp
	tst.w	d0
	ble	.25
.26
	move.w	#4,_G_h01_94AE
.25
.24
.23
.21
	bra	.9
.27
	move.w	#18,_G_h01_94AE
	bra	.9
.28
	tst.w	_G_h01_94B4
	beq	.29
	cmp.w	#1,_G_h01_94B0
	bne	.29
	move.w	#3,_G_h01_94AE
	bra	.30
.29
	pea	-4(a5)
	move.w	#2,-(sp)
	move.w	#2,-(sp)
	jsr	_F_h11_5AB0
	add.w	#8,sp
	tst.w	d0
	beq	.31
	tst.w	_G_h01_94B6
	beq	.32
	clr.w	_G_h01_94B6
	move.w	#130,_G_h01_94C0
	move.w	_G_h01_94C0,d0
	sub.w	#16,d0
	asr.w	#5,d0
	move.w	d0,_G_h01_94BC
	move.w	#12,_G_h01_94AE
	bra	.33
.32
	move.w	#20,_G_h01_94AE
.33
	bra	.34
.31
	move.w	_G_h01_94BA,d0
	ext.l	d0
	asl.l	#1,d0
	lea	_G_h01_945C,a0
	tst.w	(a0,d0.l)
	beq	.35
	tst.w	_G_h01_94B6
	beq	.36
	move.w	#19,_G_h01_94AE
	bra	.37
.36
	cmp.w	#1,_G_h01_94B0
	bne	.38
	move.w	_G_h01_94BA,d0
	add.w	#1,d0
	ext.l	d0
	asl.l	#1,d0
	lea	_G_h01_945C,a0
	tst.w	(a0,d0.l)
	beq	.38
	move.w	#17,_G_h01_94AE
	bra	.39
.38
	tst.w	_G_h01_94B0
	bne	.40
	move.w	_G_h01_94BA,d0
	sub.w	#1,d0
	ext.l	d0
	asl.l	#1,d0
	lea	_G_h01_945C,a0
	tst.w	(a0,d0.l)
	beq	.40
	move.w	#16,_G_h01_94AE
	bra	.41
.40
	move.w	#19,_G_h01_94AE
.41
.39
.37
	bra	.42
.35
	move.w	#19,_G_h01_94AE
.42
.34
.30
	bra	.9
.43
	tst.w	_G_h01_94B6
	beq	.44
	move.w	#10,_G_h01_94AE
	bra	.45
.44
	move.w	_G_h01_94C0,d0
	add.w	#14,d0
	asr.w	#5,d0
	cmp.w	#2,d0
	blt	.46
	tst.w	_G_h01_94B4
	beq	.47
	move.l	-14(a5),a0
	move.w	2(a0),d0
	asl.w	#5,d0
	add.w	#16,d0
	move.w	d0,_G_h01_94C0
	move.w	_G_h01_94D6,-(sp)
	jsr	_F_h11_5EC0
	add.w	#2,sp
.47
	move.w	#13,_G_h01_94AE
	bra	.48
.46
	move.w	#21,_G_h01_94AE
.48
.45
	bra	.9
.49
	add.w	#1,_G_h01_94B8
	bra	.9
.50
.8
	sub.l	#1,d0
	beq	.28
	sub.l	#2,d0
	beq	.10
	sub.l	#2,d0
	beq	.43
	sub.l	#2,d0
	beq	.18
	sub.l	#121,d0
	beq	.27
	bra	.49
.9
	bra	.52
.7
	cmp.w	#8,_G_h01_94AE
	bne	.53
	move.w	#2,_G_h01_34D8+14
	move.l	#0,d0
	move.w	-2(a5),d0
	bra	.54
.56
	add.w	#1,_G_h01_94BC
	move.w	_G_h01_94BC,d0
	asl.w	#5,d0
	add.w	#16,d0
	move.w	d0,_G_h01_94C0
	clr.w	_G_h01_94D8
	move.w	_G_h01_94C0,d0
	add.w	#16,d0
	cmp.w	#112,d0
	ble	.57
	move.w	#2,_G_h01_94AE
	bra	.58
.57
	move.w	#5,_G_h01_94AE
.58
	bra	.55
.59
	move.w	#256,-(sp)
	move.w	_G_h01_94C0,d0
	add.w	#16,d0
	move.w	d0,-(sp)
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	move.w	d0,-(sp)
	move.w	_G_h01_94D8,d0
	add.w	#1,d0
	move.w	d0,-(sp)
	jsr	_F_h11_6F78
	add.w	#8,sp
	tst.w	d0
	beq	.60
	add.w	#1,_G_h01_94D8
	move.w	#1,-6(a5)
	bra	.61
.60
	add.w	#1,_G_h01_94BC
	move.w	_G_h01_94BC,d0
	asl.w	#5,d0
	add.w	#16,d0
	move.w	d0,_G_h01_94C0
	move.w	_G_h01_94C0,d0
	add.w	#16,d0
	cmp.w	#112,d0
	ble	.62
	move.w	#2,_G_h01_94AE
	bra	.63
.62
	move.w	#5,_G_h01_94AE
.63
	clr.w	_G_h01_94D8
.61
	bra	.55
.64
	move.w	#256,-(sp)
	move.w	_G_h01_94C0,d0
	add.w	#16,d0
	move.w	d0,-(sp)
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	move.w	d0,-(sp)
	move.w	_G_h01_94D8,d0
	sub.w	#1,d0
	move.w	d0,-(sp)
	jsr	_F_h11_6F78
	add.w	#8,sp
	tst.w	d0
	beq	.65
	sub.w	#1,_G_h01_94D8
	move.w	#1,-6(a5)
	bra	.66
.65
	add.w	#1,_G_h01_94BC
	move.w	_G_h01_94BC,d0
	asl.w	#5,d0
	add.w	#16,d0
	move.w	d0,_G_h01_94C0
	clr.w	_G_h01_94D8
	move.w	_G_h01_94C0,d0
	add.w	#16,d0
	cmp.w	#112,d0
	ble	.67
	move.w	#2,_G_h01_94AE
	bra	.68
.67
	move.w	#5,_G_h01_94AE
.68
.66
	bra	.55
.69
	clr.w	_G_h01_34D8+14
	bra	.55
.54
	sub.l	#3,d0
	beq	.59
	sub.l	#2,d0
	beq	.56
	sub.l	#2,d0
	beq	.64
	bra	.69
.55
.53
.52
	tst.w	-6(a5)
	bne	.70
	move.w	_G_h01_94AE,d0
	cmp.w	-8(a5),d0
	bne	.71
	move.w	_G_h01_94B0,d0
	cmp.w	-10(a5),d0
	beq	.70
.71
	move.w	_G_h01_94AE,-(sp)
	jsr	_F_h11_4B0C
	add.w	#2,sp
.70
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	ext.l	d0
	divs.w	#53,d0
	move.w	d0,_G_h01_94BA
	move.w	_G_h01_94C0,d0
	sub.w	#16,d0
	asr.w	#5,d0
	move.w	d0,_G_h01_94BC
	jsr	_F_h00_435E
	bra	.6
.2	equ	-14
.3	reg	
	public	_F_h11_6F78
	public	_F_h11_3F90
	public	_F_h11_5EC0
	public	_F_h11_5AB0
	public	_F_h11_5A62
	public	_F_h11_5A12
	public	_F_h11_4B0C
	public	_F_h00_4376
	public	_F_h00_435E
	public	.begin
	dseg
	public	_G_h01_34D8
	public	_G_h01_7A90
	public	_G_h01_94D8
	public	_G_h01_94D6
	public	_G_h01_94C0
	public	_G_h01_94BE
	public	_G_h01_94BC
	public	_G_h01_94BA
	public	_G_h01_94B8
	public	_G_h01_94B6
	public	_G_h01_94B4
	public	_G_h01_94B0
	public	_G_h01_94AE
	public	_G_h01_945C
	public	_G_h01_8BEC
	public	_G_h01_8B1C
	end
