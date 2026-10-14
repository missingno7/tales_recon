"""Natural library routes: complete members, all operands and retained producer."""
import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from common import FormatError, sha256
import runtime_natural_members as n
from analysis_support import game
RECIPE_FILE=ROOT/n.RECIPE


class NaturalMemberTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not RECIPE_FILE.exists():raise unittest.SkipTest('curated natural recipe is not installed')
        cls.recipe=json.loads(RECIPE_FILE.read_text())
        cls.original=game()[:2]
        cls.contexts=n.producer(ROOT,cls.recipe)
        cls.result=n.verify(ROOT,recipe=cls.recipe,original=cls.original)
        cls.result=dict(cls.result,contributions=[r for r in cls.result['contributions'] if r['member'] in n.LEGACY_MEMBERS])

    def prove(self,candidate=None,original=None):
        return n.prove_context(ROOT,self.recipe,candidate or self.contexts['natural'],original or self.original,self.contexts['crt'])

    def changed_code(self,member,field,value):
        b,m,sm=self.contexts['natural'];spec=n.SPECS[member]
        start=n.symbol(sm,spec['export'])[1]+spec['delta']
        h=next(h for h in m['hunks'] if h['number']==0)
        at=h['content_offset']+start+field
        out=bytearray(b);out[at:at+len(value)]=value
        return bytes(out),m,sm

    def test_complete_members_and_owned_format_data(self):
        self.assertEqual([(c['member'],c['size'],c['owned_data_size']) for c in self.result['contributions']],
                         [('wbparse',180,0),('format',936,18),('printf',28,0)])
        self.assertTrue(self.result['contributions'][2]['raw_equal'])
        self.assertEqual(self.result['contributions'][1]['owned_data']['original'],(1,0x2c64))
        self.assertEqual(self.result['contexts'][0]['identities']['_ctp_']['original'],(1,0x2c76))
        self.assertEqual(self.result['contexts'][0]['identities']['_Cbuffs']['original'],(1,0x2cf8))
        for member in self.result['contributions']:
            self.assertEqual(member['code_sha256'],sha256(n.extent(*self.original,0,member['original']['offset'],member['size'])))

    def test_all_external_fields_reject_wrong_displacement(self):
        for member in self.result['contributions']:
            for row in member['operand_identity']:
                if 'field' not in row:continue
                field=row['field'];b,m,sm=self.contexts['natural'];spec=n.SPECS[member['member']]
                start=n.symbol(sm,spec['export'])[1]+spec['delta'];raw=n.extent(b,m,0,start+field,2)
                changed=((int.from_bytes(raw,'big')+2)&65535).to_bytes(2,'big')
                with self.subTest(member=member['member'],field=field),self.assertRaises(FormatError):self.prove(self.changed_code(member['member'],field,changed))

    def test_wrong_private_entry_in_close_slot(self):
        b,m,sm=self.contexts['natural'];ids=self.result['contexts'][0]['identities']
        wb=next(c for c in self.result['contributions'] if c['member']=='wbparse')
        r=next(row for row in wb['operand_identity'] if row.get('symbol')=='_CloseLibrary')
        slot=r['candidate_slot']['slot_offset'];h=next(h for h in m['hunks'] if h['number']==1)
        out=bytearray(b);out[h['content_offset']+slot+2:h['content_offset']+slot+6]=ids['__CloseLibrary']['candidate'][1].to_bytes(4,'big')
        bad=copy.deepcopy(m)
        next(x for x in bad['relocations'] if x['source_hunk']==1 and x['source_offset']==slot+2)['addend_raw']=ids['__CloseLibrary']['candidate'][1]
        with self.assertRaisesRegex(FormatError,'target identity'):self.prove((bytes(out),bad,sm))

    def test_putchar_slot_pea_opcode_is_rejected(self):
        # The slot number does not matter: PC/A4 addressing mismatch must reject
        # before any byte-resolution buffer can hide the 487A -> 486C change.
        with self.assertRaises(FormatError):self.prove(self.changed_code('printf',12,bytes.fromhex('486c8002')))

    def test_real_linked_putchar_slot_pea_is_rejected(self):
        directory=ROOT/'build/worker-jobs/routing-04/sys/work'
        if not (directory/'m_put').exists():self.skipTest('linked putchar-slot negative not retained')
        b=(directory/'m_put').read_bytes();m=n.parse(b);sm=n.symbols((directory/'m_put.sym').read_text())
        candidate=(b,m,sm)
        ids,_=n.environment(ROOT,self.recipe,candidate,self.original,self.contexts['crt'])
        ids['_format']=dict(candidate=n.symbol(sm,'_format'),original=(0,0x7bf4+142))
        with self.assertRaisesRegex(FormatError,'addressing mode'):
            n.compare_member(candidate,self.original,0x7bd8,n.symbol(sm,'_printf')[1],28,28,
                {14:dict(kind='PC',symbol='_putchar'),18:dict(kind='PC',symbol='_format')},ids)

    def test_failed_producing_step_rejects(self):
        original_read=n.read
        def changed(root,path):
            raw=original_read(root,path)
            if path==self.recipe['receipt']['path']:
                receipt=json.loads(raw);receipt['steps'][0]['returncode']=1
                return json.dumps(receipt).encode()
            return raw
        with patch.object(n,'read',side_effect=changed),self.assertRaises(FormatError):n.producer(ROOT,self.recipe)

    def test_pc_call_opcode_cannot_replace_a4_route(self):
        for member,site in [('wbparse',146),('format',578)]:
            with self.subTest(member=member),self.assertRaises(FormatError):self.prove(self.changed_code(member,site,bytes.fromhex('4eba0002')))

    def test_missing_wrong_and_duplicate_slot_relocations(self):
        wb=self.result['contributions'][0]
        slot=next(r for r in wb['operand_identity'] if r.get('symbol')=='_CloseLibrary')['candidate_slot']['slot_offset']
        b,m,sm=self.contexts['natural'];entry=next(r for r in m['relocations'] if r['source_hunk']==1 and r['source_offset']==slot+2)
        for field,value in [('type','HUNK_RELOC16'),('width',2),('target_hunk',1),('source_offset',slot),('addend_raw',0)]:
            bad=copy.deepcopy(m);next(r for r in bad['relocations'] if r==entry)[field]=value
            with self.subTest(field=field),self.assertRaises(FormatError):self.prove((b,bad,sm))
        for mode in ['missing','duplicate']:
            bad=copy.deepcopy(m)
            if mode=='missing':bad['relocations'].remove(entry)
            else:bad['relocations'].append(copy.deepcopy(entry))
            with self.subTest(mode=mode),self.assertRaises(FormatError):self.prove((b,bad,sm))

    def test_original_slot_also_rechecks_private_entry_and_relocation(self):
        ob,om=self.original;out=bytearray(ob);h=next(h for h in om['hunks'] if h['number']==1)
        out[h['content_offset']+0x12e:h['content_offset']+0x132]=(0x8788).to_bytes(4,'big')
        bad=copy.deepcopy(om);next(r for r in bad['relocations'] if r['source_hunk']==1 and r['source_offset']==0x12e)['addend_raw']=0x8788
        with self.assertRaisesRegex(FormatError,'target identity'):self.prove(original=(bytes(out),bad))
        bad=copy.deepcopy(om);bad['relocations']=[r for r in bad['relocations'] if not(r['source_hunk']==1 and r['source_offset']==0x12e)]
        with self.assertRaises(FormatError):self.prove(original=(ob,bad))

    def test_internal_pc_target_and_literal_tail_reject(self):
        with self.assertRaises(FormatError):self.prove(self.changed_code('wbparse',14,bytes.fromhex('487a0090')))
        with self.assertRaises(FormatError):self.prove(self.changed_code('wbparse',158,b'X'))
        with self.assertRaises(FormatError):self.prove(self.changed_code('format',540,bytes.fromhex('0002')))

    def test_wrong_cbuf_addend_and_same_length_callback_reject(self):
        b,m,sm=self.contexts['natural'];hn,start=n.symbol(sm,'_putchar');h=next(h for h in m['hunks'] if h['number']==0)
        out=bytearray(b);field=h['content_offset']+start+6
        out[field:field+2]=((int.from_bytes(out[field:field+2],'big')+22)&65535).to_bytes(2,'big')
        with self.assertRaises(FormatError):self.prove((bytes(out),m,sm))

    def test_complete_format_owned_data_not_clipped(self):
        b,m,sm=self.contexts['natural'];off=n.symbol(sm,'_ctp_')[1]-18;h=next(h for h in m['hunks'] if h['number']==1)
        for k in [0,16,17]:
            out=bytearray(b);out[h['content_offset']+off+k]^=1
            with self.subTest(byte=k),self.assertRaises(FormatError):self.prove((bytes(out),m,sm))

    def test_nonzero_data_bss_and_shortened_object_reject(self):
        original_read=n.read
        for pos,value in [(10,178),(14,4),(18,4)]:
            def changed(root,path):
                raw=original_read(root,path)
                if path.endswith('/wbparse.o'):
                    out=bytearray(raw);out[pos:pos+4]=value.to_bytes(4,'big');return bytes(out)
                return raw
            with patch.object(n,'read',side_effect=changed),self.subTest(pos=pos),self.assertRaises(FormatError):n.producer(ROOT,self.recipe)

    def test_rehashed_recipe_changes_never_define_authority(self):
        for key in ['tools','artifacts','commands','sources','anchors']:
            bad=copy.deepcopy(self.recipe);bad[key]={} if key!='commands' else []
            with self.subTest(key=key),self.assertRaisesRegex(FormatError,'curated recipe'):n.producer(ROOT,bad)

    def test_missing_changed_artefact_and_header_reject(self):
        original_read=n.read
        for suffix in ['/format.asm','/consumer.o','/natural.sym']:
            def changed(root,path):return original_read(root,path)+b'X' if path.endswith(suffix) else original_read(root,path)
            with patch.object(n,'read',side_effect=changed),self.subTest(suffix=suffix),self.assertRaises(FormatError):n.producer(ROOT,self.recipe)

    def test_changed_header_pin_rejects(self):
        original_pinned=n.pinned
        def changed(root,path):
            raw=original_pinned(root,path)
            return raw+b'X' if path.endswith('/include/ctype.h') else raw
        with patch.object(n,'pinned',side_effect=changed),self.assertRaises(FormatError):n.producer(ROOT,self.recipe)

    def test_exports_cannot_move_or_be_private_substitutions(self):
        b,m,sm=self.contexts['natural']
        for name in ['_printf','_format','__wb_parse','_routing_consumer']:
            bad=dict(sm);key=next(key for key in bad if key[1]==name);bad[key]+=2
            with self.subTest(name=name),self.assertRaises(FormatError):self.prove((b,m,bad))

    def test_hunk_type_and_unchecked_code_relocation_reject(self):
        b,m,sm=self.contexts['natural'];bad=copy.deepcopy(m);next(h for h in bad['hunks'] if h['number']==1)['type']='CODE'
        with self.assertRaises(FormatError):self.prove((b,bad,sm))
        bad=copy.deepcopy(m);start=n.symbol(sm,'_printf')[1]
        bad['relocations'].append(dict(source_hunk=0,source_offset=start+2,width=4,type='HUNK_RELOC32',target_hunk=1,addend_raw=0))
        with self.assertRaises(FormatError):self.prove((b,bad,sm))

    def test_implicit_and_explicit_ctype_resolve_to_the_same_identity(self):
        # Both complete pinned provider contexts bind at the 0x7FFE bias.
        directory=ROOT/'build/worker-jobs/routing-proof-01/sys/work'
        if not directory.exists():self.skipTest('old rejected context not retained')
        b=(directory/'natural').read_bytes();m=n.parse(b);sm=n.symbols((directory/'natural.sym').read_text())
        self.assertEqual(self.prove((b,m,sm))[0],self.prove()[0])


if __name__=='__main__':unittest.main()
