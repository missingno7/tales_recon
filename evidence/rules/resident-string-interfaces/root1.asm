	entry	.entry
.entry
	rts
	public	_strcpy,_strlen,_strcpy_body,_strlen_body
	dseg
_strcpy
	dc.w	$4ef9
	dc.l	_strcpy_body
_strlen
	dc.w	$4ef9
	dc.l	_strlen_body
