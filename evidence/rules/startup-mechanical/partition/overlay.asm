;:ts=8
	public	_F_h03_0000
_F_h03_0000:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.l	#0,d0
.4
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	
	public	.begin
	dseg
	end
