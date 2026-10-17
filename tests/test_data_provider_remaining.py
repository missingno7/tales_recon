"""Synthetic closed bounds, typed sentinels, FFP and named DATA relocation tests."""
import copy,struct,sys,unittest,tempfile,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import FormatError
import data_provider_more as more
import data_provider_sequences as seq
import data_provider_cells as cells
import data_provider_audio_fields as audio
import data_providers as dp
import data_provider_job as jobgen
import data_provider_locrows as loc
from types import SimpleNamespace


def fact(route='ASSET_ID_PROGRAM'):
    at=0x1f38;ty='unsigned char';dims=[3];value=[4,5,255];size=3
    if route=='SAMPLE_RECORD_PREFIX':at=0x206c;ty='struct DP_Sequence';dims=[];value=dict(records=[dict(duration=1,length_words=12,sample_data=None)],terminal_duration=-32768);size=10
    f=dict(schema_version=1,kind='BOUNDED_DATA_TABLE',id='resident_data_%04X'%at,source='src/recovered/data/resident_data_%04X.c'%at,original=dict(hunk=1,start=at,size=size),route=route,selector_index=0,definitions=[dict(symbol='G_h01_%04X'%at,type=ty,offset=0,dimensions=dims,initializer=value,bounds=dict(kind=route,bytes=size))],anchors={'consumer':dict(source_sha256='a'*64,proof_sha256='b'*64)},object_sections=dict(CODE=0,DATA=(size+1)&~1,BSS=0,COMMON=0),historical_owner='UNKNOWN',historical_tu='UNKNOWN',original_filename=None,producer=dict(batch='evidence/data-providers/producer-9999.json',prefix='test',profile='aztec36'))
    return f


def pointer_fact():
    f=fact();f.pop('route');f.pop('selector_index');f.pop('anchors');f['kind']=cells.KIND;at=0x1f9e;f['id']='resident_data_1F9E';f['source']='src/recovered/data/'+f['id']+'.c';f['original']=dict(hunk=1,start=at,size=4);f['object_sections']['DATA']=4
    f['target_fact']='evidence/data-providers/resident_data_1F38.json';f['target_fact_sha256']='a'*64
    f['definitions']=[dict(symbol='G_h01_1F9E',type='unsigned char *',offset=0,target='G_h01_1F38',target_type='unsigned char',target_count=3,target_offset=0x1f38,selector_index=0,bounds=dict(kind='NAMED_DATA_POINTER_CELL',bytes=4))]
    return f


def aj_pointer(symbol='_DP_p',targets=('_DP_a','_DP_b','_DP_a')):
    names=list(dict.fromkeys(targets));stream=bytearray(b'\xf5')
    for n in targets:stream+=bytes((0xfd,0x71+names.index(n),0))
    stream+=b'\xf4\xf5';stream+=bytes((-(36+len(stream))-1)%4+1)
    syms=b'\x03\x0a\0\0'+symbol.encode()+b'\0'
    for n in names:syms+=b'\x07\x2a\0\0'+targets.count(n).to_bytes(2,'big')+n.encode()+b'\0'
    syms+=bytes((-len(syms))%4);h=bytearray(36);h[:2]=b'AJ';h[34:36]=b'\xc0\0'
    for at,v in ((10,0),(14,4*len(targets)),(18,0),(24,9)):h[at:at+4]=v.to_bytes(4,'big')
    for at,v in ((22,1+len(names)),(28,(36+len(stream))//4),(30,(36+len(stream)+len(syms))//4),(32,(36+len(stream)+len(syms))//4)):h[at:at+2]=v.to_bytes(2,'big')
    return bytes(h)+stream+syms


def link(symbol='_DP_p',targets=('_DP_a','_DP_b','_DP_a'),names=('_DP_a','_DP_b')):
    size=4*len(targets);binder=b''.join((i+1).to_bytes(2,'big') for i in range(len(names)));data=b''.join((size+2*names.index(n)).to_bytes(4,'big') for n in targets)+binder;data+=bytes((-len(data))%4);rounded=len(data)
    words=lambda *v:struct.pack('>'+str(len(v))+'I',*v)
    blob=words(1011,0,3,0,2,1,rounded//4,1,1001,1)+b'\x4e\x75\0\0'+words(1010,1002,rounded//4)+data+words(1004,len(targets),1,*range(0,size,4),0,1010,1003,1,1010)
    groups=[{'.begin':0,'__H0_org':0,'__H0_end':4},{'__H1_org':0,symbol:0,'__H1_end':rounded,**{n:size+2*i for i,n in enumerate(names)}},{'__H2_org':rounded,'__H2_end':rounded}]
    text=''.join('Segment 00:  Hunk %03d\n'%i+''.join('\t%08x %s\n'%(at,n) for n,at in g.items()) for i,g in enumerate(groups))
    return blob,text


class TypedRemainingData(unittest.TestCase):
    def test_missing_frame_pair_cannot_be_silently_filled(self):
        f=fact();f.pop('selector_index');f.update(id='resident_data_060A',source='src/recovered/data/resident_data_060A.c',route='FRAME_COORDINATES',original=dict(hunk=1,start=0x60a,size=28));f['object_sections']['DATA']=28
        f['definitions']=[dict(symbol='G_h01_060A',type='short',offset=0,dimensions=[14],initializer=[0]*14,bounds=dict(kind='FRAME_COORDINATES',bytes=28))]
        with self.assertRaises(FormatError):more.shape(f)
        f['original']['size']=4;f['object_sections']['DATA']=4;f['definitions'][0].update(dimensions=[2],initializer=[1,-2],bounds=dict(kind='FRAME_COORDINATES',bytes=4))
        self.assertEqual(more.shape(f),4)
        f['original']['start']=0x60e;f['id']='resident_data_060E';f['source']='src/recovered/data/resident_data_060E.c';f['definitions'][0]['symbol']='G_h01_060E'
        with self.assertRaises(FormatError):more.shape(f)

    def test_unknown_direction_is_only_accepted_for_decoded_word_compare_read(self):
        self.assertTrue(more.scalar_access(dict(direction='UNKNOWN',mnemonic='cmp.w',width_bytes=2),2))
        for mnemonic,width in [('lea.l',4),('cmp.l',4),('tst.w',2),('cmp.b',1)]:
            self.assertFalse(more.scalar_access(dict(direction='UNKNOWN',mnemonic=mnemonic,width_bytes=width),width))
        self.assertFalse(more.scalar_access(dict(direction='UNKNOWN',mnemonic='cmp.w',width_bytes=2),1))

    def test_decimal_ffp_values_and_sign_have_exact_math_encoding(self):
        for v,w in [('0.0','00000000'),('1.0','80000041'),('-1.0','800000c1'),('0.9','e6666640'),('0.4','cccccd3f'),('-0.7','b33333c0')]:
            with self.subTest(v=v):self.assertEqual(more.ffp(v).hex(),w)

    def test_float_initializer_is_finite_decimal_source(self):
        for v in [1.0,True,'NaN','Inf','0x80000041','1e999','1','']:
            with self.subTest(v=v),self.assertRaises(FormatError):more.ffp(v)

    def test_asset_program_includes_first_sentinel_and_no_padding(self):
        f=fact();self.assertEqual(seq.semantic(f),bytes((4,5,255)));self.assertEqual(seq.shape(f),3);self.assertEqual(f['object_sections']['DATA'],4)
        self.assertIn(b'unsigned char G_h01_1F38[3]',seq.source(f));self.assertNotIn(b'bytes_hex',seq.source(f))
        for vals in ([4,255,5,255],[4,5],[256,255],[True,255]):
            x=copy.deepcopy(f);x['definitions'][0]['initializer']=vals
            with self.assertRaises(FormatError):seq.shape(x)

    def test_terminal_descriptor_credits_only_consumed_duration_word(self):
        f=fact('SAMPLE_RECORD_PREFIX');self.assertEqual(seq.shape(f),10);self.assertEqual(seq.semantic(f),bytes.fromhex('0001000c000000008000'))
        self.assertIn(b'int terminal_duration;',seq.source(f));self.assertNotIn(b'char [',seq.source(f));self.assertNotIn(b'padding',seq.source(f))
        for mode in ('tail','null_integer','positive_terminal','negative_record','missing_field'):
            x=copy.deepcopy(f);d=x['definitions'][0];v=d['initializer']
            if mode=='tail':x['original']['size']+=6;x['object_sections']['DATA']+=6;d['bounds']['bytes']+=6
            elif mode=='null_integer':v['records'][0]['sample_data']=0
            elif mode=='positive_terminal':v['terminal_duration']=1
            elif mode=='negative_record':v['records'][0]['duration']=-1
            else:del v['records'][0]['length_words']
            with self.subTest(mode=mode),self.assertRaises(FormatError):seq.shape(x)

    def test_opaque_extra_fields_wrong_extent_and_code_common_reject(self):
        for mode in ('bytes_hex','mask','padding','extent','CODE','BSS','COMMON'):
            f=fact()
            if mode in ('bytes_hex','mask','padding'):f[mode]='00'
            elif mode=='extent':f['definitions'][0]['dimensions'][0]+=1
            else:f['object_sections'][mode]+=2
            with self.subTest(mode=mode),self.assertRaises(FormatError):seq.shape(f)

    def test_pointer_initializer_uses_a_named_typed_object(self):
        f=pointer_fact();src=cells.source(f);self.assertIn(b'extern unsigned char G_h01_1F38[3];',src);self.assertIn(b'= G_h01_1F38;',src);self.assertNotIn(b'0x',src);self.assertEqual(dp.source(f),src)
        for mode in ('integer','unbound','extra','extent','index'):
            x=copy.deepcopy(f);d=x['definitions'][0]
            if mode=='integer':d['target']=0x1f38
            elif mode=='unbound':x['target_fact']='evidence/data-providers/resident_data_1F39.json'
            elif mode=='extra':d['initializer']=0
            elif mode=='extent':x['original']['size']=8
            else:d['selector_index']=1
            with self.subTest(mode=mode),self.assertRaises(FormatError):cells.shape(x)

    def test_channel_pointer_binds_named_first_field_without_channel_carrier(self):
        f=pointer_fact();f.update(id='resident_data_29FA',source='src/recovered/data/resident_data_29FA.c',original=dict(hunk=1,start=0x29fa,size=4),target_fact='evidence/data-providers/resident_data_2A12.json');d=f['definitions'][0];d.update(symbol='G_h01_29FA',type='struct DP_Channel *',target='G_h01_2A12',target_type='unsigned long',target_count=1,target_offset=0x2a12)
        src=cells.source(f);self.assertIn(b'(struct DP_Channel *)&G_h01_2A12;',src);self.assertNotIn(b'[76]',src);self.assertNotIn(b'char reserved',src)

    def test_period_words_are_scalar_data_and_never_dispatch_pointer45(self):
        f=fact();f.pop('selector_index');f['route']='AUDIO_PERIOD_WORD';f['selector_index']=0;f['field']='period';f['data_model_sha256']='a'*64;f['id']='resident_data_29DE';f['source']='src/recovered/data/resident_data_29DE.c';f['original']=dict(hunk=1,start=0x29de,size=2);f['object_sections']['DATA']=2;f['definitions']=[dict(symbol='G_h01_29DE',type='unsigned short',offset=0,dimensions=[],initializer=428,bounds=dict(kind='AUDIO_PERIOD_WORD',bytes=2))]
        self.assertEqual(audio.semantic(f),bytes.fromhex('01ac'));self.assertNotIn(b'*',audio.source(f))
        f['definitions'][0]['type']='char *';f['definitions'][0]['initializer']=None
        with self.assertRaises(FormatError):audio.shape(f)


class ArchiveRowBounds(unittest.TestCase):
    def test_selector_domain_comes_from_independent_decoded_word_fields(self):
        entries=[SimpleNamespace(kind=4,record_output=('1 2 %d 3\ntext\n'%(16*n+4)).encode('ascii')) for n in range(1,7)]
        entries.append(SimpleNamespace(kind=4,record_output=b'1 2 8 3\ntext\n'))
        rows=loc.selector_rows(entries);self.assertEqual({x['argument'] for x in rows},set(range(1,7)))
        for payload,kind in [(b'1 2 20\n',4),(b'1 2 20 3 junk\n',4),(b'1 2 65536 3\n',4),(b'1 2 20 3\n',3)]:
            with self.assertRaises(FormatError):loc.selector_rows([SimpleNamespace(kind=kind,record_output=payload)])

    def test_only_typed_six_by_five_option_words_are_emitted(self):
        f=fact();f.pop('selector_index');f.update(id='resident_data_12C0',source='src/recovered/data/resident_data_12C0.c',route='LOCATION_OPTION_ROWS',original=dict(hunk=1,start=0x12c0,size=60));f['object_sections']['DATA']=60
        f['definitions']=[dict(symbol='G_h01_12C0',type='int',offset=0,dimensions=[6,5],initializer=[[row*5+col for col in range(5)] for row in range(6)],bounds=dict(kind='LOCATION_OPTION_ROWS',bytes=60))]
        self.assertEqual(len(more.semantic(f)),60);self.assertIn(b'int G_h01_12C0[6][5]',more.source(f))
        for mode in ('capacity32','columns','byte_carrier','padding','float'):
            x=copy.deepcopy(f);d=x['definitions'][0]
            if mode=='capacity32':d['dimensions'][0]=32
            elif mode=='columns':d['dimensions'][1]=6
            elif mode=='byte_carrier':d['type']='char'
            elif mode=='padding':d['initializer'][0].append(0)
            else:d['initializer'][0][0]=1.0
            with self.subTest(mode=mode),self.assertRaises(FormatError):more.shape(x)


class RegenerationRecipe(unittest.TestCase):
    def test_windows_mount_recipe_and_request_pin_are_normalized_together(self):
        from common import json_bytes,sha256
        with tempfile.TemporaryDirectory() as directory:
            job=Path(directory);raw=b'filesystem2=rw,DH0:Worker:D:\\test\\sys,0\r\n'
            (job/'worker.uae').write_bytes(raw);(job/'request.json').write_bytes(json_bytes(dict(config_sha256='old',source_files=[dict(path='test.c',sha256='a'*64)])))
            jobgen.normalize_config(job);expected=b'filesystem2=rw,DH0:Worker:D:/test/sys,0\n'
            self.assertEqual((job/'worker.uae').read_bytes(),expected)
            request=json.loads((job/'request.json').read_bytes());self.assertEqual(request['config_sha256'],sha256(expected));self.assertEqual(request['source_files'],[dict(path='test.c',sha256='a'*64)])
            jobgen.normalize_config(job);self.assertEqual((job/'worker.uae').read_bytes(),expected)


class NamedDataObject(unittest.TestCase):
    def test_complete_data_external_control_with_duplicate_references(self):
        p=cells.object_data(aj_pointer(),'_DP_p',['_DP_a','_DP_b','_DP_a']);self.assertEqual(p['sections'],dict(CODE=0,DATA=12,BSS=0,COMMON=0));self.assertEqual([x['symbol'] for x in p['fixups']],['_DP_a','_DP_b','_DP_a'])
        exe,sm=link();p,model,data=cells.linked_view(aj_pointer(),exe,sm,'_DP_p',['_DP_a','_DP_b','_DP_a'],['_DP_a','_DP_b']);self.assertEqual(data,bytes.fromhex('0000000c0000000e0000000c'))

    def test_one_scalar_pointer_uses_same_measured_grammar(self):
        raw=aj_pointer('_DP_cell',['_DP_a']);exe,sm=link('_DP_cell',['_DP_a'],['_DP_a','_DP_b']);p,m,data=cells.linked_view(raw,exe,sm,'_DP_cell',['_DP_a'],['_DP_a','_DP_b']);self.assertEqual(p['sections']['DATA'],4);self.assertEqual(data,bytes.fromhex('00000004'))

    def test_aj_external_class_reference_count_index_and_object_sections_are_exact(self):
        for mode in ('CODE_external','reference_count','index','addend','CODE','BSS','trailer','symbol_value'):
            raw=bytearray(aj_pointer());p=raw.index(b'\x07\x2a')
            if mode=='CODE_external':raw[p+1]=0x28
            elif mode=='reference_count':raw[p+5]+=1
            elif mode=='index':raw[38]=0x73
            elif mode=='addend':raw[39]=1
            elif mode=='CODE':raw[13]=2
            elif mode=='BSS':raw[21]=2
            elif mode=='trailer':raw+=b'\0\0\0\0'
            else:raw[p+3]=2
            with self.subTest(mode=mode),self.assertRaises(FormatError):cells.object_data(bytes(raw),'_DP_p',['_DP_a','_DP_b','_DP_a'])

    def test_whole_link_rejects_changed_binder_pointer_symbols_and_relocations(self):
        raw=aj_pointer();exe,sm=link();model=__import__('hunk').parse(exe);at=model['hunks'][1]['content_offset']
        for mode in ('pointer','binder','symbol','relocation','CODE'):
            b=bytearray(exe);text=sm
            if mode=='pointer':b[at+3]^=2
            elif mode=='binder':b[at+13]^=1
            elif mode=='symbol':text=text.replace('_DP_a','_DP_wrong')
            elif mode=='relocation':
                p=b.index((1004).to_bytes(4,'big'),at+16);b[p+11]=0
            else:b[model['hunks'][0]['content_offset']]^=2
            with self.subTest(mode=mode),self.assertRaises(FormatError):cells.linked_view(raw,bytes(b),text,'_DP_p',['_DP_a','_DP_b','_DP_a'],['_DP_a','_DP_b'])

    def test_synthetic_binder_has_no_game_bytes_and_needs_complete_unique_names(self):
        src=cells.binder_source(['_DP_a','_DP_b']);self.assertEqual(src,b'int DP_a = 1;\nint DP_b = 2;\n')
        for names in [['_DP_b','_DP_a'],['_DP_a','_DP_a'],['0x1f38']]:
            with self.assertRaises(FormatError):cells.binder_source(names)


if __name__=='__main__':unittest.main()
