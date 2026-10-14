;:ts=8
	public	_F_h11_13DC
_F_h11_13DC:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.l	_G_h01_94CE,a0
	cmp.l	_G_h01_9F4E,a0
	beq	.5
	move.l	_G_h01_94CE,a0
	cmp.l	_G_h01_9F56,a0
	bne	.4
.5
	move.w	#22,-(sp)
	move.w	#33,-(sp)
	move.w	#40,-(sp)
	move.w	_G_h01_94C4,-(sp)
	move.w	_G_h01_94C2,-(sp)
	jsr	_F_h11_4696
	lea	10(sp),sp
	move.w	#10,-(sp)
	move.w	#33,-(sp)
	move.w	#40,-(sp)
	move.w	_G_h01_94C4,-(sp)
	move.w	_G_h01_94C2,-(sp)
	jsr	_F_h11_583A
	lea	10(sp),sp
	bra	.6
.4
	move.l	_G_h01_94CE,a0
	cmp.l	_G_h01_9F52,a0
	bne	.7
	move.w	#22,-(sp)
	move.w	#41,-(sp)
	move.w	#48,-(sp)
	move.w	_G_h01_94C4,-(sp)
	move.w	_G_h01_94C2,-(sp)
	jsr	_F_h11_4696
	lea	10(sp),sp
	move.w	#10,-(sp)
	move.w	#41,-(sp)
	move.w	#48,-(sp)
	move.w	_G_h01_94C4,-(sp)
	move.w	_G_h01_94C2,-(sp)
	jsr	_F_h11_583A
	lea	10(sp),sp
	bra	.8
.7
	move.l	_G_h01_94CE,a0
	cmp.l	_G_h01_9F8E,a0
	bne	.9
	move.w	#22,-(sp)
	move.w	#34,-(sp)
	move.w	#88,-(sp)
	move.w	_G_h01_94C4,-(sp)
	move.w	_G_h01_94C2,-(sp)
	jsr	_F_h11_4696
	lea	10(sp),sp
	move.w	#10,-(sp)
	move.w	#34,-(sp)
	move.w	#88,-(sp)
	move.w	_G_h01_94C4,-(sp)
	move.w	_G_h01_94C2,-(sp)
	jsr	_F_h11_583A
	lea	10(sp),sp
.9
.8
.6
.10
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	
	public	_F_h11_583A
	public	_F_h11_4696
	public	.begin
	dseg
	public	_G_h01_9F8E
	public	_G_h01_9F56
	public	_G_h01_9F52
	public	_G_h01_9F4E
	public	_G_h01_94CE
	public	_G_h01_94C4
	public	_G_h01_94C2
	end
