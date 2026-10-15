; Typed bytecode data. No original source filename or TU is claimed.
SC_HEADER macro
	dc.b \1,\2
	endm
SC_NOTE macro
	dc.b \1,\2
	endm
SC_COUNT macro
	dc.b $80,\1
	endm
SC_LOOP macro
	dc.b $81
	ds 0
	dc.l \1
	endm
SC_TRIGGER macro
	dc.b $82,\1
	endm
SC_JUMP macro
	dc.b $84
	ds 0
	dc.l \1
	endm
SC_CALL macro
	dc.b $85
	ds 0
	dc.l \1
	endm
SC_RETURN macro
	dc.b $86
	endm
SC_TRANSPOSE macro
	dc.b $87,\1
	endm
SC_END macro
	dc.b $88
	endm
SC_REST macro
	dc.b $89,\1
	endm
SC_PLAY_NOTE macro
	dc.b $8b,\1,\2
	endm
SC_PITCH_ADJUST macro
	dc.b $8c,\1
	endm
SC_ENVELOPE macro
	dc.b $8f,\1
	endm
SC_BANK macro
	dc.b $90,\1
	endm
SC_RAMP macro
	dc.b $91,\1,\2
	endm
SC_VIBRATO macro
	dc.b $95,\1,\2
	endm
SC_TICK_INCREMENT macro
	dc.b $97,\1
	endm
SC_HOLD macro
	dc.b $a0,\1
	endm
SC_ATTENUATION macro
	dc.b $ab,\1
	endm
	cseg
	public _audio_score_16E4_begin
	public _audio_score_16E4_end
	public _audio_h_16E4
	public _audio_c_16F6
	public _audio_h_172C
	public _audio_c_173C
	public _audio_c_1748
	public _audio_h_1769
	public _audio_c_1779
	public _audio_c_1784
	public _audio_h_17F9
	public _audio_c_1809
	public _audio_c_1814
_audio_score_16E4_begin:
_audio_h_16E4:
	SC_HEADER 3,0
	SC_ATTENUATION 192
	SC_ENVELOPE 8
	SC_TRANSPOSE 0
	SC_TRIGGER 136
	SC_TRIGGER 140
	SC_TRIGGER 141
	SC_BANK 26
	SC_TICK_INCREMENT 224
_audio_c_16F6:
	SC_NOTE 51,4
	SC_REST 4
	SC_NOTE 52,4
	SC_REST 4
	SC_NOTE 53,4
	SC_REST 4
	SC_NOTE 54,4
	SC_REST 4
	SC_NOTE 55,4
	SC_REST 4
	SC_NOTE 56,4
	SC_REST 4
	SC_NOTE 57,4
	SC_REST 4
	SC_NOTE 56,4
	SC_REST 4
	SC_NOTE 55,4
	SC_REST 4
	SC_NOTE 54,4
	SC_REST 4
	SC_NOTE 53,4
	SC_REST 4
	SC_NOTE 52,4
	SC_REST 4
	SC_JUMP _audio_c_16F6
_audio_h_172C:
	SC_HEADER 0,0
	SC_ATTENUATION 136
	SC_ENVELOPE 8
	SC_TRANSPOSE 0
	SC_PITCH_ADJUST 0
	SC_BANK 24
	SC_TICK_INCREMENT 224
	SC_REST 6
_audio_c_173C:
	SC_CALL _audio_c_1748
	SC_JUMP _audio_c_173C
_audio_c_1748:
	SC_NOTE 71,24
	SC_REST 24
	SC_NOTE 71,8
	SC_REST 16
	SC_NOTE 71,8
	SC_REST 16
	SC_NOTE 72,56
	SC_REST 12
	SC_NOTE 72,12
	SC_REST 16
	SC_NOTE 73,36
	SC_REST 36
	SC_NOTE 73,8
	SC_REST 16
	SC_NOTE 74,92
	SC_REST 4
	SC_RETURN
_audio_h_1769:
	SC_HEADER 1,0
	SC_ATTENUATION 136
	SC_ENVELOPE 8
	SC_TRANSPOSE 0
	SC_PITCH_ADJUST 0
	SC_BANK 24
	SC_TICK_INCREMENT 224
	SC_REST 6
_audio_c_1779:
	SC_CALL _audio_c_1784
	SC_JUMP _audio_c_1779
_audio_c_1784:
	SC_NOTE 51,16
	SC_REST 8
	SC_NOTE 51,4
	SC_REST 4
	SC_NOTE 51,4
	SC_REST 4
	SC_NOTE 51,4
	SC_REST 16
	SC_NOTE 51,4
	SC_REST 20
	SC_NOTE 51,4
	SC_REST 8
	SC_NOTE 51,16
	SC_REST 8
	SC_NOTE 51,4
	SC_REST 4
	SC_NOTE 51,4
	SC_REST 4
	SC_NOTE 51,4
	SC_REST 4
	SC_NOTE 51,8
	SC_REST 4
	SC_NOTE 51,4
	SC_REST 8
	SC_NOTE 51,4
	SC_REST 8
	SC_NOTE 51,4
	SC_REST 8
	SC_NOTE 51,12
	SC_REST 12
	SC_NOTE 51,4
	SC_REST 4
	SC_NOTE 51,4
	SC_REST 4
	SC_NOTE 51,4
	SC_REST 4
	SC_NOTE 51,4
	SC_REST 8
	SC_NOTE 51,4
	SC_REST 20
	SC_NOTE 51,8
	SC_REST 4
	SC_NOTE 51,16
	SC_REST 8
	SC_NOTE 51,4
	SC_REST 4
	SC_NOTE 51,4
	SC_REST 4
	SC_NOTE 51,4
	SC_REST 4
	SC_NOTE 51,8
	SC_REST 4
	SC_NOTE 51,4
	SC_REST 8
	SC_NOTE 51,4
	SC_REST 8
	SC_NOTE 51,4
	SC_REST 8
	SC_RETURN
_audio_h_17F9:
	SC_HEADER 2,0
	SC_ATTENUATION 136
	SC_ENVELOPE 8
	SC_TRANSPOSE 0
	SC_PITCH_ADJUST 0
	SC_BANK 24
	SC_TICK_INCREMENT 224
	SC_REST 6
_audio_c_1809:
	SC_CALL _audio_c_1814
	SC_JUMP _audio_c_1809
_audio_c_1814:
	SC_NOTE 58,24
	SC_REST 24
	SC_NOTE 58,8
	SC_REST 16
	SC_NOTE 58,8
	SC_REST 16
	SC_NOTE 59,56
	SC_REST 16
	SC_NOTE 59,12
	SC_REST 12
	SC_NOTE 64,36
	SC_REST 36
	SC_NOTE 64,8
	SC_REST 16
	SC_NOTE 65,92
	SC_REST 4
	SC_RETURN
_audio_score_16E4_end:
	end
