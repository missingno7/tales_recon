	entry	.entry
.entry
	rts
	public	_strcpy,_strlen,_strcpy_body,_strlen_body
	dseg
	dc.w	1,2,3
_strcpy
	dc.w	$4ef9
	dc.l	_strcpy_body
_strlen
	dc.w	$4ef9
	dc.l	_strlen_body
