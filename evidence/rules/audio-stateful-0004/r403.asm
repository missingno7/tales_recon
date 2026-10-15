; Typed CODE-resident audio data; historical ownership/TU UNKNOWN.
T4_HEADER macro
	dc.b \1,\2
	endm
T4_NOTE macro
	dc.b \1,\2
	endm
T4_SELECTOR macro
	dc.l \1
	endm
T4_ENVELOPE_PTR macro
	dc.l \1
	endm
T4_ENV_INITIAL macro
	dc.b \1
	endm
T4_ENV_DELTA macro
	dc.b \1
	endm
T4_ENV_TARGET macro
	dc.b \1
	endm
T4_ENV_DELAY macro
	dc.b \1
	endm
T4_ENV_ZERO macro
	dc.b 0
	endm
T4_COUNT macro
	dc.b $80,\1
	endm
T4_LOOP macro
	dc.b $81
	ds 0
	dc.l \1
	endm
T4_TRIGGER macro
	dc.b $82,\1
	endm
T4_JUMP macro
	dc.b $84
	ds 0
	dc.l \1
	endm
T4_CALL macro
	dc.b $85
	ds 0
	dc.l \1
	endm
T4_RETURN macro
	dc.b $86
	endm
T4_TRANSPOSE macro
	dc.b $87,\1
	endm
T4_END macro
	dc.b $88
	endm
T4_REST macro
	dc.b $89,\1
	endm
T4_PLAY_NOTE macro
	dc.b $8b,\1,\2
	endm
T4_PITCH_ADJUST macro
	dc.b $8c,\1
	endm
T4_ENVELOPE macro
	dc.b $8f,\1
	endm
T4_BANK macro
	dc.b $90,\1
	endm
T4_RAMP macro
	dc.b $91,\1,\2
	endm
T4_VIBRATO macro
	dc.b $95,\1,\2
	endm
T4_TICK_INCREMENT macro
	dc.b $97,\1
	endm
T4_HOLD macro
	dc.b $a0,\1
	endm
T4_ATTENUATION macro
	dc.b $ab,\1
	endm
T4_FLAGS macro
	dc.b $83,\1
	endm
T4_RAMP_OFF macro
	dc.b $92
	endm
T4_RANDOM_NOTE macro
	dc.b $99,\1
	endm
T4_CHANNEL_ATTENUATION macro
	dc.b $9e,\1
	endm
T4_SOUND_ENABLE macro
	dc.b $9f,\1
	endm
T4_MASTER_ATTENUATION macro
	dc.b $a3,\1
	endm
T4_ADD_MASTER_ATTENUATION macro
	dc.b $a4,\1
	endm
T4_WAIT_SAMPLE macro
	dc.b $a7
	endm
T4_RESTART_ENVELOPE macro
	dc.b $a8,\1
	endm
T4_SAMPLE_TIMED macro
	dc.b $9a,\1
	ds 0
	dc.w \2
	dc.b \3
	endm
T4_SAMPLE_WAIT macro
	dc.b $9a,\1
	ds 0
	dc.w \2
	endm
T4_SAMPLE93_TIMED macro
	dc.b $93,\1
	ds 0
	dc.w \2
	dc.b \3
	endm
T4_SAMPLE93_WAIT macro
	dc.b $93,\1
	ds 0
	dc.w \2
	endm
	cseg
	public _r403_begin
	public _r403_end
	public _G_h00_6200
	public _audio4_c_64DD
	public _audio4_c_6579
	public _audio4_h_64C0
	public _audio4_h_64C5
	public _audio4_h_64CA
	public _audio4_h_64D7
	public _audio4_h_64F1
	public _audio4_h_64F4
	public _audio4_h_64F7
	public _audio4_h_64FA
	public _audio4_h_64FD
	public _audio4_h_6500
	public _audio4_h_653A
	public _audio4_h_656B
	public _audio4_h_65A3
	public _audio4_h_65BD
	public _audio4_h_65D5
	public _audio4_h_6600
	public _audio4_h_6624
	public _audio4_h_6648
	public _audio4_h_666C
	public _audio4_h_667E
	public _audio4_h_6693
	public _audio4_h_66A7
	public _audio4_h_66AE
	public _audio4_h_66DB
	public _audio4_h_66E6
	public _audio4_h_6708
	public _audio4_h_6726
	public _audio4_h_6734
	public _audio4_h_6740
	public _audio4_h_675B
	public _audio4_h_6774
	public _audio4_h_6786
	public _audio4_h_6792
	public _audio4_h_67AF
	public _audio4_h_67CC
	public _audio4_h_67EF
	public _audio4_h_6802
	public _audio4_h_681A
	public _audio4_h_683E
	public _audio4_h_684A
	public _audio4_h_6861
	public _audio4_h_687C
	public _audio4_h_68B5
	public _audio4_h_68C3
	public _audio4_h_68D1
	public _audio4_h_68EC
	public _audio4_h_68FA
	public _audio4_h_6908
	public _audio4_h_6927
	public _audio4_h_6938
	public _audio4_h_6950
	public _audio4_h_695C
	public _audio4_h_696D
	public _audio4_h_6985
	public _audio4_h_699F
	public _audio4_h_69B6
	public _audio4_h_69CD
	public _audio4_h_69E4
	public _audio4_h_69F0
	public _audio4_h_69FC
	public _audio4_h_6A0F
	public _audio4_h_6A22
	public _audio4_h_6A41
	public _audio4_h_6A54
	public _audio4_h_6A68
	public _audio4_h_6A78
	public _audio4_h_6AA0
	public _audio4_h_6AAC
	public _audio4_h_6AC0
	public _audio4_h_6ACC
	public _audio4_h_6ADB
	public _audio4_h_6AEF
	public _audio4_h_6B20
	public _audio4_h_6B2E
	public _audio4_h_6B4A
	public _audio4_h_6B69
	public _audio4_h_6B82
	public _audio4_h_6B9A
	public _audio4_h_6BCD
	public _audio4_h_6BD6
	public _audio4_h_6BE2
	public _audio4_h_6BEE
	public _audio4_h_6BFA
	public _audio4_h_6C06
	public _audio4_h_6C12
	public _audio4_h_6C1E
	public _audio4_h_6C32
	public _audio4_h_6C3A
	public _audio4_h_6C62
	public _audio4_h_6C86
	public _audio4_h_6CAA
	public _audio4_h_6CB6
	public _audio4_h_6CD2
	public _audio4_h_6CDA
	public _audio4_h_6CF4
	public _audio4_h_6D08
	public _audio4_h_6D14
	public _audio4_h_6D20
	public _audio4_h_6D3B
	public _audio4_h_6D53
	public _audio4_h_6D6B
	public _audio4_h_6DB4
	public _audio4_h_6DCD
	public _audio4_h_6DF9
	public _audio4_h_6E1C
	public _audio4_h_6E38
	public _audio4_h_6E49
	public _audio4_h_6E55
	public _audio4_h_6E67
	public _audio4_h_6E7B
	public _audio4_h_6E8F
	public _audio4_h_6EAE
	public _audio4_h_6ECC
	public _audio4_h_6EDC
	public _audio4_h_6F01
	public _audio4_h_6F21
	public _audio4_h_6F41
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
_r403_begin:
_G_h00_6200:
	T4_SELECTOR _audio4_h_64CA
	T4_SELECTOR _audio_h_19C8
	T4_SELECTOR _audio4_h_67EF
	T4_SELECTOR _audio4_h_6B9A
	T4_SELECTOR _audio4_h_681A
	T4_SELECTOR _audio4_h_653A
	T4_SELECTOR _audio4_h_6802
	T4_SELECTOR _audio4_h_64F1
	T4_SELECTOR _audio4_h_6A54
	T4_SELECTOR _audio4_h_6ACC
	T4_SELECTOR _audio4_h_6AA0
	T4_SELECTOR _audio4_h_6E49
	T4_SELECTOR _audio4_h_6B2E
	T4_SELECTOR _audio4_h_6B20
	T4_SELECTOR _audio4_h_6B4A
	T4_SELECTOR _audio4_h_667E
	T4_SELECTOR _audio4_h_6AAC
	T4_SELECTOR _audio4_h_6AEF
	T4_SELECTOR _audio4_h_6A78
	T4_SELECTOR _audio4_h_6A68
	T4_SELECTOR _audio4_h_6ADB
	T4_SELECTOR _audio4_h_6AC0
	T4_SELECTOR _audio4_h_6B69
	T4_SELECTOR _audio4_h_6B82
	T4_SELECTOR _audio4_h_6BEE
	T4_SELECTOR _audio4_h_64F1
	T4_SELECTOR _audio4_h_64F1
	T4_SELECTOR _audio4_h_6E8F
	T4_SELECTOR _audio4_h_6693
	T4_SELECTOR _audio_h_21DE
	T4_SELECTOR _audio_h_257C
	T4_SELECTOR _audio_h_13B8
	T4_SELECTOR _audio4_h_64D7
	T4_SELECTOR _audio4_h_666C
	T4_SELECTOR _audio4_h_683E
	T4_SELECTOR _audio4_h_67AF
	T4_SELECTOR _audio4_h_67CC
	T4_SELECTOR _audio_h_16E4
	T4_SELECTOR _audio4_h_6C86
	T4_SELECTOR _audio4_h_69CD
	T4_SELECTOR _audio4_h_69B6
	T4_SELECTOR _audio4_h_69FC
	T4_SELECTOR _audio4_h_69F0
	T4_SELECTOR _audio4_h_6A41
	T4_SELECTOR _audio_h_13B8
	T4_SELECTOR _audio4_h_6C12
	T4_SELECTOR _audio4_h_6A0F
	T4_SELECTOR _audio4_h_6A22
	T4_SELECTOR _audio4_h_69E4
	T4_SELECTOR _audio4_h_6950
	T4_SELECTOR _audio4_h_6792
	T4_SELECTOR _audio4_h_6985
	T4_SELECTOR _audio4_h_699F
	T4_SELECTOR _audio4_h_6938
	T4_SELECTOR _audio4_h_695C
	T4_SELECTOR _audio4_h_6B69
	T4_SELECTOR _audio_h_13B8
	T4_SELECTOR _audio4_h_696D
	T4_SELECTOR _audio4_h_64F1
	T4_SELECTOR _audio4_h_65D5
	T4_SELECTOR _audio4_h_6786
	T4_SELECTOR _audio_h_1693
	T4_SELECTOR _audio_h_16C8
	T4_SELECTOR _audio4_h_6ECC
	T4_SELECTOR _audio4_h_6EAE
	T4_SELECTOR _audio4_h_6C1E
	T4_SELECTOR _audio4_h_6E67
	T4_SELECTOR _audio4_h_6E7B
	T4_SELECTOR _audio4_h_6E1C
	T4_SELECTOR _audio4_h_6E38
	T4_SELECTOR _audio4_h_6CF4
	T4_SELECTOR _audio4_h_6CAA
	T4_SELECTOR _audio4_h_6C62
	T4_SELECTOR _audio4_h_656B
	T4_SELECTOR _audio4_h_6C3A
	T4_SELECTOR _audio4_h_6BE2
	T4_SELECTOR _audio4_h_66AE
	T4_SELECTOR _audio_h_15E0
	T4_SELECTOR _audio_h_165C
	T4_SELECTOR _audio_h_1591
	T4_SELECTOR _audio_h_1601
	T4_SELECTOR _audio4_h_6DB4
	T4_SELECTOR _audio4_h_6D20
	T4_SELECTOR _audio4_h_6DCD
	T4_SELECTOR _audio4_h_64F1
	T4_SELECTOR _audio4_h_64F1
	T4_SELECTOR _audio4_h_68FA
	T4_SELECTOR _audio4_h_696D
	T4_SELECTOR _audio4_h_6500
	T4_SELECTOR _audio4_h_68B5
	T4_SELECTOR _audio4_h_68D1
	T4_SELECTOR _audio_h_1CC6
	T4_SELECTOR _audio4_h_68C3
	T4_SELECTOR _audio4_h_68EC
	T4_SELECTOR _audio_h_19B9
	T4_SELECTOR _audio4_h_684A
	T4_SELECTOR _audio4_h_687C
	T4_SELECTOR _audio4_h_6927
	T4_SELECTOR _audio4_h_6861
	T4_SELECTOR _audio4_h_6908
	T4_SELECTOR _audio4_h_64F1
	T4_SELECTOR _audio4_h_6E55
	T4_SELECTOR _audio4_h_6774
	T4_SELECTOR _audio4_h_675B
	T4_SELECTOR _audio4_h_6740
	T4_SELECTOR _audio4_h_6734
	T4_SELECTOR _audio4_h_6708
	T4_SELECTOR _audio4_h_66E6
	T4_SELECTOR _audio4_h_6726
	T4_SELECTOR _audio4_h_6EDC
	T4_SELECTOR _audio_h_1448
	T4_SELECTOR _audio4_h_6BCD
	T4_SELECTOR _audio4_h_6BD6
	T4_SELECTOR _audio4_h_64F1
	T4_SELECTOR _audio4_h_64F1
	T4_SELECTOR _audio4_h_64F1
	T4_SELECTOR _audio4_h_64F1
	T4_SELECTOR _audio4_h_64F1
	T4_SELECTOR _audio4_h_6BE2
	T4_SELECTOR _audio4_h_6BEE
	T4_SELECTOR _audio4_h_6BFA
	T4_SELECTOR _audio4_h_6C06
	T4_SELECTOR _audio4_h_6C12
	T4_SELECTOR _audio4_h_64F1
	T4_SELECTOR _audio4_h_64F1
	T4_SELECTOR _audio4_h_64C0
	T4_SELECTOR _audio4_h_64C5
	T4_SELECTOR _audio_h_1AA8
	T4_SELECTOR _audio_h_1BD4
	T4_SELECTOR _audio_h_1870
	T4_SELECTOR _audio_h_1E67
	T4_SELECTOR _audio_h_2611
	T4_SELECTOR _audio_h_26B9
	T4_SELECTOR _audio_h_2317
	T4_SELECTOR _audio_h_245E
	T4_SELECTOR _audio_h_172C
	T4_SELECTOR _audio4_h_64F7
	T4_SELECTOR _audio4_h_64FA
	T4_SELECTOR _audio4_h_64FD
	T4_SELECTOR _audio_h_17F9
	T4_SELECTOR _audio_h_1769
	T4_SELECTOR _audio_h_2769
	T4_SELECTOR _audio4_h_66DB
	T4_SELECTOR _audio4_h_6CB6
	T4_SELECTOR _audio4_h_6D08
	T4_SELECTOR _audio4_h_6D14
	T4_SELECTOR _audio4_h_66A7
	T4_SELECTOR _audio4_h_6CDA
	T4_SELECTOR _audio4_h_6CD2
	T4_SELECTOR _audio4_h_6F01
	T4_SELECTOR _audio4_h_6F21
	T4_SELECTOR _audio4_h_6F41
	T4_SELECTOR _audio4_h_6600
	T4_SELECTOR _audio4_h_6624
	T4_SELECTOR _audio4_h_6648
	T4_SELECTOR _audio4_h_65A3
	T4_SELECTOR _audio4_h_65BD
	T4_SELECTOR _audio_h_149B
	T4_SELECTOR _audio_h_14F1
	T4_SELECTOR _audio_h_1543
	T4_SELECTOR _audio4_h_64F4
	T4_SELECTOR _audio_h_13DF
	T4_SELECTOR _audio_h_1402
	T4_SELECTOR _audio_h_1425
	T4_SELECTOR _audio4_h_6C32
	T4_SELECTOR _audio4_h_6D3B
	T4_SELECTOR _audio4_h_6D53
	T4_SELECTOR _audio4_h_6D6B
	T4_SELECTOR _audio4_h_6DF9
	T4_SELECTOR _audio_h_1864
	T4_SELECTOR _audio_h_1A9E
	T4_SELECTOR _audio_h_1BC7
_audio4_h_64C0:
	T4_HEADER 0,10
	T4_SOUND_ENABLE 0
	T4_END
_audio4_h_64C5:
	T4_HEADER 0,10
	T4_SOUND_ENABLE 1
	T4_END
_audio4_h_64CA:
	T4_HEADER 0,10
	T4_MASTER_ATTENUATION 0
	T4_TICK_INCREMENT 255
	T4_TRIGGER 137
	T4_TRIGGER 138
	T4_TRIGGER 139
	T4_END
_audio4_h_64D7:
	T4_HEADER 3,8
	T4_MASTER_ATTENUATION 0
	T4_COUNT 120
_audio4_c_64DD:
	T4_ADD_MASTER_ATTENUATION 1
	T4_REST 2
	T4_LOOP _audio4_c_64DD
	T4_TRIGGER 137
	T4_TRIGGER 138
	T4_TRIGGER 161
	T4_REST 2
	T4_MASTER_ATTENUATION 0
	T4_END
_audio4_h_64F1:
	T4_HEADER 0,10
	T4_END
_audio4_h_64F4:
	T4_HEADER 0,10
	T4_END
_audio4_h_64F7:
	T4_HEADER 1,10
	T4_END
_audio4_h_64FA:
	T4_HEADER 2,10
	T4_END
_audio4_h_64FD:
	T4_HEADER 3,10
	T4_END
_audio4_h_6500:
	T4_HEADER 0,0
	T4_ENVELOPE 0
	T4_BANK 7
	T4_ATTENUATION 208
	T4_RAMP 236,255
	T4_TRANSPOSE 16
	T4_NOTE 80,6
	T4_REST 4
	T4_NOTE 80,6
	T4_REST 4
	T4_NOTE 80,6
	T4_REST 4
	T4_NOTE 80,6
	T4_REST 4
	T4_REST 1
	T4_NOTE 80,4
	T4_REST 1
	T4_NOTE 80,4
	T4_REST 1
	T4_NOTE 80,4
	T4_REST 1
	T4_NOTE 80,4
	T4_REST 1
	T4_NOTE 80,4
	T4_REST 1
	T4_NOTE 80,4
	T4_END
_audio4_h_653A:
	T4_HEADER 0,0
	T4_ENVELOPE 0
	T4_BANK 27
	T4_TRANSPOSE 0
	T4_NOTE 48,4
	T4_NOTE 32,4
	T4_NOTE 48,4
	T4_NOTE 0,32
	T4_NOTE 32,4
	T4_NOTE 48,4
	T4_ATTENUATION 128
	T4_NOTE 32,4
	T4_ATTENUATION 144
	T4_NOTE 32,4
	T4_ATTENUATION 160
	T4_NOTE 32,4
	T4_ATTENUATION 176
	T4_NOTE 32,4
	T4_ATTENUATION 192
	T4_NOTE 32,4
	T4_ATTENUATION 208
	T4_NOTE 32,4
	T4_NOTE 16,4
	T4_NOTE 0,4
	T4_END
_audio4_h_656B:
	T4_HEADER 0,0
	T4_ENVELOPE 62
	T4_FLAGS 255
	T4_SAMPLE_TIMED 10,2304,1
	T4_COUNT 22
_audio4_c_6579:
	T4_RAMP 216,0
	T4_HOLD 5
	T4_RAMP 26,0
	T4_HOLD 4
	T4_LOOP _audio4_c_6579
	T4_END
_r403_end:
	end
