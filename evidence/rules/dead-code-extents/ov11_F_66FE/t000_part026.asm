;:ts=8
	public	_F_h11_37A0
_F_h11_37A0:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.w	8(a5),d0
	ext.l	d0
	asl.l	#6,d0
	lea	_G_h01_9FCE,a0
	add.l	a0,d0
	move.l	d0,-4(a5)
	move.l	-4(a5),a0
	tst.w	46(a0)
	beq	.4
	move.l	-4(a5),a0
	move.l	10(a5),a1
	move.w	50(a0),(a1)
	move.l	-4(a5),a0
	move.l	14(a5),a1
	move.w	52(a0),(a1)
.4
	move.l	-4(a5),a0
	move.w	46(a0),d0
.5
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	-4
.3	reg	
	public	.begin
	dseg
	public	_G_h01_9FCE
	end
