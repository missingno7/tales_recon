"""Individually bounded audio state fields; unknown channel holes stay raw.

The four channel pointers establish four bases, never a channel allocation or
stride. Curated field interpretation is checked against current named ASM
operands. Periods are WORD cells in a conditional note-index domain, not a
claimed historical twelve-element allocation.
"""
import json,re
from common import require,sha256
from repo_paths import canonical_path
from audio_sequence_data import payload
from data_provider_sequences import anchors,pointer_target

ROUTES={'AUDIO_CHANNEL_FIELD','AUDIO_IRQ_FIELD','AUDIO_GLOBAL_CELL','AUDIO_PERIOD_WORD'}
CHANNEL={
 'period_accumulator':('resident_driver_58BC','move.l (a0),d2'),
 'stream':('resident_driver_5A50','move.l a1,$4(a0)'),
 'ticks':('resident_driver_5A50','move.b (a1)+,$8(a0)'),
 'loop_count':('resident_driver_5CC6','subq.b #$1,$a(a0)'),
 'period_offset':('resident_asm_59A4','add.w $c(a0),d1'),
 'period_slide':('resident_driver_58BC','add.l $e(a0),d2'),
 'note_offset':('resident_driver_5CC6','move.b d0,$12(a0)'),
 'vibrato_delta':('resident_driver_58BC','add.l $14(a0),d2'),
 'vibrato_count':('resident_driver_58BC','subq.b #$1,$18(a0)'),
 'vibrato_reload':('resident_driver_58BC','move.b $19(a0),$18(a0)'),
 'envelope':('resident_driver_544C','movea.l $1a(a0),a3'),
 'envelope_state':('resident_driver_544C','move.b $1e(a0),d0'),
 'envelope_cursor':('resident_driver_544C','move.b $1f(a0),d3'),
 'envelope_step':('resident_driver_544C','add.b $20(a0),d0'),
 'envelope_target':('resident_driver_544C','cmp.b $21(a0),d0'),
 'volume':('resident_driver_544C','move.b $22(a0),d2'),
 'transpose':('resident_asm_59A4','add.b $23(a0),d0'),
 'return_depth':('resident_driver_5CC6','addq.b #$1,$24(a0)'),
 'vibrato_shift':('resident_asm_59A4','move.b $25(a0),d3'),
 'sample_data':('resident_driver_5A50','movea.l $26(a0),a2'),
 'vibrato_delay_reload':('resident_driver_5A50','move.b $37(a0),$38(a0)'),
 'vibrato_delay':('resident_driver_58BC','subq.b #$1,$38(a0)'),
 'dma_pending':('resident_driver_58BC','tst.b $39(a0)'),
 'sample_bank':('resident_asm_59A4','add.b $3a(a0),d0'),
 'priority':('resident_driver_57E4','move.b d1,$3b(a1)'),
 'default_envelope':('resident_driver_5A50','move.l $3c(a0),d0'),
 'alternate_envelope':('resident_driver_544C','move.l $40(a0),d0'),
 'gate_ticks':('resident_driver_58BC','move.b $44(a0),d0'),
 'volume_reduction_45':('resident_driver_544C','sub.b $45(a0),d2'),
 'volume_reduction_46':('resident_driver_544C','sub.b $46(a0),d2'),
 'tick_phase':('resident_driver_58BC','add.b d0,$48(a0)'),
 'tick_rate':('resident_driver_58BC','move.b $49(a0),d0')}
GLOBALS={
 'vibrato_flags':(0x2a0a,'unsigned char','resident_asm_59A4','btst d7,_G_h01_2A0A'),
 'noise_word':(0x2b86,'unsigned short','resident_driver_5D92','move.w _G_h01_2B86,d0'),
 'rng_byte':(0x2b89,'unsigned char','resident_asm_559E','lea _G_h01_2B89,a0'),
 'rng_word':(0x2b8a,'unsigned short','resident_asm_559E','lea _G_h01_2B8A,a1'),
 'master_attenuation':(0x2b8c,'unsigned char','resident_driver_544C','sub.b _G_h01_2B8C,d2'),
 'output_enable':(0x2b8d,'unsigned char','resident_driver_544C','tst.b _G_h01_2B8D'),
 'palette_ticks':(0x2c2a,'unsigned char','resident_callback_61A0','sub.b d0,_G_h01_2C2A'),
 'palette_cursor':(0x2c2b,'unsigned char','resident_callback_61A0','move.b d0,_G_h01_2C2B')}
WIDTHS={'char':1,'unsigned char':1,'int':2,'unsigned short':2,'unsigned int':2,'long':4,'unsigned long':4,'unsigned char *':4,'char *':4,'struct GameAudioSample *':4}

def shape(f):
    require(set(f)=={'schema_version','kind','id','source','original','definitions','route','selector_index','field','data_model_sha256','anchors','object_sections','historical_owner','historical_tu','original_filename','producer'},'audio field fact fields')
    o=f['original'];route=f['route'];ds=f['definitions'];index=f['selector_index']
    require(f['schema_version']==1 and f['kind']=='BOUNDED_DATA_TABLE' and route in ROUTES and o['hunk']==1 and set(o)=={'hunk','start','size'} and type(o['start']) is int and o['start']>=0x320,'closed initialized audio field')
    require(f['id']=='resident_data_%04X'%o['start'] and f['source']=='src/recovered/data/'+f['id']+'.c','audio field identity')
    require(f['historical_owner']==f['historical_tu']=='UNKNOWN' and f['original_filename'] is None,'unknown original provenance')
    require(isinstance(f['anchors'],dict) and f['anchors'] and isinstance(ds,list) and len(ds)==1 and type(index) is int,'one independently bounded field')
    d=ds[0];require(set(d)=={'symbol','type','offset','dimensions','initializer','bounds'} and d['symbol']=='G_h01_%04X'%o['start'] and d['offset']==0 and d['dimensions']==[] and d['type'] in WIDTHS,'typed scalar field, never channel carrier')
    ty=d['type'];size=WIDTHS[ty];v=d['initializer']
    if ty.endswith('*'):require(v is None,'only typed null pointers; numeric addresses reject')
    else:require(type(v) is int and (0 if ty.startswith('unsigned') else -(1<<(size*8-1)))<=v<(1<<(size*8-(0 if ty.startswith('unsigned') else 1))),'strict audio scalar range')
    if route=='AUDIO_CHANNEL_FIELD':require(0<=index<4 and f['field'] in CHANNEL,'four-channel field witness')
    elif route=='AUDIO_IRQ_FIELD':require(0<=index<4 and f['field'] in ('countdown','cursor') and o['start']==0x2b4e+index*8+(4 if f['field']=='cursor' else 0) and ty==('int' if f['field']=='countdown' else 'struct GameAudioSample *'),'IRQ known word/pointer only; +2 word stays raw')
    elif route=='AUDIO_GLOBAL_CELL':require(index==0 and f['field'] in GLOBALS and (o['start'],ty)==GLOBALS[f['field']][:2],'exact audio scalar identity')
    else:require(0<=index<12 and f['field']=='period' and ty=='unsigned short' and o['start']==0x29de+index*2,'individual note-period WORD cell')
    require(type(o['size']) is int and o['size']==size and d['bounds']==dict(kind=route,bytes=size) and f['object_sections']==dict(CODE=0,DATA=(size+1)&~1,BSS=0,COMMON=0),'full typed scalar object, no filler credit')
    return size

def source(f):
    shape(f);d=f['definitions'][0];v=d['initializer'];ty=d['type'];header='struct GameAudioSample;\n' if ty.startswith('struct ') else ''
    return (header+ty+' '+d['symbol']+' = '+('0' if ty.endswith('*') else str(v)+('L' if ty.endswith('long') else ''))+';\n').encode('ascii')

def semantic(f):
    size=shape(f);d=f['definitions'][0];return bytes(size) if d['type'].endswith('*') else (d['initializer']%(1<<(size*8))).to_bytes(size,'big')

def evidence_paths(root,f):
    from data_provider_sequences import evidence_paths as paths
    return sorted(set(paths(root,f)+['recovery/data_model.json']))

def typed_evidence(root,f,analysis,ledger,promotions):
    from data_provider_tables import fragments
    from data_providers import document
    from census import advisory_image
    from game_image import game
    shape(f);a=anchors(root,f,analysis,ledger,promotions);route=f['route'];index=f['selector_index'];d=f['definitions'][0];field=f['field'];o=f['original']
    raw=canonical_path(root,'recovery/data_model.json').read_bytes();require(sha256(raw)==f['data_model_sha256'],'stale curated audio interpretation');dm=json.loads(raw)
    with advisory_image():blob,model,_=game()
    if route=='AUDIO_CHANNEL_FIELD':
        fid,operand=CHANNEL[field];require(set(a)=={fid,'resident_driver_58BC'},'channel field/selector anchors')
        fragments(a['resident_driver_58BC'][0],'moveq #$3,d7','lsl.l #$2,d0','lea _G_h01_29FA,a0','movea.l 0(a0,d0.l),a0','dbra d7,_recon_h00_58CA')
        fragments(a[fid][0],operand)
        rec=next(x for x in dm['structs']['GameAudioChannel']['fields'] if x['name']==field)
        require(rec['type']==d['type'] and rec['type']!='UNKNOWN','field type disagrees with independently interpreted consumer')
        offsets=re.findall(r'\$([0-9a-f]+)\(a[01]\)',operand)
        offset=int(offsets[0],16) if offsets else 0
        width={'b':1,'w':2,'l':4}[operand.split()[0][-1]]
        require(rec['offset']==offset and WIDTHS[d['type']]==width,'curated field offset/width not rederived from named ASM operand')
        base=pointer_target(blob,model,0x29fa,index);require(o['start']==base+rec['offset'],'channel field base/offset differs')
        details=dict(channel=index,base=base,field=field,field_offset=rec['offset'],type=d['type'],operand=operand,channel_extent='UNKNOWN',channel_stride='UNKNOWN',capacity_claim=False)
    elif route=='AUDIO_IRQ_FIELD':
        fid=['resident_frameless_55D6','resident_frameless_5646','resident_frameless_56B6','resident_frameless_5726'][index]
        require(set(a)=={fid,'resident_asm_59A4','resident_driver_58BC'},'IRQ row and channel-domain anchors')
        fragments(a['resident_driver_58BC'][0],'moveq #$3,d7','dbra d7,_recon_h00_58CA')
        fragments(a['resident_asm_59A4'][0],'move.w d7,d3','lsl.w #3,d3','lea _G_h01_2B4E,a2','adda.w d3,a2','move.l a4,4(a2)')
        if field=='countdown':fragments(a[fid][0],'subq.w #$1,_G_h01_%04X'%o['start'])
        else:fragments(a[fid][0],'movea.l _G_h01_%04X,a0'%o['start'],'move.l a0,_G_h01_%04X'%o['start'])
        require(dm['globals'][d['symbol']]['type']==d['type'] and dm['globals'][d['symbol']]['extent']==o['size'],'IRQ typed cell interpretation changed')
        details=dict(channel=index,field=field,record_stride=8,unknown_word_offset=2,capacity_claim=False)
    elif route=='AUDIO_GLOBAL_CELL':
        at,ty,fid,operand=GLOBALS[field];require(set(a)=={fid},'one direct audio scalar witness');fragments(a[fid][0],operand)
        if field=='rng_byte':fragments(a[fid][0],'move.b (a0),d0','move.b d0,(a0)')
        if field=='rng_word':fragments(a[fid][0],'roxr.w (a1)')
        details=dict(field=field,type=ty,operand=operand,scalar_width=o['size'])
    else:
        require(set(a)=={'resident_driver_57E4','resident_asm_59A4'},'note reset and WORD reader')
        fragments(a['resident_driver_57E4'][0],'clr.w $12(a1)')
        fragments(a['resident_asm_59A4'][0],'clr.l d1','move.b d0,d1','and.b #$f,d1','add.b $12(a0),d1','cmp.b #$b,d1','ble _L59C6','sub.b #$c,d1','lsl.w #1,d1','lea _G_h01_29DE,a2','move.w 0(a2,d1.w),d1','move.w d1,6(a3)')
        domain={x if x<=11 else x-12 for x in range(16)};require(domain==set(range(12)) and index in domain,'conditional period-index domain differs')
        details=dict(index=index,element_width=2,condition='note_offset==0 after canonical reset',full_period_table_extent='UNKNOWN',index44_dispatch_alias='29DE first two period WORDs; not a code pointer')
    return [dict(kind=route,anchors=f['anchors'],data_model_sha256=f['data_model_sha256'],details=details,historical_extent='complete reconstructed scalar provider; historical aggregate extent unknown')]

def compare_data(original,model,f,obj,linked,map_text):
    from data_provider_tables import numeric_compare
    return numeric_compare(original,model,f,obj,linked,map_text,shape(f),semantic(f),source(f))
