;:ts=8
	dseg
	ds	0
	public	_candidate_reference
_candidate_reference:
	dc.l	_recovered
	cseg
	public	_main
_main:
	link	a5,#.2
	movem.l	.3,-(sp)
	move.l	#0,d0
.4
	movem.l	(sp)+,.3
	unlk	a5
	rts
.2	equ	0
.3	reg	
	public	_recovered
	public	.begin
	dseg
	end
