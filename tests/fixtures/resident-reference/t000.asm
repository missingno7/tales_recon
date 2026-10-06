;:ts=8
	public	_recovered
_recovered:
	link	a5,#.2
	movem.l	.3,-(sp)
	jsr	_F_h00_0200
	add.w	_G_h01_0100,d0
.4
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	
	public	_F_h00_0200
	public	.begin
	dseg
	public	_G_h01_0100
	end
