;:ts=8
	dseg
	ds	0
	public	_control_initialized
_control_initialized:
	dc.l	$0001
	cseg
	global	_control_common,8
	public	.begin
	dseg
	end
