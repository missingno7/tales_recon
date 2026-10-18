"""Synthetic type, bounds and complete-object invariants; no corpus counts."""
import copy
import struct
import sys
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import data_provider_tables as t
import data_providers as dp
from common import FormatError,sha256
from hunk import parse


def fact(route='PALETTE_FADE32'):
    cases={
        'PALETTE_FADE32':(0x200,'unsigned int',[32],list(range(32)),64),
        'CREDIT_TEXT_ROWS':(0x6fe,'char',[24,26],[' '*25]*24,624),
        'TILE_CHARACTER_ROWS':(0xac4,'char',[25,21],['F'*20]*25,525),
        'LEVEL_ENTRY_ROWS':(0x10f2,'struct DP_LevelEntry',[25],[dict(kind=1,active=0,pos=-2,t=3) for _ in range(25)],150),
        'RENDERED_C_STRING':(0x68b,'char',[3],'AB',3),
        'COORDINATE_PAIRS':(0x200,'short',[4],[-1,2,3,-4],8),
        'STOCK_EVENT_MASKS':(0x468,'unsigned char',[14],[1]*14,14),
        'ADPCM_TABLES':(0x1e32,'int',[8],[-1]*8,16)}
    start,ty,dims,values,size=cases[route];ident='resident_data_%04X'%start
    ds=[dict(symbol='G_h01_%04X'%start,type=ty,offset=0,dimensions=dims,initializer=values,bounds=dict(kind=route,bytes=size))]
    if route=='ADPCM_TABLES':
        ds.append(dict(symbol='G_h01_1E42',type='int',offset=16,dimensions=[49],initializer=list(range(49)),bounds=dict(kind=route,bytes=98)));size=114
    return dict(schema_version=1,kind=t.KIND,id=ident,source='src/recovered/data/'+ident+'.c',original=dict(hunk=1,start=start,size=size),route=route,definitions=ds,anchors={'consumer':dict(source_sha256='a'*64,proof_sha256='b'*64)},object_sections=dict(CODE=0,DATA=(size+1)&~1,BSS=0,COMMON=0),historical_owner='UNKNOWN',historical_tu='UNKNOWN',original_filename=None,producer=dict(batch='evidence/data-providers/producer-9999.json',prefix='test',profile='aztec36'))


def aj(data=b'AB\0',declared=4,name='_DP_odd',code=0,bss=0):
    stream=b'\xf5'+bytes([15+len(data)])+data+b'\xf4\xf5';stream+=bytes((-len(stream))%4)
    names=b'\x03\x0a\0\0'+name.encode()+b'\0';names+=bytes((-len(names))%4)
    h=bytearray(36);h[:2]=b'AJ'
    for off,v in ((10,code),(14,declared),(18,bss),(24,9)):h[off:off+4]=v.to_bytes(4,'big')
    for off,v in ((22,1),(28,(36+len(stream))//4),(30,(36+len(stream)+len(names))//4),(32,(36+len(stream)+len(names))//4)):h[off:off+2]=v.to_bytes(2,'big')
    h[34:36]=b'\xc0\0';return bytes(h)+stream+names


def executable(data=b'AB\0\0'):
    words=[1011,0,3,0,2,1,len(data)//4,1,1001,1]
    return struct.pack('>'+str(len(words))+'I',*words)+b'\x4e\x75\0\0'+struct.pack('>III',1010,1002,len(data)//4)+data+struct.pack('>IIII',1010,1003,1,1010)


MAP='''Segment 00:  Hunk 000
\t00000000 __H0_org
\t00000000 .begin
\t00000004 __H0_end
Segment 00:  Hunk 001
\t00000000 __H1_org
\t00000000 _DP_odd
\t00000004 __H1_end
Segment 00:  Hunk 002
\t00000004 __H2_org
\t00000004 __H2_end
'''


class TableShapeTests(unittest.TestCase):
    def test_routes_emit_only_complete_typed_values(self):
        for route in t.ROUTES:
            with self.subTest(route=route):
                f=fact(route);self.assertEqual(len(t.semantic(f)),t.shape(f));self.assertNotIn(b'\r',t.source(f));self.assertTrue(t.source(f).endswith(b'\n'))

    def test_unknown_fact_or_padding_fields_reject(self):
        for key in ('bytes_hex','padding','mask'):
            f=fact();f[key]='00'
            with self.assertRaises(FormatError):t.shape(f)

    def test_byte_carrier_cannot_replace_palette_words(self):
        f=fact();f['definitions'][0]['type']='unsigned char'
        with self.assertRaises(FormatError):t.shape(f)

    def test_extents_dimensions_sections_and_offsets_reject_mutations(self):
        for route in t.ROUTES:
            for key in ('extent','dimension','bounds','offset','DATA','CODE','BSS','COMMON'):
                with self.subTest(route=route,key=key):
                    f=fact(route);d=f['definitions'][0]
                    if key=='extent':f['original']['size']+=2
                    elif key=='dimension':d['dimensions'][0]+=1
                    elif key=='bounds':d['bounds']['bytes']+=1
                    elif key=='offset':d['offset']+=2
                    else:f['object_sections'][key]+=2
                    with self.assertRaises(FormatError):t.shape(f)

    def test_palette_range_and_strict_integer_type(self):
        for value in (-1,4096,True,1.0,'1'):
            f=fact();f['definitions'][0]['initializer'][0]=value
            with self.assertRaises(FormatError):t.shape(f)

    def test_grid_cannot_hide_bytes_or_wrong_character_width(self):
        for text in ('F'*19,'F'*21,'F'*19+'\0','F'*19+'\x01','F'*19+'A'):
            f=fact('TILE_CHARACTER_ROWS');f['definitions'][0]['initializer'][0]=text
            with self.assertRaises(FormatError):t.shape(f)

    def test_entry_fields_have_no_untyped_holes(self):
        for mutation in ('padding','missing','wide','unsigned'):
            f=fact('LEVEL_ENTRY_ROWS');row=f['definitions'][0]['initializer'][0]
            if mutation=='padding':row['padding']=0
            elif mutation=='missing':del row['t']
            elif mutation=='wide':row['pos']=32768
            else:row['active']=-1
            with self.assertRaises(FormatError):t.shape(f)

    def test_odd_character_address_and_implicit_nul(self):
        f=fact('RENDERED_C_STRING');self.assertEqual(t.shape(f),3);self.assertEqual(t.source(f),b'char G_h01_068B[] = "AB";\n');self.assertEqual(t.semantic(f),b'AB\0')

    def test_explicit_string_nul_cannot_hide_a_tail(self):
        f=fact('RENDERED_C_STRING');f['definitions'][0]['initializer']='A\0B'
        with self.assertRaises(FormatError):t.shape(f)

    def test_word_alignment_and_signed_coordinates(self):
        f=fact();f['original']['start']+=1
        with self.assertRaises(FormatError):t.shape(f)
        self.assertEqual(t.semantic(fact('COORDINATE_PAIRS')),b'\xff\xff\0\2\0\3\xff\xfc')


class BoundWitnessTests(unittest.TestCase):
    def anchors(self):
        src=b'int recovered() { return 1; }\n';pr=b'{}';pins=dict(source_sha256=sha256(src),proof_sha256=sha256(pr))
        f=fact();f['anchors']={'consumer':pins};ledger=dict(functions={'consumer':dict(source='a.c',proof='p.json',**pins)});analysis=dict(functions=[dict(id='consumer')]);files={'a.c':src,'p.json':pr}
        return f,ledger,analysis,files

    def test_current_source_and_proof_pins_are_mandatory(self):
        f,l,a,files=self.anchors()
        with patch.object(t,'canonical_path',side_effect=lambda r,n:SimpleNamespace(read_bytes=lambda:files[n])), \
             patch.object(t,'read_source',side_effect=lambda r,n,**kwargs:files[n]):
            self.assertIn('consumer',t.canonical_anchors(None,f,a,l,[dict(id='consumer')]))
            for name in files:
                old=files[name];files[name]=old+b' '
                with self.assertRaises(FormatError):t.canonical_anchors(None,f,a,l,[dict(id='consumer')])
                files[name]=old
            with self.assertRaises(FormatError):t.canonical_anchors(None,f,a,l,[])

    def test_changed_instruction_width_or_bound_rejects(self):
        f=dict(instructions=[dict(offset=4,mnemonic='move.w',operands='(a0), d0')])
        t.instruction(f,4,'move.w','(a0), d0')
        for m,o in [('move.b','(a0), d0'),('move.w','(a1), d0')]:
            with self.assertRaises(FormatError):t.instruction(f,4,m,o)

    def test_named_bound_address_and_zero_addend_are_mandatory(self):
        address=0x200;i=dict(offset=10,size=4,mnemonic='lea.l',raw='41ec'+(address-32766).to_bytes(2,'big',signed=True).hex());identity=dict(symbol='_table',hunk=1,offset=address,addend=0)
        b=dict(kind='A4_D16_SYMBOL',offset=12,identity=identity);p=dict(comparison=dict(relocation_proof=[b]));f=dict(start=0,instructions=[i]);anchor=('',p,f)
        self.assertEqual(t.binding(anchor,'table',address),[10])
        for key,value in [('symbol','_other'),('hunk',0),('offset',address+2),('addend',2)]:
            old=identity[key];identity[key]=value
            with self.assertRaises(FormatError):t.binding(anchor,'table',address)
            identity[key]=old


class CompleteObjectTests(unittest.TestCase):
    def test_default_parser_keeps_its_strict_extent(self):
        with self.assertRaises(FormatError):dp.data_object(aj())
        self.assertEqual(dp.data_object(aj(),terminal_padding=1)['bytes'],b'AB\0\0')

    def test_padding_is_not_a_general_fill_option(self):
        for n in (True,-1,2,4):
            with self.assertRaises(FormatError):dp.data_object(aj(),terminal_padding=n)
        with self.assertRaises(FormatError):dp.data_object(aj(b'AB\0\0'),terminal_padding=1)

    def test_hidden_sections_and_partial_data_reject(self):
        for kwargs in (dict(code=2),dict(bss=2),dict(declared=6)):
            with self.assertRaises(FormatError):dp.data_object(aj(**kwargs),terminal_padding=1)

    def test_full_object_and_link(self):
        p=t.linked_data(aj(),executable(),MAP,[dict(name='_DP_odd',offset=0)],b'AB\0',dict(CODE=0,DATA=4,BSS=0,COMMON=0));self.assertEqual(p['bytes'],b'AB\0\0')

    def test_changed_payload_or_extra_symbol_rejects(self):
        for exe,map_text in [(executable(b'AB\0\1'),MAP),(executable(),MAP.replace('\t00000004 __H1_end','\t00000002 _extra\n\t00000004 __H1_end'))]:
            with self.assertRaises(FormatError):t.linked_data(aj(),exe,map_text,[dict(name='_DP_odd',offset=0)],b'AB\0',dict(CODE=0,DATA=4,BSS=0,COMMON=0))

    def test_original_cross_boundary_relocation_rejects(self):
        f=fact('RENDERED_C_STRING');blob=executable();model=parse(blob);model['relocations']=[dict(source_hunk=1,source_offset=0x68a,width=4)]
        with patch.object(t,'linked_data',return_value=dict(sections=f['object_sections'])),patch.object(t,'payload',return_value=bytes(0x68b)+b'AB\0'):
            with self.assertRaisesRegex(FormatError,'relocation'):t.compare_data(blob,model,f,b'',blob,MAP)


if __name__=='__main__':unittest.main()
