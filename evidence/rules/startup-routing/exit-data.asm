	public _exit
	dseg
_exit
	dc.w $4ef9
	dc.l _exit_body
	cseg
	public _exit_body
_exit_body
	rts
