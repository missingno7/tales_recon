;:ts=8
	public	_F_h11_49CE
_F_h11_49CE:
	link	a5,#.2
	movem.l	.3,-(sp)
	clr.w	_G_h01_8A3E
	move.w	_G_h01_A45E,d0
	ext.l	d0
	divs.w	#320,d0
	swap	d0
	move.w	d0,_G_h01_A45E
.4
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	
	public	.begin
	dseg
	public	_G_h01_A45E
	public	_G_h01_8A3E
	end
