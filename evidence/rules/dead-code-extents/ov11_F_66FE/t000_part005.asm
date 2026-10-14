;:ts=8
	public	_F_h11_0D8E
_F_h11_0D8E:
	link	a5,#.2
	movem.l	.3,-(sp)
	clr.w	-10(a5)
	move.w	_G_h01_94AE,-12(a5)
	move.w	_G_h01_94DE,d0
	add.w	#1,d0
	cmp.w	_G_h01_94E0,d0
	sge	d0
	and.w	#1,d0
	move.w	d0,-14(a5)
	move.w	_G_h01_94D6,d0
	muls.w	#52,d0
	lea	_G_h01_8BEC,a0
	add.l	a0,d0
	move.l	d0,-18(a5)
	tst.w	_G_h01_94E6
	ble	.4
.5
	movem.l	(sp)+,.3
	unlk	a5
	rts
.4
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
	move.w	_G_h01_94AE,d0
	ext.l	d0
	bra	.6
.8
	tst.w	-14(a5)
	beq	.9
	add.w	#8,_G_h01_94C0
	move.w	#5,_G_h01_94AE
.9
	bra	.7
.10
	tst.w	-14(a5)
	beq	.11
	move.w	#5,_G_h01_94AE
	tst.w	_G_h01_94B0
	bne	.12
	move.l	#14,d0
	bra	.13
.12
	move.l	#-14,d0
.13
	add.w	d0,_G_h01_94BE
.11
	bra	.7
.14
	tst.w	-14(a5)
	beq	.15
	move.w	_G_h01_94BA,d0
	ext.l	d0
	asl.l	#1,d0
	lea	_G_h01_945C,a0
	move.w	(a0,d0.l),-8(a5)
	beq	.16
	move.w	#324,-(sp)
	move.w	_G_h01_94C0,d0
	add.w	#24,d0
	move.w	d0,-(sp)
	move.w	_G_h01_94BE,d0
	add.w	#15,d0
	move.w	d0,-(sp)
	move.w	-8(a5),-(sp)
	jsr	_F_h11_6F78
	add.w	#8,sp
	tst.w	d0
	beq	.16
	move.w	-8(a5),_G_h01_94D8
	move.w	#8,_G_h01_94AE
	bra	.17
.16
	move.w	#2,_G_h01_94AE
.17
.15
	bra	.7
.18
	tst.w	-14(a5)
	beq	.19
	move.w	_G_h01_94BA,d0
	ext.l	d0
	asl.l	#1,d0
	lea	_G_h01_945C,a0
	move.w	(a0,d0.l),-8(a5)
	beq	.20
	move.w	#324,-(sp)
	move.w	_G_h01_94C0,d0
	add.w	#8,d0
	move.w	d0,-(sp)
	move.w	_G_h01_94BE,d0
	add.w	#4,d0
	move.w	d0,-(sp)
	move.w	-8(a5),-(sp)
	jsr	_F_h11_6F78
	add.w	#8,sp
	tst.w	d0
	beq	.20
	move.w	-8(a5),_G_h01_94D8
	move.w	#8,_G_h01_94AE
	bra	.21
.20
	move.w	#2,_G_h01_94AE
.21
.19
	bra	.7
.22
	tst.w	-14(a5)
	beq	.23
	move.w	#2,_G_h01_94AE
.23
	bra	.7
.24
	tst.w	-14(a5)
	beq	.25
	move.w	_G_h01_94C0,d0
	asr.w	#5,d0
	asl.w	#5,d0
	add.w	#16,d0
	move.w	d0,_G_h01_94C0
	move.w	#5,_G_h01_94AE
.25
	bra	.7
.26
	tst.w	-14(a5)
	beq	.27
	add.w	#7,_G_h01_94C0
	move.w	#5,_G_h01_94AE
.27
	bra	.7
.28
	tst.w	-14(a5)
	beq	.29
	add.w	#6,_G_h01_94C0
	move.w	#5,_G_h01_94AE
	bra	.30
.29
	cmp.w	#5,_G_h01_94DE
	bne	.31
	move.w	_G_h01_94BA,d0
	ext.l	d0
	asl.l	#3,d0
	move.w	_G_h01_94BC,d1
	add.w	#1,d1
	ext.l	d1
	asl.l	#1,d1
	add.l	d1,d0
	lea	_G_h01_8B1C,a0
	tst.w	(a0,d0.l)
	bne	.32
	move.w	#2,_G_h01_94AE
.32
.31
.30
	bra	.7
.33
	tst.w	-14(a5)
	beq	.34
	add.w	#5,_G_h01_94C0
	move.w	_G_h01_94BE,-(sp)
	jsr	_F_h11_3F90
	add.w	#2,sp
	move.w	d0,-6(a5)
	tst.w	d0
	blt	.35
	move.w	-6(a5),_G_h01_94D4
	move.w	_G_h01_94D4,-(sp)
	jsr	_F_h11_40AE
	add.w	#2,sp
	move.w	#1,_G_h01_94B6
	move.w	#5,_G_h01_94AE
	pea	_G_h01_94C0
	pea	_G_h01_94BE
	move.w	_G_h01_94D4,-(sp)
	jsr	_F_h11_415A
	lea	10(sp),sp
	pea	_G_h01_94C0
	pea	_G_h01_94BE
	move.w	_G_h01_94D4,-(sp)
	jsr	_F_h11_415A
	lea	10(sp),sp
	bra	.36
.35
	move.w	#2,_G_h01_94AE
.36
.34
	bra	.7
.37
	tst.w	-14(a5)
	beq	.38
	move.w	#5,_G_h01_94AE
.38
	bra	.7
.39
	cmp.w	#1,_G_h01_94DE
	bne	.40
	move.w	_G_h01_94D6,-(sp)
	jsr	_F_h11_5EC0
	add.w	#2,sp
	bra	.41
.40
	cmp.w	#6,_G_h01_94DE
	bne	.42
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
	move.w	(a0,d0.l),-8(a5)
	tst.w	-8(a5)
	beq	.44
	tst.w	_G_h01_94B4
	beq	.43
	move.w	-8(a5),d0
	cmp.w	_G_h01_94D6,d0
	bne	.43
.44
	move.w	#2,_G_h01_94AE
	bra	.7
.43
	bra	.45
.42
	tst.w	-14(a5)
	beq	.46
	move.w	_G_h01_94C0,d0
	add.w	#14,d0
	asr.w	#5,d0
	asl.w	#5,d0
	add.w	#16,d0
	move.w	d0,_G_h01_94C0
	move.w	#5,_G_h01_94AE
	move.w	#119,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
.46
.45
.41
	move.w	_G_h01_94BA,d0
	ext.l	d0
	asl.l	#1,d0
	lea	_G_h01_945C,a0
	move.w	(a0,d0.l),-8(a5)
	beq	.47
	move.w	#1024,-(sp)
	move.w	_G_h01_94C0,d0
	add.w	#16,d0
	move.w	d0,-(sp)
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	move.w	d0,-(sp)
	move.w	-8(a5),-(sp)
	jsr	_F_h11_6F78
	add.w	#8,sp
	tst.w	d0
	beq	.47
	move.w	-8(a5),_G_h01_94D8
	move.w	#8,_G_h01_94AE
.47
	bra	.7
.48
	cmp.w	#4,_G_h01_94DE
	bne	.49
	move.w	_G_h01_94C0,d0
	add.w	#14,d0
	asr.w	#5,d0
	cmp.w	#2,d0
	ble	.49
	add.w	#8,_G_h01_94C0
	bra	.50
.49
	tst.w	-14(a5)
	beq	.51
	cmp.w	#3,_G_h01_94BC
	blt	.52
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	move.w	d0,-(sp)
	jsr	_F_h11_3F90
	add.w	#2,sp
	move.w	d0,-6(a5)
	tst.w	d0
	blt	.53
	move.w	-6(a5),_G_h01_94D4
	move.w	_G_h01_94D4,-(sp)
	jsr	_F_h11_40AE
	add.w	#2,sp
	pea	_G_h01_94C0
	pea	_G_h01_94BE
	move.w	_G_h01_94D4,-(sp)
	jsr	_F_h11_415A
	lea	10(sp),sp
	pea	_G_h01_94C0
	pea	_G_h01_94BE
	move.w	_G_h01_94D4,-(sp)
	jsr	_F_h11_415A
	lea	10(sp),sp
	move.w	#1,_G_h01_94B6
	bra	.54
.53
	move.w	#6,_G_h01_94AE
.54
.52
	move.w	#5,_G_h01_94AE
	move.w	#119,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
.51
.50
	bra	.7
.55
	tst.w	-14(a5)
	beq	.56
	move.w	#10,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
	bchg.b	#0,_G_h01_94B3
	move.w	#5,_G_h01_94AE
.56
	bra	.7
.57
	move.w	_G_h01_94C0,d0
	add.w	#40,d0
	cmp.w	#154,d0
	blt	.58
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	move.w	d0,-(sp)
	jsr	_F_h11_3F90
	add.w	#2,sp
	move.w	d0,-6(a5)
	tst.w	d0
	blt	.59
	move.w	-6(a5),_G_h01_94D4
	move.w	_G_h01_94D4,-(sp)
	jsr	_F_h11_40AE
	add.w	#2,sp
	move.w	#1,_G_h01_94B6
	move.w	#5,_G_h01_94AE
	pea	_G_h01_94C0
	pea	_G_h01_94BE
	move.w	_G_h01_94D4,-(sp)
	jsr	_F_h11_415A
	lea	10(sp),sp
	pea	_G_h01_94C0
	pea	_G_h01_94BE
	move.w	_G_h01_94D4,-(sp)
	jsr	_F_h11_415A
	lea	10(sp),sp
	bra	.60
.59
	move.w	#6,_G_h01_94AE
.60
	bra	.61
.58
	add.w	#16,_G_h01_94C0
	move.w	#1,-10(a5)
.61
	bra	.7
.62
	pea	_G_h01_94C0
	pea	_G_h01_94BE
	pea	-4(a5)
	pea	-2(a5)
	move.w	_G_h01_94D8,-(sp)
	jsr	_F_h11_6ED6
	lea	18(sp),sp
	move.w	_G_h01_94BE,d0
	cmp.w	-2(a5),d0
	bge	.63
	cmp.w	#1,_G_h01_94B0
	bne	.64
	move.l	#28,d0
	bra	.65
.64
	move.l	#30,d0
.65
	move.l	_G_h01_94DA,a0
	move.b	d0,52(a0)
	tst.w	_G_h01_94B0
	bne	.66
	sub.w	#20,_G_h01_94BE
	sub.w	#13,_G_h01_94C0
	bra	.67
.66
	sub.w	#9,_G_h01_94BE
	sub.w	#12,_G_h01_94C0
.67
	bra	.68
.63
	move.w	_G_h01_94BE,d0
	cmp.w	-2(a5),d0
	ble	.69
	cmp.w	#1,_G_h01_94B0
	bne	.70
	move.l	#29,d0
	bra	.71
.70
	move.l	#31,d0
.71
	move.l	_G_h01_94DA,a0
	move.b	d0,52(a0)
	tst.w	_G_h01_94B0
	bne	.72
	sub.w	#6,_G_h01_94BE
	sub.w	#12,_G_h01_94C0
	bra	.73
.72
	add.w	#4,_G_h01_94BE
	sub.w	#10,_G_h01_94C0
.73
	bra	.74
.69
	cmp.w	#1,_G_h01_94B0
	bne	.75
	move.l	#23,d0
	bra	.76
.75
	move.l	#27,d0
.76
	move.l	_G_h01_94DA,a0
	move.b	d0,52(a0)
	tst.w	_G_h01_94B0
	bne	.77
	sub.w	#12,_G_h01_94BE
	sub.w	#1,_G_h01_94C0
	bra	.78
.77
	sub.w	#5,_G_h01_94BE
	add.w	#0,_G_h01_94C0
.78
.74
.68
	move.w	#1,-10(a5)
	bra	.7
.79
	tst.w	-14(a5)
	beq	.80
	move.w	#7,_G_h01_94AE
.80
	bra	.7
.81
	move.w	#1,-10(a5)
	bra	.7
.82
	dc.w	.81-.83-2
	dc.w	.55-.83-2
	dc.w	.57-.83-2
	dc.w	.39-.83-2
	dc.w	.48-.83-2
	dc.w	.81-.83-2
	dc.w	.79-.83-2
	dc.w	.81-.83-2
	dc.w	.62-.83-2
	dc.w	.81-.83-2
	dc.w	.37-.83-2
	dc.w	.81-.83-2
	dc.w	.24-.83-2
	dc.w	.33-.83-2
	dc.w	.22-.83-2
	dc.w	.81-.83-2
	dc.w	.18-.83-2
	dc.w	.14-.83-2
	dc.w	.10-.83-2
	dc.w	.8-.83-2
	dc.w	.26-.83-2
	dc.w	.28-.83-2
.6
	cmp.l	#22,d0
	bcc	.81
	asl.l	#1,d0
	move.w	.82(pc,d0.w),d0
.83
	jmp	(pc,d0.w)
.7
	tst.w	-10(a5)
	bne	.84
	move.w	-12(a5),d0
	cmp.w	_G_h01_94AE,d0
	beq	.85
	move.w	_G_h01_94AE,-(sp)
	jsr	_F_h11_4B0C
	add.w	#2,sp
	bra	.86
.85
	jsr	_F_h11_4AA4
.86
.84
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
	bra	.5
.2	equ	-18
.3	reg	
	public	_F_h11_6F78
	public	_F_h11_6ED6
	public	_F_h11_5EC0
	public	_F_h11_4B0C
	public	_F_h11_4AA4
	public	_F_h11_415A
	public	_F_h11_40AE
	public	_F_h11_3F90
	public	_F_h00_57D2
	public	.begin
	dseg
	public	_G_h01_8BEC
	public	_G_h01_8B1C
	public	_G_h01_945C
	public	_G_h01_94E6
	public	_G_h01_94E0
	public	_G_h01_94DE
	public	_G_h01_94DA
	public	_G_h01_94D8
	public	_G_h01_94D6
	public	_G_h01_94D4
	public	_G_h01_94C0
	public	_G_h01_94BE
	public	_G_h01_94BC
	public	_G_h01_94BA
	public	_G_h01_94B6
	public	_G_h01_94B4
	public	_G_h01_94B3
	public	_G_h01_94B0
	public	_G_h01_94AE
	end
