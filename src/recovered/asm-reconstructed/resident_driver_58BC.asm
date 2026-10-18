	far data
	dseg
	public _audio_channel_0_state_pointer
	public _audio_pitch_effect_channel_mask
	cseg
	public _recon_h00_544C
	public _recon_h00_5A72
	public _recon_h00_58BC
	public _recon_h00_58C8
	public _recon_h00_58CA
	public _recon_h00_58E0
	public _recon_h00_58E6
	public _recon_h00_5912
	public _recon_h00_5926
	public _recon_h00_5936
	public _recon_h00_5950
	public _recon_h00_5964
	public _recon_h00_597A
	public _recon_h00_5982
	public _recon_h00_5994
	public _end_update
_recon_h00_58BC
	movem.l a2-a6,-(sp)
	bsr _recon_h00_58C8
	movem.l (sp)+,a2-a6
	rts
_recon_h00_58C8
	moveq #$3,d7
_recon_h00_58CA
	move.l d7,d0
	lsl.l #$2,d0
	lea _audio_channel_0_state_pointer,a0
	movea.l 0(a0,d0.l),a0
	tst.l $4(a0)
	beq _recon_h00_58E0
	bsr _recon_h00_58E6
_recon_h00_58E0
	dbra d7,_recon_h00_58CA
	rts
_recon_h00_58E6
	tst.b $39(a0)
	beq _recon_h00_5912
	clr.b $39(a0)
	move.w #$1,d0
	lsl.w d7,d0
	or.w #$8000,d0
	move.w d0,$dff096
	lsl.w #$7,d0
	move.w d0,$dff09c
	or.w #$8000,d0
	move.w d0,$dff09a
_recon_h00_5912
	move.b $49(a0),d0
	add.b d0,$48(a0)
	bcc _recon_h00_5936
	subq.b #$1,$8(a0)
	bne _recon_h00_5926
	bsr _recon_h00_5A72
_recon_h00_5926
	move.b $44(a0),d0
	cmp.b $8(a0),d0
	bne _recon_h00_5936
	move.b #$5,$1e(a0)
_recon_h00_5936
	bsr _recon_h00_544C
	move.l (a0),d2
	btst d7,_audio_pitch_effect_channel_mask
	beq _recon_h00_597A
	tst.b $38(a0)
	beq _recon_h00_5950
	subq.b #$1,$38(a0)
	bra _recon_h00_597A
_recon_h00_5950
	subq.b #$1,$18(a0)
	bne _recon_h00_5964
	move.b $19(a0),$18(a0)
	eori.l #$ffffffff,$14(a0)
_recon_h00_5964
	add.l $14(a0),d2
	move.l d2,(a0)
	swap d2
	move.w d7,d3
	lsl.w #$4,d3
	movea.l #$dff0a6,a2
	adda.w d3,a2
	move.w d2,(a2)
_recon_h00_597A
	tst.l $e(a0)
	bne _recon_h00_5982
	rts
_recon_h00_5982
	add.l $e(a0),d2
	move.l d2,(a0)
	swap d2
	cmp.w #$87,d2
	bcc _recon_h00_5994
	move.w #$87,d2
_recon_h00_5994
	move.w d7,d3
	lsl.w #$4,d3
	movea.l #$dff0a6,a2
	adda.w d3,a2
	move.w d2,(a2)
	rts
_end_update
	dseg
	end
