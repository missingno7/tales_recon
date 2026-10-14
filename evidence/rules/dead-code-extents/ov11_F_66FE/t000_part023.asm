;:ts=8
	public	_F_h11_2EEA
_F_h11_2EEA:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	ext.l	d0
	asl.l	#6,d0
	lea	_G_h01_9FCE,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	clr.w	-6(a5)
	clr.w	-8(a5)
	move.l	-4(a5),a0
	add.l	#2,a0
	move.l	a0,-(sp)
	jsr	_F_h11_45EC
	add.w	#4,sp
	move.w	d0,-10(a5)
	move.l	-4(a5),a0
	sub.w	#1,62(a0)
	move.w	#1,-6(a5)
	move.l	-4(a5),a0
	move.w	44(a0),d0
	ext.l	d0
	bra	.4
.6
	move.l	-4(a5),a0
	tst.w	62(a0)
	bne	.7
	move.l	-4(a5),a0
	move.w	30(a0),d0
	cmp.w	_G_h01_94BE,d0
	ble	.8
	move.l	-4(a5),a0
	tst.w	(a0)
	beq	.8
	jsr	_F_h00_463E
	ext.l	d0
	divs.w	#100,d0
	swap	d0
	cmp.w	#75,d0
	bge	.8
	move.l	-4(a5),a0
	move.w	#12,44(a0)
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
	bra	.9
.8
	move.l	-4(a5),a0
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	sub.w	#32,d0
	move.w	30(a0),d1
	cmp.w	d0,d1
	ble	.10
	jsr	_F_h00_463E
	ext.l	d0
	divs.w	#100,d0
	swap	d0
	cmp.w	#75,d0
	bge	.10
	move.l	-4(a5),a0
	move.w	#16,44(a0)
	move.l	-4(a5),a0
	move.w	#8,32(a0)
	move.l	-4(a5),a0
	move.w	_G_h01_94BE,d0
	sub.w	30(a0),d0
	add.w	#12,d0
	ext.l	d0
	divs.w	#64,d0
	swap	d0
	move.w	d0,_G_h01_34D8+18
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	34(a1),d0
	add.w	_G_h01_34D8+18,d0
	move.w	d0,30(a0)
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
.10
.9
.7
	bra	.5
.11
	move.l	-4(a5),a0
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	sub.w	#64,d0
	move.w	30(a0),d1
	cmp.w	d0,d1
	bge	.12
	move.l	-4(a5),a0
	move.w	#14,44(a0)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	34(a0),30(a1)
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
	bra	.13
.12
	move.l	-4(a5),a0
	tst.w	46(a0)
	bne	.14
	jsr	_F_h00_463E
	ext.l	d0
	divs.w	#100,d0
	swap	d0
	cmp.w	_G_h01_1300+30,d0
	bge	.14
	move.l	-4(a5),a0
	move.w	#17,44(a0)
	move.w	8(a5),_G_h01_7A92
	move.l	-4(a5),a0
	move.w	#1,46(a0)
	move.l	-4(a5),a0
	move.w	#3,48(a0)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	30(a1),d0
	add.w	#8,d0
	move.w	d0,54(a0)
	move.l	-4(a5),a0
	move.w	d0,56(a0)
	move.l	-4(a5),a0
	move.w	d0,50(a0)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	32(a1),d0
	add.w	#28,d0
	move.w	d0,58(a0)
	move.l	-4(a5),a0
	move.w	d0,60(a0)
	move.l	-4(a5),a0
	move.w	d0,52(a0)
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
.14
.13
	bra	.5
.15
	move.l	-4(a5),a0
	tst.w	62(a0)
	beq	.16
	bra	.17
.16
	tst.w	-10(a5)
	beq	.18
	move.l	-4(a5),a0
	move.w	#14,44(a0)
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
	bra	.19
.18
	move.l	-4(a5),a0
	cmp.w	#2,8(a0)
	bne	.20
	move.w	#96,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
.20
	move.l	-4(a5),a0
	add.l	#2,a0
	move.l	a0,-(sp)
	move.w	#2,-(sp)
	jsr	_F_h11_4474
	add.w	#6,sp
.19
.17
	bra	.5
.21
	move.l	-4(a5),a0
	tst.w	62(a0)
	beq	.22
	bra	.23
.22
	tst.w	-10(a5)
	beq	.24
	move.l	-4(a5),a0
	add.w	#12,32(a0)
	move.l	-4(a5),a0
	cmp.w	#80,32(a0)
	ble	.25
	move.l	-4(a5),a0
	move.w	#13,44(a0)
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
	bra	.26
.25
	move.l	-4(a5),a0
	move.w	32(a0),d0
	add.w	#28,d0
	move.w	_G_h01_94C0,d1
	add.w	#32,d1
	cmp.w	d1,d0
	bge	.27
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
	bra	.28
.27
	move.l	-4(a5),a0
	move.w	#13,44(a0)
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
.28
.26
	bra	.29
.24
	move.l	-4(a5),a0
	add.l	#2,a0
	move.l	a0,-(sp)
	move.w	#2,-(sp)
	jsr	_F_h11_4474
	add.w	#6,sp
.29
.23
	bra	.5
.30
	move.l	-4(a5),a0
	tst.w	62(a0)
	beq	.31
	bra	.32
.31
	tst.w	-10(a5)
	beq	.33
	move.l	-4(a5),a0
	sub.w	#12,32(a0)
	move.l	-4(a5),a0
	cmp.w	#16,32(a0)
	bge	.34
	move.l	-4(a5),a0
	move.w	#14,44(a0)
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
	bra	.35
.34
	move.l	-4(a5),a0
	move.w	32(a0),d0
	add.w	#32,d0
	move.w	_G_h01_94C0,d1
	add.w	#32,d1
	cmp.w	d1,d0
	bgt	.37
	move.l	-4(a5),a0
	move.w	30(a0),d0
	cmp.w	_G_h01_94BE,d0
	bge	.36
.37
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
	bra	.38
.36
	move.l	-4(a5),a0
	move.w	#13,44(a0)
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
.38
.35
	bra	.39
.33
	move.l	-4(a5),a0
	add.l	#2,a0
	move.l	a0,-(sp)
	move.w	#2,-(sp)
	jsr	_F_h11_4474
	add.w	#6,sp
.39
.32
	bra	.5
.40
	move.l	-4(a5),a0
	tst.w	62(a0)
	bgt	.41
	jsr	_F_h00_463E
	ext.l	d0
	divs.w	#100,d0
	swap	d0
	cmp.w	_G_h01_1300+26,d0
	bge	.42
	move.l	-4(a5),a0
	tst.w	46(a0)
	bne	.43
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	move.l	-4(a5),a0
	cmp.w	30(a0),d0
	bgt	.43
	move.l	-4(a5),a0
	move.w	#15,44(a0)
	move.w	#1,_G_h01_12C0+96
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
	move.w	8(a5),_G_h01_7A92
	clr.w	_G_h01_A14E
	move.l	-4(a5),a0
	move.w	#1,46(a0)
	move.l	-4(a5),a0
	clr.w	48(a0)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	30(a1),d0
	add.w	#44,d0
	move.w	d0,54(a0)
	move.l	-4(a5),a0
	move.w	d0,56(a0)
	move.l	-4(a5),a0
	move.w	d0,50(a0)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	32(a1),d0
	add.w	#22,d0
	move.w	d0,58(a0)
	move.l	-4(a5),a0
	move.w	d0,60(a0)
	move.l	-4(a5),a0
	move.w	d0,52(a0)
.43
	bra	.44
.42
	jsr	_F_h00_463E
	ext.l	d0
	divs.w	#100,d0
	swap	d0
	cmp.w	_G_h01_1300+28,d0
	bge	.45
	move.l	-4(a5),a0
	move.w	30(a0),d0
	add.w	#32,d0
	move.w	d0,-(sp)
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	move.w	d0,-(sp)
	move.l	-4(a5),a0
	move.w	30(a0),d0
	sub.w	#32,d0
	move.w	d0,-(sp)
	jsr	_F_h11_25D6
	add.w	#6,sp
	tst.w	d0
	bne	.47
	move.l	-4(a5),a0
	move.w	30(a0),d0
	cmp.w	_G_h01_94BE,d0
	bge	.46
.47
	move.l	-4(a5),a0
	move.w	#11,44(a0)
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
	bra	.48
.46
	move.l	-4(a5),a0
	move.w	32(a0),d0
	add.w	#20,d0
	cmp.w	_G_h01_94C0,d0
	bge	.49
	move.l	-4(a5),a0
	cmp.w	#80,32(a0)
	bge	.49
	move.l	-4(a5),a0
	move.w	#12,44(a0)
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
	bra	.50
.49
	move.l	-4(a5),a0
	move.w	32(a0),d0
	add.w	#20,d0
	move.w	_G_h01_94C0,d1
	add.w	#32,d1
	cmp.w	d1,d0
	ble	.51
	move.l	-4(a5),a0
	move.w	#11,44(a0)
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
.51
.50
.48
.45
.44
.41
	bra	.5
.52
	tst.w	-10(a5)
	beq	.53
	move.l	-4(a5),a0
	move.w	#13,44(a0)
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
	bra	.54
.53
	move.l	-4(a5),a0
	cmp.w	#1,8(a0)
	bne	.55
	tst.w	_G_h01_12C0+96
	beq	.55
	move.w	#96,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
	clr.w	_G_h01_12C0+96
	move.l	-4(a5),a0
	add.l	#2,a0
	move.l	a0,-(sp)
	move.w	#2,-(sp)
	jsr	_F_h11_4474
	add.w	#6,sp
	bra	.56
.55
	move.l	-4(a5),a0
	add.l	#2,a0
	move.l	a0,-(sp)
	move.w	#2,-(sp)
	jsr	_F_h11_4474
	add.w	#6,sp
.56
.54
	bra	.5
.57
	tst.w	-10(a5)
	beq	.58
	move.l	-4(a5),a0
	move.w	#13,44(a0)
	move.w	#1,-6(a5)
	move.w	#1,-8(a5)
	bra	.59
.58
	move.l	-4(a5),a0
	add.l	#2,a0
	move.l	a0,-(sp)
	move.w	#2,-(sp)
	jsr	_F_h11_4474
	add.w	#6,sp
.59
	bra	.5
.60
	dc.w	.30-.61-2
	dc.w	.21-.61-2
	dc.w	.40-.61-2
	dc.w	.6-.61-2
	dc.w	.52-.61-2
	dc.w	.11-.61-2
	dc.w	.15-.61-2
	dc.w	.57-.61-2
.4
	sub.l	#11,d0
	cmp.l	#8,d0
	bcc	.5
	asl.l	#1,d0
	move.w	.60(pc,d0.w),d0
.61
	jmp	(pc,d0.w)
.5
	tst.w	_G_h01_8A3C
	bne	.63
	tst.w	-6(a5)
	beq	.62
.63
	move.w	#7,-(sp)
	move.w	8(a5),-(sp)
	jsr	_F_h11_2E26
	add.w	#4,sp
.62
	tst.w	-8(a5)
	beq	.64
	move.l	-4(a5),a0
	move.w	32(a0),-(sp)
	move.l	-4(a5),a0
	move.w	30(a0),-(sp)
	move.l	-4(a5),a0
	move.w	44(a0),-(sp)
	move.l	-4(a5),a0
	add.l	#2,a0
	move.l	a0,-(sp)
	move.w	#2,-(sp)
	jsr	_F_h11_41F6
	lea	12(sp),sp
.64
	move.l	-4(a5),a0
	tst.w	62(a0)
	bgt	.65
	move.l	-4(a5),a0
	move.w	_G_h01_34D8+16,62(a0)
.65
.66
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-10
.3	reg	
	public	_F_h11_45EC
	public	_F_h11_4474
	public	_F_h11_41F6
	public	_F_h11_2E26
	public	_F_h11_25D6
	public	_F_h00_57D2
	public	_F_h00_463E
	public	.begin
	dseg
	public	_G_h01_A14E
	public	_G_h01_94C0
	public	_G_h01_94BE
	public	_G_h01_94B0
	public	_G_h01_8A3C
	public	_G_h01_7A92
	public	_G_h01_34D8
	public	_G_h01_12C0
	public	_G_h01_1300
	public	_G_h01_9FCE
	end
