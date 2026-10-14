;:ts=8
	public	_F_h11_70DC
_F_h11_70DC:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	muls.w	#10,d0
	lea	_G_h01_A6A8,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	move.w	(a0),d0
	add.w	#1,d0
	move.w	d0,-(sp)
	move.w	_G_h01_94BA,-(sp)
	move.l	-4(a5),a0
	move.w	(a0),d0
	sub.w	#2,d0
	move.w	d0,-(sp)
	jsr	_F_h11_25D6
	add.w	#6,sp
	tst.w	d0
	beq	.4
	move.w	#9,-(sp)
	move.w	8(a5),-(sp)
	jsr	_F_h11_717A
	add.w	#4,sp
	move.l	-4(a5),a0
	move.w	6(a0),d0
	add.w	#30,d0
	move.w	d0,-(sp)
	move.l	-4(a5),a0
	move.w	4(a0),d0
	add.w	#48,d0
	move.w	d0,-(sp)
	move.w	_G_h01_94C0,d0
	add.w	#16,d0
	move.w	d0,-(sp)
	move.l	#8,d0
	move.w	_G_h01_94B0,d1
	asr.w	d1,d0
	add.w	_G_h01_94BE,d0
	move.w	d0,-(sp)
	move.l	-4(a5),a0
	move.w	6(a0),-(sp)
	move.l	-4(a5),a0
	move.w	4(a0),-(sp)
	jsr	_F_h11_25F8
	lea	12(sp),sp
	tst.w	d0
	beq	.5
	move.w	#1,_G_h01_12FE
.5
.4
.6
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	
	public	_F_h11_717A
_F_h11_717A:
	link	a5,#.7
	movem.l	.8,-(sp)
	move.w	8(a5),d0
	muls.w	#10,d0
	lea	_G_h01_A6B0,a0
	move.w	#2,(a0,d0.l)
.9
	movem.l	(sp)+,.8
	unlk	a5
	rts
.7	equ	0
.8	reg	
	public	_F_h11_25F8
	public	_F_h11_25D6
	public	.begin
	dseg
	public	_G_h01_A6B0
	public	_G_h01_A6A8
	public	_G_h01_94C0
	public	_G_h01_94BE
	public	_G_h01_94BA
	public	_G_h01_94B0
	public	_G_h01_12FE
	end
