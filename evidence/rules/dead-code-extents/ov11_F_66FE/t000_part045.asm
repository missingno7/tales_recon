;:ts=8
	public	_F_h11_49EA
_F_h11_49EA:
	link	a5,#.2
	movem.l	.3,-(sp)
	clr.l	-(sp)
	move.l	_G_h01_46CA,-(sp)
	jsr	_F_h00_8BC8
	add.w	#8,sp
	clr.l	-(sp)
	pea	255
	pea	192
	pea	176
	pea	320
	clr.l	-(sp)
	clr.l	-(sp)
	move.l	_G_h01_46D2,-(sp)
	clr.l	-(sp)
	clr.l	-(sp)
	move.l	_G_h01_46CE,-(sp)
	jsr	_F_h00_8A46
	lea	44(sp),sp
	move.l	_G_h01_9F5A,a0
	move.w	#48,(a0)
	move.l	_G_h01_9F5A,a0
	clr.w	2(a0)
	move.l	_G_h01_9F5A,a0
	move.b	#1,52(a0)
	move.l	_G_h01_9F5A,-(sp)
	jsr	_F_h00_34E0
	add.w	#4,sp
	move.w	#176,-(sp)
	move.w	#128,-(sp)
	jsr	_F_h00_3B16
	add.w	#4,sp
	move.l	d0,_G_h01_A460
	clr.l	-(sp)
	pea	255
	pea	192
	pea	176
	pea	104
	clr.l	-(sp)
	clr.l	-(sp)
	move.l	_G_h01_A460,-(sp)
	clr.l	-(sp)
	pea	56
	move.l	_G_h01_46D2,-(sp)
	jsr	_F_h00_8A46
	lea	44(sp),sp
	clr.w	_G_h01_A45E
	clr.w	_G_h01_8A3E
.4
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	
	public	_F_h00_3B16
	public	_F_h00_34E0
	public	_F_h00_8A46
	public	_F_h00_8BC8
	public	.begin
	dseg
	public	_G_h01_8A3E
	public	_G_h01_A45E
	public	_G_h01_A460
	public	_G_h01_9F5A
	public	_G_h01_46D2
	public	_G_h01_46CE
	public	_G_h01_46CA
	end
