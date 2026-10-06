;:ts=8
	global	_SysBase,4
	global	_DOSBase,4
	global	_MathBase,4
	global	_MathTransBase,4
	global	_MathIeeeDoubBasBase,4
	global	_MathIeeeDoubTransBase,4
	global	__savsp,4
	global	__stkbase,4
	global	_errno,2
	global	_Enable_Abort,2
	global	__argc,2
	global	__arg_len,2
	global	__argv,4
	global	__arg_lin,4
	global	_WBenchMsg,4
	global	__devtab,4
	dseg
	ds	0
	public	__numdev
__numdev:
	dc.w	20
	cseg
	global	__detach_name,4
	global	__detach_curdir,4
	global	__oldtrap,4
	global	__trapaddr,4
	public	.begin
	dseg
	end
