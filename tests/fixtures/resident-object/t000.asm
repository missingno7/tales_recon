;:ts=8
	public	_recovered
_recovered:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.l	#7,d0
.4
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	
	public	.begin
	dseg
	end
