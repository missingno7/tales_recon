;:ts=8
	public	_F_h11_37E4
_F_h11_37E4:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	move.w	d0,-2(a5)
	move.w	_G_h01_94C0,d0
	add.w	#16,d0
	move.w	d0,-4(a5)
	move.w	8(a5),d0
	ext.l	d0
	asl.l	#6,d0
	lea	_G_h01_9FCE,a0
	add.l	a0,d0
	move.l	d0,-8(a5)
	clr.w	-10(a5)
	move.l	-8(a5),a0
	tst.w	46(a0)
	beq	.4
	move.l	-8(a5),a0
	move.w	52(a0),d0
	add.w	#12,d0
	move.w	d0,-(sp)
	move.l	-8(a5),a0
	move.w	50(a0),d0
	add.w	#8,d0
	move.w	d0,-(sp)
	move.l	-8(a5),a0
	move.w	52(a0),d0
	add.w	#2,d0
	move.w	d0,-(sp)
	move.l	-8(a5),a0
	move.w	50(a0),d0
	add.w	#4,d0
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
	move.w	d0,-10(a5)
.4
	tst.w	-10(a5)
	beq	.5
	move.l	-8(a5),a0
	tst.w	48(a0)
	bne	.6
	move.l	-8(a5),a0
	move.w	#18,44(a0)
	move.l	-8(a5),a0
	move.w	32(a0),-(sp)
	move.l	-8(a5),a0
	move.w	30(a0),-(sp)
	move.w	#18,-(sp)
	move.l	-8(a5),a0
	add.l	#2,a0
	move.l	a0,-(sp)
	move.w	#2,-(sp)
	jsr	_F_h11_41F6
	lea	12(sp),sp
	bra	.7
.6
	tst.w	_G_h01_94B6
	beq	.8
	move.w	_G_h01_94D4,-(sp)
	jsr	_F_h11_407C
	add.w	#2,sp
	clr.w	_G_h01_94B6
.8
.7
	move.w	#2,_G_h01_94AE
	move.w	#2,-(sp)
	jsr	_F_h11_4B0C
	add.w	#2,sp
	move.l	-8(a5),a0
	clr.w	46(a0)
	move.w	8(a5),d0
	add.w	#12,d0
	move.w	d0,-(sp)
	move.w	#16,-(sp)
	move.w	#24,-(sp)
	move.l	-8(a5),a0
	move.w	60(a0),-(sp)
	move.l	-8(a5),a0
	move.w	56(a0),-(sp)
	jsr	_F_h11_4696
	lea	10(sp),sp
.5
	move.w	-10(a5),d0
.9
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-10
.3	reg	
	public	_F_h11_407C
	public	_F_h11_4696
	public	_F_h11_4B0C
	public	_F_h11_41F6
	public	_F_h11_262E
	public	.begin
	dseg
	public	_G_h01_9FCE
	public	_G_h01_94D4
	public	_G_h01_94C0
	public	_G_h01_94BE
	public	_G_h01_94B6
	public	_G_h01_94B0
	public	_G_h01_94AE
	end
