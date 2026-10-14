;:ts=8
	public	_recovered
_recovered:
	link	a5,#.2
	movem.l	.3,-(sp)
	clr.w	-30(a5)
	move.w	#33,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
	clr.b	-1(a5)
	clr.b	-6(a5)
	clr.l	-28(a5)
	move.l	-28(a5),-(sp)
	move.w	#40,-(sp)
	jsr	_F_h00_291E
	add.w	#6,sp
	move.l	d0,-28(a5)
	clr.w	-(sp)
	move.w	#16,-(sp)
	pea	.1+0
	move.w	#24,-(sp)
	move.w	#64,-(sp)
	jsr	_F_h00_35DC
	lea	12(sp),sp
	clr.w	-(sp)
	move.w	#12,-(sp)
	pea	.1+25
	move.w	#32,-(sp)
	move.w	#40,-(sp)
	jsr	_F_h00_35DC
	lea	12(sp),sp
	clr.w	-(sp)
	move.w	#16,-(sp)
	pea	.1+57
	move.w	#40,-(sp)
	move.w	#80,-(sp)
	jsr	_F_h00_35DC
	lea	12(sp),sp
	clr.w	-(sp)
	move.w	#16,-(sp)
	pea	.1+79
	move.w	#48,-(sp)
	move.w	#72,-(sp)
	jsr	_F_h00_35DC
	lea	12(sp),sp
	clr.w	-(sp)
	move.w	#16,-(sp)
	pea	.1+101
	move.w	#56,-(sp)
	move.w	#64,-(sp)
	jsr	_F_h00_35DC
	lea	12(sp),sp
	clr.w	-16(a5)
.6
	jsr	_F_h00_463E
	swap	d0
	clr.w	d0
	swap	d0
	divu.w	#26,d0
	swap	d0
	move.w	d0,-12(a5)
	clr.w	-18(a5)
	bra	.10
.9
	move.w	-18(a5),d0
	lea	-5(a5),a0
	move.b	(a0,d0.w),d1
	ext.w	d1
	move.w	-12(a5),d0
	add.w	#65,d0
	cmp.w	d0,d1
	bne	.11
	bra	.8
.11
.7
	add.w	#1,-18(a5)
.10
	move.w	-18(a5),d0
	cmp.w	-16(a5),d0
	blt	.9
.8
	move.w	-18(a5),d0
	cmp.w	-16(a5),d0
	bge	.12
	sub.w	#1,-16(a5)
	bra	.13
.12
	move.w	-12(a5),d0
	add.w	#65,d0
	move.w	-16(a5),d1
	lea	-5(a5),a0
	move.b	d0,(a0,d1.w)
	clr.l	-(sp)
	pea	255
	pea	192
	pea	8
	pea	8
	pea	72
	move.w	-16(a5),d0
	asl.w	#3,d0
	add.w	#144,d0
	ext.l	d0
	move.l	d0,-(sp)
	move.l	_G_h01_46D2,-(sp)
	clr.l	-(sp)
	move.w	-12(a5),d0
	asl.w	#3,d0
	move.l	#0,d1
	move.w	d0,d1
	move.l	d1,-(sp)
	move.l	-28(a5),-(sp)
	jsr	_F_h00_8A46
	lea	44(sp),sp
.13
.4
	add.w	#1,-16(a5)
	cmp.w	#4,-16(a5)
	blt	.6
.5
	jsr	_F_h00_463E
	swap	d0
	clr.w	d0
	swap	d0
	divu.w	#10,d0
	swap	d0
	move.w	d0,-12(a5)
	clr.w	-16(a5)
.16
	move.w	-16(a5),d0
	cmp.w	-12(a5),d0
	bne	.17
	btst.b	#0,-15(a5)
	beq	.18
	move.w	#168,d0
	bra	.19
.18
	move.l	#120,d0
.19
	move.w	d0,-22(a5)
	cmp.w	#2,-16(a5)
	bge	.20
	move.w	#88,-24(a5)
	bra	.21
.20
	cmp.w	#4,-16(a5)
	bge	.22
	move.w	#96,-24(a5)
	bra	.23
.22
	cmp.w	#6,-16(a5)
	bge	.24
	move.w	#104,-24(a5)
	bra	.25
.24
	cmp.w	#8,-16(a5)
	bge	.26
	move.w	#112,-24(a5)
	bra	.27
.26
	move.w	#120,-24(a5)
.27
.25
.23
.21
	clr.w	-(sp)
	move.w	#1,-(sp)
	pea	-5(a5)
	move.w	-24(a5),-(sp)
	move.w	-22(a5),-(sp)
	jsr	_F_h00_35DC
	lea	12(sp),sp
	bra	.28
.17
	clr.w	-18(a5)
.31
	jsr	_F_h00_463E
	swap	d0
	clr.w	d0
	swap	d0
	divu.w	#26,d0
	swap	d0
	move.w	d0,-14(a5)
	clr.w	-20(a5)
	bra	.35
.34
	move.w	-20(a5),d0
	lea	-10(a5),a0
	move.b	(a0,d0.w),d1
	ext.w	d1
	move.w	-14(a5),d0
	add.w	#65,d0
	cmp.w	d0,d1
	bne	.36
	bra	.33
.36
.32
	add.w	#1,-20(a5)
.35
	move.w	-20(a5),d0
	cmp.w	-18(a5),d0
	blt	.34
.33
	move.w	-20(a5),d0
	cmp.w	-18(a5),d0
	bge	.37
	sub.w	#1,-18(a5)
	bra	.38
.37
	move.w	-14(a5),d0
	add.w	#65,d0
	move.w	-18(a5),d1
	lea	-10(a5),a0
	move.b	d0,(a0,d1.w)
.38
.29
	add.w	#1,-18(a5)
	cmp.w	#4,-18(a5)
	blt	.31
.30
	btst.b	#0,-15(a5)
	beq	.39
	move.w	#168,d0
	bra	.40
.39
	move.l	#120,d0
.40
	move.w	d0,-22(a5)
	cmp.w	#2,-16(a5)
	bge	.41
	move.w	#88,-24(a5)
	bra	.42
.41
	cmp.w	#4,-16(a5)
	bge	.43
	move.w	#96,-24(a5)
	bra	.44
.43
	cmp.w	#6,-16(a5)
	bge	.45
	move.w	#104,-24(a5)
	bra	.46
.45
	cmp.w	#8,-16(a5)
	bge	.47
	move.w	#112,-24(a5)
	bra	.48
.47
	move.w	#120,-24(a5)
.48
.46
.44
.42
	clr.w	-(sp)
	move.w	#1,-(sp)
	pea	-10(a5)
	move.w	-24(a5),-(sp)
	move.w	-22(a5),-(sp)
	jsr	_F_h00_35DC
	lea	12(sp),sp
.28
.14
	add.w	#1,-16(a5)
	cmp.w	#10,-16(a5)
	blt	.16
.15
	clr.w	-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
	clr.l	-(sp)
	pea	255
	pea	192
	pea	200
	pea	320
	clr.l	-(sp)
	clr.l	-(sp)
	move.l	_G_h01_46CE,-(sp)
	clr.l	-(sp)
	clr.l	-(sp)
	move.l	_G_h01_46D2,-(sp)
	jsr	_F_h00_8A46
	lea	44(sp),sp
	jsr	_F_h00_307C
	lea	_G_h01_14E6,a0
	move.l	a0,_G_h01_46D6
	pea	_G_h01_14E6
	jsr	_F_h00_31AA
	add.w	#4,sp
	move.w	#111,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
	clr.l	-(sp)
	pea	255
	pea	192
	pea	200
	pea	320
	clr.l	-(sp)
	clr.l	-(sp)
	move.l	_G_h01_46D2,-(sp)
	clr.l	-(sp)
	clr.l	-(sp)
	move.l	_G_h01_46CE,-(sp)
	jsr	_F_h00_8A46
	lea	44(sp),sp
	jsr	_F_h00_307C
	jsr	_F_h00_435E
	clr.w	-16(a5)
	move.w	-16(a5),-(sp)
	jsr	_F_h13_0746
	add.w	#2,sp
	clr.w	-18(a5)
.51
	clr.w	-18(a5)
	jsr	_F_h00_4376
	move.w	d0,-18(a5)
	cmp.w	#3,-18(a5)
	bne	.52
	add.w	#1,-16(a5)
	cmp.w	#9,-16(a5)
	ble	.53
	clr.w	-16(a5)
.53
	bra	.54
.52
	cmp.w	#7,-18(a5)
	bne	.55
	sub.w	#1,-16(a5)
	tst.w	-16(a5)
	bge	.56
	move.w	#9,-16(a5)
.56
	bra	.57
.55
	cmp.w	#5,-18(a5)
	bne	.58
	add.w	#2,-16(a5)
	cmp.w	#9,-16(a5)
	ble	.59
	clr.w	-16(a5)
.59
	bra	.60
.58
	cmp.w	#1,-18(a5)
	bne	.61
	sub.w	#2,-16(a5)
	tst.w	-16(a5)
	bge	.62
	move.w	#9,-16(a5)
.62
.61
.60
.57
.54
	tst.w	-18(a5)
	beq	.63
	move.w	-16(a5),-(sp)
	jsr	_F_h13_0746
	add.w	#2,sp
	pea	5
	jsr	_F_h00_86A8
	add.w	#4,sp
.63
	jsr	_F_h00_435E
	btst.b	#7,-17(a5)
	beq	.64
	move.w	-16(a5),d0
	cmp.w	-12(a5),d0
	beq	.65
.65
	bra	.66
	tst.w	-30(a5)
	bne	.67
	jsr	_F_h00_307C
	move.w	#14,-(sp)
	clr.w	-(sp)
	pea	.1+127
	move.w	#144,-(sp)
	move.w	#48,-(sp)
	jsr	_F_h00_35DC
	lea	12(sp),sp
	move.w	#70,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
	jsr	_F_h00_307C
	pea	25
	jsr	_F_h00_86A8
	add.w	#4,sp
	add.w	#1,-30(a5)
	bra	.68
.67
	cmp.w	#1,-30(a5)
	bne	.69
	clr.w	-(sp)
	clr.w	-(sp)
	pea	.1+156
	move.w	#144,-(sp)
	move.w	#48,-(sp)
	jsr	_F_h00_35DC
	lea	12(sp),sp
	clr.w	-20(a5)
.72
	jsr	_F_h00_307C
	move.w	#4,-(sp)
	move.w	#1,-(sp)
	pea	.1+185
	move.w	#144,-(sp)
	move.w	#96,-(sp)
	jsr	_F_h00_35DC
	lea	12(sp),sp
	move.w	#70,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
	jsr	_F_h00_307C
	pea	25
	jsr	_F_h00_86A8
	add.w	#4,sp
	jsr	_F_h00_307C
	clr.w	-(sp)
	clr.w	-(sp)
	pea	.1+202
	move.w	#144,-(sp)
	move.w	#96,-(sp)
	jsr	_F_h00_35DC
	lea	12(sp),sp
	jsr	_F_h00_307C
	pea	25
	jsr	_F_h00_86A8
	add.w	#4,sp
.70
	add.w	#1,-20(a5)
	cmp.w	#3,-20(a5)
	blt	.72
.71
	add.w	#1,-30(a5)
	bra	.50
.69
	bra	.50
.68
	bra	.73
.66
	bra	.50
.73
.64
	pea	1
	jsr	_F_h00_86A8
	add.w	#4,sp
.49
	bra	.51
.50
	move.l	-28(a5),-(sp)
	jsr	_F_h00_3B84
	add.w	#4,sp
	jsr	_F_h00_330E
	move.w	#33,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
	jsr	_F_h00_435E
	move.w	-16(a5),d0
	cmp.w	-12(a5),d0
	beq	.74
	move.l	#1,d0
.75
	movem.l	(sp)+,.3
	unlk	a5
	rts
.74
	move.l	#1,d0
	bra	.75
.2	equ	-30
.3	reg	
.1
	dc.b	84,104,105,115,32,105,115,32,71,121,114,111,32,71,101
	dc.b	97,114,108,111,111,115,101,39,115,0,83,85,80,69,82
	dc.b	32,65,78,84,73,45,83,80,89,32,83,69,67,85,82
	dc.b	73,84,89,32,83,89,83,84,69,77,46,0,68,101,99
	dc.b	111,100,101,32,116,104,101,32,102,111,108,108,111,119,105
	dc.b	110,103,32,0,109,101,115,115,97,103,101,32,116,111,32
	dc.b	112,114,111,118,101,32,116,104,97,116,0,121,111,117,32
	dc.b	97,114,101,32,110,111,116,32,97,32,66,101,97,103,108
	dc.b	101,32,66,111,121,46,0,80,111,115,115,105,98,108,101
	dc.b	32,66,101,97,103,108,101,32,66,111,121,32,66,114,101
	dc.b	97,107,45,73,110,0,32,32,32,32,32,32,32,32,32
	dc.b	32,32,32,32,32,32,32,32,32,32,32,32,32,32,32
	dc.b	32,32,32,32,0,66,69,65,71,76,69,32,66,79,89
	dc.b	32,65,76,69,82,84,0,32,32,32,32,32,32,32,32
	dc.b	32,32,32,32,32,32,32,32,0
	ds	0
	public	_F_h13_0746
	public	_F_h00_330E
	public	_F_h00_3B84
	public	_F_h00_86A8
	public	_F_h00_4376
	public	_F_h00_435E
	public	_F_h00_31AA
	public	_F_h00_307C
	public	_F_h00_8A46
	public	_F_h00_463E
	public	_F_h00_35DC
	public	_F_h00_291E
	public	_F_h00_57D2
	public	.begin
	dseg
	public	_G_h01_14E6
	public	_G_h01_46D6
	public	_G_h01_46D2
	public	_G_h01_46CE
	end
