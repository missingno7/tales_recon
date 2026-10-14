;:ts=8
	public	_F_h11_2DBA
_F_h11_2DBA:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	ext.l	d0
	asl.l	#6,d0
	lea	_G_h01_9FCE,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	cmp.w	#14,44(a0)
	beq	.4
	move.l	-4(a5),a0
	add.l	#2,a0
	move.l	a0,-(sp)
	jsr	_F_h11_4610
	add.w	#4,sp
.4
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	36(a0),38(a1)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	40(a0),42(a1)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	32(a0),40(a1)
	move.l	-4(a5),a0
	move.l	-4(a5),a1
	move.w	30(a0),36(a1)
.5
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	
	public	_F_h11_4610
	public	.begin
	dseg
	public	_G_h01_9FCE
	end
