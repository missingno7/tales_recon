;:ts=8
	public	_F_h11_4A92
_F_h11_4A92:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.l	_G_h01_A460,-(sp)
	jsr	_F_h00_3B84
	add.w	#4,sp
.4
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	
	public	_F_h00_3B84
	public	.begin
	dseg
	public	_G_h01_A460
	end
