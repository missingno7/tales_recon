;:ts=8
	public	_F_h11_2272
_F_h11_2272:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	_G_h01_9FCC,d0
	ext.l	d0
	bra	.4
.6
	move.w	_G_h01_94B8,d0
	cmp.w	_G_h01_9F4C,d0
	ble	.7
	move.w	#1,_G_h01_9FCC
	move.w	_G_h01_8A3E,d0
	add.w	#318,d0
	move.w	d0,_G_h01_9FC0
	move.w	_G_h01_94C0,d0
	add.w	#12,d0
	move.w	d0,_G_h01_9FC2
	move.w	_G_h01_9FC0,_G_h01_9FC4
	move.w	_G_h01_9FC2,_G_h01_9FC6
	move.w	_G_h01_9FC4,_G_h01_9FC8
	move.w	_G_h01_9FC6,_G_h01_9FCA
	move.w	#12,-(sp)
	jsr	_F_h11_2430
	add.w	#2,sp
	move.w	_G_h01_9FC2,-(sp)
	move.w	_G_h01_9FC0,-(sp)
	move.w	_G_h01_9FCC,-(sp)
	pea	_G_h01_9FAA
	move.w	#33,-(sp)
	jsr	_F_h11_41F6
	lea	12(sp),sp
.7
	bra	.5
.8
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	move.w	d0,-2(a5)
	move.w	_G_h01_94C0,d0
	add.w	#16,d0
	move.w	d0,-4(a5)
	move.w	_G_h01_94AE,d0
	ext.l	d0
	bra	.9
.11
	add.w	#8,-4(a5)
	bra	.10
.12
	add.w	#16,-2(a5)
	add.w	#8,-4(a5)
	bra	.10
.9
	sub.l	#6,d0
	beq	.12
	sub.l	#13,d0
	beq	.11
.10
	move.w	_G_h01_9FC2,d0
	add.w	#20,d0
	move.w	d0,-(sp)
	move.w	_G_h01_9FC0,d0
	add.w	#18,d0
	move.w	d0,-(sp)
	move.w	_G_h01_9FC2,d0
	add.w	#8,d0
	move.w	d0,-(sp)
	move.w	_G_h01_9FC0,d0
	add.w	#8,d0
	move.w	d0,-(sp)
	move.w	-4(a5),d0
	add.w	#6,d0
	move.w	d0,-(sp)
	move.w	-2(a5),d0
	add.w	#4,d0
	move.w	d0,-(sp)
	move.w	-4(a5),d0
	sub.w	#6,d0
	move.w	d0,-(sp)
	move.w	-2(a5),d0
	sub.w	#4,d0
	move.w	d0,-(sp)
	jsr	_F_h11_262E
	lea	16(sp),sp
	tst.w	d0
	beq	.13
	cmp.w	#2,_G_h01_94AE
	beq	.13
	cmp.w	#45,_G_h01_94AE
	beq	.13
	tst.w	_G_h01_94B6
	beq	.14
	move.w	_G_h01_94D4,-(sp)
	jsr	_F_h11_407C
	add.w	#2,sp
	clr.w	_G_h01_94B6
.14
	move.w	#2,_G_h01_94AE
	move.w	#2,-(sp)
	jsr	_F_h11_4B0C
	add.w	#2,sp
.13
	move.w	_G_h01_9FC0,d0
	add.w	#32,d0
	cmp.w	_G_h01_8A3E,d0
	bge	.15
	clr.w	_G_h01_9FCC
	clr.w	_G_h01_94B8
	bra	.16
.15
	sub.w	#4,_G_h01_9FC0
	pea	_G_h01_9FAA
	move.w	#33,-(sp)
	jsr	_F_h11_4474
	add.w	#6,sp
.16
	move.w	#12,-(sp)
	jsr	_F_h11_2430
	add.w	#2,sp
	bra	.5
.4
	tst.l	d0
	beq	.6
	sub.l	#1,d0
	beq	.8
.5
.17
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	
	public	_F_h11_23F4
_F_h11_23F4:
	link	a5,#.18
	movem.l	.19,-(sp)
	tst.w	_G_h01_9FCC
	beq	.20
	move.w	_G_h01_9FC0,_G_h01_9FAA
	move.w	_G_h01_9FC2,_G_h01_9FAC
	pea	_G_h01_9FAA
	jsr	_F_h11_4610
	add.w	#4,sp
.20
	move.w	_G_h01_9FC4,_G_h01_9FC8
	move.w	_G_h01_9FC6,_G_h01_9FCA
	move.w	_G_h01_9FC0,_G_h01_9FC4
	move.w	_G_h01_9FC2,_G_h01_9FC6
.21
	movem.l	(sp)+,.19
	unlk	a5
	rts
.18	equ	0
.19	reg	
	public	_F_h11_2430
_F_h11_2430:
	link	a5,#.22
	movem.l	.23,-(sp)
	move.w	#2,_G_h01_9FB6
	cmp.w	#12,8(a5)
	bne	.24
	move.w	#33,-(sp)
	move.w	#32,-(sp)
	move.w	#40,-(sp)
	move.w	_G_h01_9FCA,-(sp)
	move.w	_G_h01_9FC8,-(sp)
	jsr	_F_h11_4696
	lea	10(sp),sp
.24
	move.w	#32,-(sp)
	move.w	#40,-(sp)
	move.w	_G_h01_9FCA,-(sp)
	move.w	_G_h01_9FC8,-(sp)
	move.w	#12,-(sp)
	jsr	_F_h11_247C
	lea	10(sp),sp
.25
	movem.l	(sp)+,.23
	unlk	a5
	rts
.22	equ	0
.23	reg	
	public	_F_h11_247C
_F_h11_247C:
	link	a5,#.26
	movem.l	.27,-(sp)
	tst.w	10(a5)
	bge	.28
	clr.w	10(a5)
.28
	move.w	10(a5),d0
	ext.l	d0
	divs.w	#104,d0
	muls.w	#14,d0
	lea	_G_h01_8A66,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.w	10(a5),d0
	add.w	14(a5),d0
	ext.l	d0
	divs.w	#104,d0
	muls.w	#14,d0
	lea	_G_h01_8A66,a0
	add.l	a0,d0
	move.l	d0,-8(a5)
	bra	.32
.31
	move.l	-4(a5),a0
	tst.w	(a0)
	beq	.33
	move.w	8(a5),-(sp)
	move.l	-4(a5),a0
	move.w	(a0),-(sp)
	jsr	_F_h11_5C42
	add.w	#4,sp
.33
	move.l	-4(a5),a0
	tst.w	2(a0)
	beq	.34
	move.w	8(a5),-(sp)
	move.l	-4(a5),a0
	move.w	2(a0),-(sp)
	jsr	_F_h11_54F8
	add.w	#4,sp
.34
	move.l	-4(a5),a0
	tst.w	10(a0)
	beq	.35
	move.w	8(a5),-(sp)
	move.l	-4(a5),a0
	move.w	10(a0),-(sp)
	jsr	_F_h11_2E26
	add.w	#4,sp
.35
	move.l	-4(a5),a0
	tst.w	8(a0)
	beq	.36
	move.w	8(a5),-(sp)
	move.l	-4(a5),a0
	move.w	8(a0),-(sp)
	jsr	_F_h11_66FE
	add.w	#4,sp
.36
	move.l	-4(a5),a0
	tst.w	12(a0)
	beq	.37
	move.w	8(a5),-(sp)
	move.l	-4(a5),a0
	move.w	12(a0),-(sp)
	jsr	_F_h11_717A
	add.w	#4,sp
.37
.29
	add.l	#14,-4(a5)
.32
	move.l	-4(a5),a0
	cmp.l	-8(a5),a0
	bls	.31
.30
.38
	movem.l	(sp)+,.27
	unlk	a5
	rts
.26	equ	-8
.27	reg	
	public	_F_h11_717A
	public	_F_h11_66FE
	public	_F_h11_2E26
	public	_F_h11_54F8
	public	_F_h11_5C42
	public	_F_h11_4696
	public	_F_h11_4610
	public	_F_h11_4B0C
	public	_F_h11_4474
	public	_F_h11_41F6
	public	_F_h11_407C
	public	_F_h11_262E
	public	.begin
	dseg
	public	_G_h01_8A66
	public	_G_h01_9FB6
	public	_G_h01_9FAC
	public	_G_h01_9FCC
	public	_G_h01_9FCA
	public	_G_h01_9FC8
	public	_G_h01_9FC6
	public	_G_h01_9FC4
	public	_G_h01_9FC2
	public	_G_h01_9FC0
	public	_G_h01_9FAA
	public	_G_h01_9F4C
	public	_G_h01_94D4
	public	_G_h01_94C0
	public	_G_h01_94BE
	public	_G_h01_94B8
	public	_G_h01_94B6
	public	_G_h01_94B0
	public	_G_h01_94AE
	public	_G_h01_8A3E
	end
