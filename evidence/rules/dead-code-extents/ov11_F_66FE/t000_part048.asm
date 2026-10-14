;:ts=8
	public	_F_h11_4B0C
_F_h11_4B0C:
	link	a5,#.2
	movem.l	.3,-(sp)
	clr.w	_G_h01_94DE
	clr.w	_G_h01_94E4
	move.w	#1,_G_h01_94E6
	clr.l	_G_h01_94E8
	move.w	8(a5),d0
	ext.l	d0
	bra	.4
.6
	move.w	#7,_G_h01_94E0
	lea	_G_h01_9B4C,a0
	move.l	a0,_G_h01_94E8
	bra	.5
.7
	move.w	#7,_G_h01_94E0
	lea	_G_h01_9BBC,a0
	move.l	a0,_G_h01_94E8
	bra	.5
.8
	move.w	#88,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
	move.w	#142,_G_h01_94C0
	move.w	#5,_G_h01_94E0
	lea	_G_h01_9AFC,a0
	move.l	a0,_G_h01_94E8
	bra	.5
.9
	move.w	#3,_G_h01_94E0
	lea	_G_h01_9ABC,a0
	move.l	a0,_G_h01_94E8
	bra	.5
.10
	move.w	#5,_G_h01_94E0
	tst.w	_G_h01_94B0
	bne	.11
	lea	_G_h01_9A1C,a0
	move.l	a0,d0
	bra	.12
.11
	lea	_G_h01_9A6C,a0
	move.l	a0,d0
.12
	move.l	d0,_G_h01_94E8
	move.w	#100,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
	bra	.5
.13
	move.w	#2,_G_h01_94E0
	lea	_G_h01_99DC,a0
	move.l	a0,_G_h01_94E8
	bra	.5
.14
	move.w	#2,_G_h01_94E0
	lea	_G_h01_99FC,a0
	move.l	a0,_G_h01_94E8
	bra	.5
.15
	move.w	#1,_G_h01_94E0
	lea	_G_h01_9AEC,a0
	move.l	a0,_G_h01_94E8
	bra	.5
.16
	clr.w	_G_h01_94E0
	bra	.5
.17
	move.w	#7,_G_h01_94E0
	lea	_G_h01_978C,a0
	move.l	a0,_G_h01_94E8
	bra	.5
.18
	move.w	#7,_G_h01_94E0
	lea	_G_h01_97FC,a0
	move.l	a0,_G_h01_94E8
	bra	.5
.19
	move.w	#9,_G_h01_94E0
	cmp.w	#1,_G_h01_94B0
	bne	.20
	lea	_G_h01_98BC,a0
	move.l	a0,d0
	bra	.21
.20
	lea	_G_h01_994C,a0
	move.l	a0,d0
.21
	move.l	d0,_G_h01_94E8
	bra	.5
.22
	move.w	#3,_G_h01_94E0
	cmp.w	#1,_G_h01_94B0
	bne	.23
	lea	_G_h01_972C,a0
	move.l	a0,d0
	bra	.24
.23
	lea	_G_h01_975C,a0
	move.l	a0,d0
.24
	move.l	d0,_G_h01_94E8
	bra	.5
.25
	move.w	#8,_G_h01_94E0
	cmp.w	#1,_G_h01_94B0
	bne	.26
	lea	_G_h01_962C,a0
	move.l	a0,d0
	bra	.27
.26
	lea	_G_h01_96AC,a0
	move.l	a0,d0
.27
	move.l	d0,_G_h01_94E8
	bra	.5
.28
	clr.w	_G_h01_94E0
	cmp.w	#1,_G_h01_94B0
	bne	.29
	lea	_G_h01_986C,a0
	move.l	a0,d0
	bra	.30
.29
	lea	_G_h01_987C,a0
	move.l	a0,d0
.30
	move.l	d0,_G_h01_94E8
	bra	.5
.31
	tst.w	_G_h01_94B2
	beq	.32
	clr.w	_G_h01_94DE
	move.w	#5,_G_h01_94E0
	bra	.33
.32
	move.w	#5,_G_h01_94DE
	move.w	#10,_G_h01_94E0
.33
	cmp.w	#1,_G_h01_94B0
	bne	.34
	move.w	_G_h01_94DE,d0
	ext.l	d0
	asl.l	#4,d0
	lea	_G_h01_94EC,a0
	add.l	a0,d0
	move.l	d0,_G_h01_94E8
	bra	.35
.34
	move.w	_G_h01_94DE,d0
	ext.l	d0
	asl.l	#4,d0
	lea	_G_h01_958C,a0
	add.l	a0,d0
	move.l	d0,_G_h01_94E8
.35
	bra	.5
.36
	clr.w	_G_h01_94B6
	clr.w	_G_h01_94B4
	clr.w	_G_h01_94E0
	move.l	_G_h01_9F52,_G_h01_94DA
	cmp.w	#1,_G_h01_94B0
	bne	.37
	move.l	_G_h01_94DA,a0
	move.b	#1,52(a0)
	bra	.38
.37
	move.l	_G_h01_94DA,a0
	move.b	#3,52(a0)
.38
	move.w	#15,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
	bra	.5
.39
	move.w	#1,_G_h01_94E0
	move.l	_G_h01_9F4E,_G_h01_94DA
	pea	_G_h01_94C0
	pea	_G_h01_94BE
	pea	-4(a5)
	pea	-2(a5)
	move.w	_G_h01_94D8,-(sp)
	jsr	_F_h11_6ED6
	lea	18(sp),sp
	move.w	_G_h01_94BE,d0
	cmp.w	-2(a5),d0
	bge	.40
	cmp.w	#1,_G_h01_94B0
	bne	.41
	move.l	#28,d0
	bra	.42
.41
	move.l	#30,d0
.42
	move.l	_G_h01_94DA,a0
	move.b	d0,52(a0)
	tst.w	_G_h01_94B0
	bne	.43
	sub.w	#12,_G_h01_94BE
	add.w	#8,_G_h01_94C0
	bra	.44
.43
	sub.w	#3,_G_h01_94BE
	add.w	#9,_G_h01_94C0
.44
	bra	.45
.40
	move.w	_G_h01_94BE,d0
	cmp.w	-2(a5),d0
	ble	.46
	cmp.w	#1,_G_h01_94B0
	bne	.47
	move.l	#29,d0
	bra	.48
.47
	move.l	#31,d0
.48
	move.l	_G_h01_94DA,a0
	move.b	d0,52(a0)
	tst.w	_G_h01_94B0
	bne	.49
	add.w	#0,_G_h01_94BE
	add.w	#10,_G_h01_94C0
	bra	.50
.49
	add.w	#10,_G_h01_94BE
	add.w	#17,_G_h01_94C0
.50
	bra	.51
.46
	cmp.w	#1,_G_h01_94B0
	bne	.52
	move.l	#23,d0
	bra	.53
.52
	move.l	#27,d0
.53
	move.l	_G_h01_94DA,a0
	move.b	d0,52(a0)
	tst.w	_G_h01_94B0
	bne	.54
	sub.w	#6,_G_h01_94BE
	add.w	#22,_G_h01_94C0
	bra	.55
.54
	add.w	#1,_G_h01_94BE
	add.w	#22,_G_h01_94C0
.55
.51
.45
	sub.w	#6,_G_h01_94BE
	sub.w	#21,_G_h01_94C0
	bra	.5
.56
.4
	sub.l	#1,d0
	beq	.31
	sub.l	#1,d0
	beq	.36
	sub.l	#1,d0
	beq	.19
	sub.l	#1,d0
	beq	.25
	sub.l	#1,d0
	beq	.28
	sub.l	#1,d0
	beq	.8
	sub.l	#2,d0
	beq	.39
	sub.l	#2,d0
	beq	.22
	sub.l	#2,d0
	beq	.17
	sub.l	#1,d0
	beq	.18
	sub.l	#1,d0
	beq	.15
	sub.l	#2,d0
	beq	.14
	sub.l	#1,d0
	beq	.13
	sub.l	#1,d0
	beq	.10
	sub.l	#1,d0
	beq	.9
	sub.l	#1,d0
	beq	.6
	sub.l	#1,d0
	beq	.7
	sub.l	#24,d0
	beq	.16
.5
	tst.l	_G_h01_94E8
	beq	.58
	move.l	_G_h01_94E8,a0
	move.l	(a0),_G_h01_94DA
	move.l	_G_h01_94E8,a0
	move.w	12(a0),d0
	add.w	d0,_G_h01_94BE
	move.l	_G_h01_94E8,a0
	move.w	14(a0),d0
	add.w	d0,_G_h01_94C0
	move.l	_G_h01_94E8,a0
	move.l	_G_h01_94DA,a1
	move.b	5(a0),52(a1)
	move.l	_G_h01_94E8,a0
	move.w	6(a0),_G_h01_94E4
.58
.59
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	
	public	_F_h11_6ED6
	public	_F_h00_57D2
	public	.begin
	dseg
	public	_G_h01_9BBC
	public	_G_h01_9B4C
	public	_G_h01_9AFC
	public	_G_h01_9AEC
	public	_G_h01_9ABC
	public	_G_h01_9A6C
	public	_G_h01_9A1C
	public	_G_h01_99FC
	public	_G_h01_99DC
	public	_G_h01_994C
	public	_G_h01_98BC
	public	_G_h01_987C
	public	_G_h01_986C
	public	_G_h01_97FC
	public	_G_h01_975C
	public	_G_h01_978C
	public	_G_h01_972C
	public	_G_h01_96AC
	public	_G_h01_962C
	public	_G_h01_958C
	public	_G_h01_94EC
	public	_G_h01_9F52
	public	_G_h01_9F4E
	public	_G_h01_94E8
	public	_G_h01_94E6
	public	_G_h01_94E4
	public	_G_h01_94E0
	public	_G_h01_94DE
	public	_G_h01_94DA
	public	_G_h01_94D8
	public	_G_h01_94C0
	public	_G_h01_94BE
	public	_G_h01_94B6
	public	_G_h01_94B4
	public	_G_h01_94B2
	public	_G_h01_94B0
	end
