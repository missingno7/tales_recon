; Typed CODE-resident audio data; historical ownership/TU UNKNOWN.
T3_HEADER macro
	dc.b \1,\2
	endm
T3_NOTE macro
	dc.b \1,\2
	endm
T3_SELECTOR macro
	dc.l \1
	endm
T3_ENVELOPE_PTR macro
	dc.l \1
	endm
T3_ENV_INITIAL macro
	dc.b \1
	endm
T3_ENV_DELTA macro
	dc.b \1
	endm
T3_ENV_TARGET macro
	dc.b \1
	endm
T3_ENV_DELAY macro
	dc.b \1
	endm
T3_ENV_ZERO macro
	dc.b 0
	endm
T3_COUNT macro
	dc.b $80,\1
	endm
T3_LOOP macro
	dc.b $81
	ds 0
	dc.l \1
	endm
T3_TRIGGER macro
	dc.b $82,\1
	endm
T3_JUMP macro
	dc.b $84
	ds 0
	dc.l \1
	endm
T3_CALL macro
	dc.b $85
	ds 0
	dc.l \1
	endm
T3_RETURN macro
	dc.b $86
	endm
T3_TRANSPOSE macro
	dc.b $87,\1
	endm
T3_END macro
	dc.b $88
	endm
T3_REST macro
	dc.b $89,\1
	endm
T3_PLAY_NOTE macro
	dc.b $8b,\1,\2
	endm
T3_PITCH_ADJUST macro
	dc.b $8c,\1
	endm
T3_ENVELOPE macro
	dc.b $8f,\1
	endm
T3_BANK macro
	dc.b $90,\1
	endm
T3_RAMP macro
	dc.b $91,\1,\2
	endm
T3_VIBRATO macro
	dc.b $95,\1,\2
	endm
T3_TICK_INCREMENT macro
	dc.b $97,\1
	endm
T3_HOLD macro
	dc.b $a0,\1
	endm
T3_ATTENUATION macro
	dc.b $ab,\1
	endm
T3_FLAGS macro
	dc.b $83,\1
	endm
T3_RAMP_OFF macro
	dc.b $92
	endm
T3_RANDOM_NOTE macro
	dc.b $99,\1
	endm
T3_CHANNEL_ATTENUATION macro
	dc.b $9e,\1
	endm
T3_SOUND_ENABLE macro
	dc.b $9f,\1
	endm
T3_MASTER_ATTENUATION macro
	dc.b $a3,\1
	endm
T3_ADD_MASTER_ATTENUATION macro
	dc.b $a4,\1
	endm
	cseg
	public _audio3_04_begin
	public _audio3_04_end
	public _audio3_c_64DD
	public _audio3_e_6126
	public _audio3_e_6132
	public _audio3_h_64C0
	public _audio3_h_64C5
	public _audio3_h_64CA
	public _audio3_h_64D7
	public _audio3_h_64F1
	public _audio3_h_64F4
	public _audio3_h_64F7
	public _audio3_h_64FA
	public _audio3_h_64FD
	public _audio3_h_6500
	public _audio3_h_653A
	public _audio3_h_66A7
	public _audio3_h_66AE
	public _audio3_h_66DB
	public _audio3_h_66E6
	public _audio3_h_6708
	public _audio3_h_6726
	public _audio3_h_6740
	public _audio3_h_675B
	public _audio3_h_6774
	public _audio3_h_6786
	public _audio3_h_6792
	public _audio3_h_67CC
	public _audio3_h_6861
	public _audio3_h_68B5
	public _audio3_h_68C3
	public _audio3_h_68EC
	public _audio3_h_68FA
	public _audio3_h_6908
	public _audio3_h_6927
	public _audio3_h_6950
	public _audio3_h_695C
	public _audio3_h_696D
	public _audio3_h_6985
	public _audio3_h_699F
	public _audio3_h_69B6
	public _audio3_h_69FC
	public _audio3_h_6A0F
	public _audio3_h_6A22
	public _audio3_h_6A41
	public _audio3_h_6A78
	public _audio3_h_6AA0
	public _audio3_h_6ACC
	public _audio3_h_6ADB
	public _audio3_h_6AEF
	public _audio3_h_6B4A
	public _audio3_h_6B9A
	public _audio3_h_6BCD
	public _audio3_h_6D20
	public _audio3_h_6D3B
	public _audio3_h_6D53
	public _audio3_h_6D6B
	public _audio3_h_6DB4
	public _audio3_h_6DCD
	public _audio3_h_6DF9
	public _audio3_h_6E1C
	public _audio3_h_6E38
	public _audio3_h_6E49
	public _audio3_h_6E55
	public _audio3_h_6E67
	public _audio3_h_6E7B
	public _audio3_h_6E8F
	public _audio3_h_6EAE
	public _audio3_h_6ECC
	public _audio3_h_6EDC
	public _audio3_h_6F01
	public _audio3_h_6F21
	public _audio3_h_6F41
	public _audio_h_13B8
	public _audio_h_13DF
	public _audio_h_1402
	public _audio_h_1425
	public _audio_h_1448
	public _audio_h_149B
	public _audio_h_14F1
	public _audio_h_1543
	public _audio_h_1591
	public _audio_h_15E0
	public _audio_h_1601
	public _audio_h_165C
	public _audio_h_1693
	public _audio_h_16C8
	public _audio_h_16E4
	public _audio_h_172C
	public _audio_h_1769
	public _audio_h_17F9
	public _audio_h_1864
	public _audio_h_1870
	public _audio_h_19B9
	public _audio_h_19C8
	public _audio_h_1A9E
	public _audio_h_1AA8
	public _audio_h_1BC7
	public _audio_h_1BD4
	public _audio_h_1CC6
	public _audio_h_1E67
	public _audio_h_21DE
	public _audio_h_2317
	public _audio_h_245E
	public _audio_h_257C
	public _audio_h_2611
	public _audio_h_26B9
	public _audio_h_2769
_audio3_04_begin:
_audio3_e_6126:
	T3_ENV_DELTA -1
	T3_ENV_TARGET 8
	T3_ENV_ZERO
	T3_ENV_ZERO
_audio3_e_6132:
	T3_ENV_DELTA -5
	T3_ENV_TARGET 0
	T3_SELECTOR _audio3_h_64CA
	T3_SELECTOR _audio_h_19C8
	T3_SELECTOR _audio3_h_6B9A
	T3_SELECTOR _audio3_h_653A
	T3_SELECTOR _audio3_h_64F1
	T3_SELECTOR _audio3_h_6ACC
	T3_SELECTOR _audio3_h_6AA0
	T3_SELECTOR _audio3_h_6E49
	T3_SELECTOR _audio3_h_6B4A
	T3_SELECTOR _audio3_h_6AEF
	T3_SELECTOR _audio3_h_6A78
	T3_SELECTOR _audio3_h_6ADB
	T3_SELECTOR _audio3_h_64F1
	T3_SELECTOR _audio3_h_64F1
	T3_SELECTOR _audio3_h_6E8F
	T3_SELECTOR _audio_h_21DE
	T3_SELECTOR _audio_h_257C
	T3_SELECTOR _audio_h_13B8
	T3_SELECTOR _audio3_h_64D7
	T3_SELECTOR _audio3_h_67CC
	T3_SELECTOR _audio_h_16E4
	T3_SELECTOR _audio3_h_69B6
	T3_SELECTOR _audio3_h_69FC
	T3_SELECTOR _audio3_h_6A41
	T3_SELECTOR _audio_h_13B8
	T3_SELECTOR _audio3_h_6A0F
	T3_SELECTOR _audio3_h_6A22
	T3_SELECTOR _audio3_h_6950
	T3_SELECTOR _audio3_h_6792
	T3_SELECTOR _audio3_h_6985
	T3_SELECTOR _audio3_h_699F
	T3_SELECTOR _audio3_h_695C
	T3_SELECTOR _audio_h_13B8
	T3_SELECTOR _audio3_h_696D
	T3_SELECTOR _audio3_h_64F1
	T3_SELECTOR _audio3_h_6786
	T3_SELECTOR _audio_h_1693
	T3_SELECTOR _audio_h_16C8
	T3_SELECTOR _audio3_h_6ECC
	T3_SELECTOR _audio3_h_6EAE
	T3_SELECTOR _audio3_h_6E67
	T3_SELECTOR _audio3_h_6E7B
	T3_SELECTOR _audio3_h_6E1C
	T3_SELECTOR _audio3_h_6E38
	T3_SELECTOR _audio3_h_66AE
	T3_SELECTOR _audio_h_15E0
	T3_SELECTOR _audio_h_165C
	T3_SELECTOR _audio_h_1591
	T3_SELECTOR _audio_h_1601
	T3_SELECTOR _audio3_h_6DB4
	T3_SELECTOR _audio3_h_6D20
	T3_SELECTOR _audio3_h_6DCD
	T3_SELECTOR _audio3_h_64F1
	T3_SELECTOR _audio3_h_64F1
	T3_SELECTOR _audio3_h_68FA
	T3_SELECTOR _audio3_h_696D
	T3_SELECTOR _audio3_h_6500
	T3_SELECTOR _audio3_h_68B5
	T3_SELECTOR _audio_h_1CC6
	T3_SELECTOR _audio3_h_68C3
	T3_SELECTOR _audio3_h_68EC
	T3_SELECTOR _audio_h_19B9
	T3_SELECTOR _audio3_h_6927
	T3_SELECTOR _audio3_h_6861
	T3_SELECTOR _audio3_h_6908
	T3_SELECTOR _audio3_h_64F1
	T3_SELECTOR _audio3_h_6E55
	T3_SELECTOR _audio3_h_6774
	T3_SELECTOR _audio3_h_675B
	T3_SELECTOR _audio3_h_6740
	T3_SELECTOR _audio3_h_6708
	T3_SELECTOR _audio3_h_66E6
	T3_SELECTOR _audio3_h_6726
	T3_SELECTOR _audio3_h_6EDC
	T3_SELECTOR _audio_h_1448
	T3_SELECTOR _audio3_h_6BCD
	T3_SELECTOR _audio3_h_64F1
	T3_SELECTOR _audio3_h_64F1
	T3_SELECTOR _audio3_h_64F1
	T3_SELECTOR _audio3_h_64F1
	T3_SELECTOR _audio3_h_64F1
	T3_SELECTOR _audio3_h_64F1
	T3_SELECTOR _audio3_h_64F1
	T3_SELECTOR _audio3_h_64C0
	T3_SELECTOR _audio3_h_64C5
	T3_SELECTOR _audio_h_1AA8
	T3_SELECTOR _audio_h_1BD4
	T3_SELECTOR _audio_h_1870
	T3_SELECTOR _audio_h_1E67
	T3_SELECTOR _audio_h_2611
	T3_SELECTOR _audio_h_26B9
	T3_SELECTOR _audio_h_2317
	T3_SELECTOR _audio_h_245E
	T3_SELECTOR _audio_h_172C
	T3_SELECTOR _audio3_h_64F7
	T3_SELECTOR _audio3_h_64FA
	T3_SELECTOR _audio3_h_64FD
	T3_SELECTOR _audio_h_17F9
	T3_SELECTOR _audio_h_1769
	T3_SELECTOR _audio_h_2769
	T3_SELECTOR _audio3_h_66DB
	T3_SELECTOR _audio3_h_66A7
	T3_SELECTOR _audio3_h_6F01
	T3_SELECTOR _audio3_h_6F21
	T3_SELECTOR _audio3_h_6F41
	T3_SELECTOR _audio_h_149B
	T3_SELECTOR _audio_h_14F1
	T3_SELECTOR _audio_h_1543
	T3_SELECTOR _audio3_h_64F4
	T3_SELECTOR _audio_h_13DF
	T3_SELECTOR _audio_h_1402
	T3_SELECTOR _audio_h_1425
	T3_SELECTOR _audio3_h_6D3B
	T3_SELECTOR _audio3_h_6D53
	T3_SELECTOR _audio3_h_6D6B
	T3_SELECTOR _audio3_h_6DF9
	T3_SELECTOR _audio_h_1864
	T3_SELECTOR _audio_h_1A9E
	T3_SELECTOR _audio_h_1BC7
_audio3_h_64C0:
	T3_HEADER 0,10
	T3_SOUND_ENABLE 0
	T3_END
_audio3_h_64C5:
	T3_HEADER 0,10
	T3_SOUND_ENABLE 1
	T3_END
_audio3_h_64CA:
	T3_HEADER 0,10
	T3_MASTER_ATTENUATION 0
	T3_TICK_INCREMENT 255
	T3_TRIGGER 137
	T3_TRIGGER 138
	T3_TRIGGER 139
	T3_END
_audio3_h_64D7:
	T3_HEADER 3,8
	T3_MASTER_ATTENUATION 0
	T3_COUNT 120
_audio3_c_64DD:
	T3_ADD_MASTER_ATTENUATION 1
	T3_REST 2
	T3_LOOP _audio3_c_64DD
	T3_TRIGGER 137
	T3_TRIGGER 138
	T3_TRIGGER 161
	T3_REST 2
	T3_MASTER_ATTENUATION 0
	T3_END
_audio3_h_64F1:
	T3_HEADER 0,10
	T3_END
_audio3_h_64F4:
	T3_HEADER 0,10
	T3_END
_audio3_h_64F7:
	T3_HEADER 1,10
	T3_END
_audio3_h_64FA:
	T3_HEADER 2,10
	T3_END
_audio3_h_64FD:
	T3_HEADER 3,10
	T3_END
_audio3_h_6500:
	T3_HEADER 0,0
	T3_ENVELOPE 0
	T3_BANK 7
	T3_ATTENUATION 208
	T3_RAMP 236,255
	T3_TRANSPOSE 16
	T3_NOTE 80,6
	T3_REST 4
	T3_NOTE 80,6
	T3_REST 4
	T3_NOTE 80,6
	T3_REST 4
	T3_NOTE 80,6
	T3_REST 4
	T3_REST 1
	T3_NOTE 80,4
	T3_REST 1
	T3_NOTE 80,4
	T3_REST 1
	T3_NOTE 80,4
	T3_REST 1
	T3_NOTE 80,4
	T3_REST 1
	T3_NOTE 80,4
	T3_REST 1
	T3_NOTE 80,4
	T3_END
_audio3_h_653A:
	T3_HEADER 0,0
	T3_ENVELOPE 0
	T3_BANK 27
	T3_TRANSPOSE 0
	T3_NOTE 48,4
	T3_NOTE 32,4
	T3_NOTE 48,4
	T3_NOTE 0,32
	T3_NOTE 32,4
	T3_NOTE 48,4
	T3_ATTENUATION 128
	T3_NOTE 32,4
	T3_ATTENUATION 144
	T3_NOTE 32,4
	T3_ATTENUATION 160
	T3_NOTE 32,4
	T3_ATTENUATION 176
	T3_NOTE 32,4
	T3_ATTENUATION 192
	T3_NOTE 32,4
	T3_ATTENUATION 208
	T3_NOTE 32,4
	T3_NOTE 16,4
	T3_NOTE 0,4
	T3_END
_audio3_04_end:
	end
