;:ts=8
	public	_F_h11_6582
_F_h11_6582:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	muls.w	#40,d0
	lea	_G_h01_A464,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	clr.w	-6(a5)
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	move.w	d0,-8(a5)
	move.w	_G_h01_94C0,d0
	add.w	#16,d0
	move.w	d0,-10(a5)
	cmp.w	#19,_G_h01_94AE
	bne	.4
	add.w	#8,-10(a5)
	bra	.5
.4
	cmp.w	#18,_G_h01_94AE
	bne	.6
	sub.w	#16,-8(a5)
.6
.5
	move.l	-4(a5),a0
	cmp.w	#45,32(a0)
	beq	.7
	cmp.w	#2,_G_h01_94AE
	beq	.7
	cmp.w	#6,_G_h01_94AE
	beq	.7
	cmp.w	#7,_G_h01_94AE
	beq	.7
	move.l	-4(a5),a0
	move.w	36(a0),d0
	add.w	#56,d0
	move.w	d0,-(sp)
	move.l	-4(a5),a0
	move.w	34(a0),d0
	add.w	#48,d0
	move.w	d0,-(sp)
	move.w	-10(a5),-(sp)
	move.w	-8(a5),-(sp)
	move.l	-4(a5),a0
	move.w	36(a0),-(sp)
	move.l	-4(a5),a0
	move.w	34(a0),d0
	add.w	#16,d0
	move.w	d0,-(sp)
	jsr	_F_h11_25F8
	lea	12(sp),sp
	tst.w	d0
	beq	.8
	tst.w	_G_h01_94B6
	beq	.9
	clr.w	_G_h01_94B6
	clr.w	_G_h01_94D4
.9
	move.w	#45,_G_h01_94AE
	move.w	_G_h01_94AE,-(sp)
	jsr	_F_h11_4B0C
	add.w	#2,sp
	move.l	-4(a5),a0
	move.w	#45,32(a0)
	move.l	-4(a5),a0
	move.w	36(a0),-(sp)
	move.l	-4(a5),a0
	move.w	34(a0),-(sp)
	move.w	#45,-(sp)
	move.l	-4(a5),a0
	pea	10(a0)
	move.w	#8,-(sp)
	jsr	_F_h11_41F6
	lea	12(sp),sp
	move.w	#98,-(sp)
	jsr	_F_h00_57D2
	add.w	#2,sp
	move.w	#3,_G_h01_8A3C
	move.w	#1,-6(a5)
	bra	.10
.8
	move.l	-4(a5),a0
	move.w	(a0),d0
	cmp.w	_G_h01_94BA,d0
	bne	.11
	move.w	_G_h01_94C0,d0
	add.w	#14,d0
	asr.w	#5,d0
	move.l	-4(a5),a0
	cmp.w	2(a0),d0
	bne	.11
	cmp.w	#12,_G_h01_94AE
	beq	.12
	cmp.w	#1,_G_h01_94AE
	beq	.12
	cmp.w	#5,_G_h01_94AE
	bne	.11
.12
	move.w	#14,_G_h01_94AE
	move.w	#14,-(sp)
	jsr	_F_h11_4B0C
	add.w	#2,sp
.11
.10
.7
	move.w	-6(a5),d0
.13
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-10
.3	reg	
	public	_F_h00_57D2
	public	_F_h11_41F6
	public	_F_h11_4B0C
	public	_F_h11_25F8
	public	.begin
	dseg
	public	_G_h01_8A3C
	public	_G_h01_94D4
	public	_G_h01_94C0
	public	_G_h01_94BE
	public	_G_h01_94BA
	public	_G_h01_94B6
	public	_G_h01_94B0
	public	_G_h01_94AE
	public	_G_h01_A464
	end
