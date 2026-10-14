"""Scratch-import regression tests for the proposed tail route."""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'tools'))
from common import FormatError
from analysis_support import game
import runtime_tail_members as t
RECIPE_FILE=ROOT/t.RECIPE

class TailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document=json.loads(RECIPE_FILE.read_bytes())
        cls.original=game()[:2]
        cls.result=t.verify(ROOT,document=cls.document,original=cls.original)
        contexts=t.n.producer(ROOT,json.loads((ROOT/t.n.RECIPE).read_bytes()))
        cls.bases=t.n.bootstrap(contexts['crt'],cls.original)
        cls.candidates=[]
        for spec in cls.document['members']:
            b=(ROOT/spec['executable']['path']).read_bytes()
            cls.candidates.append((b,t.parse(b),t.symbols((ROOT/spec['symbols']['path']).read_text())))

    def compare(self,index,candidate=None,original=None,spec=None,bases=None):
        return t.compare_leaf(candidate or self.candidates[index],original or self.original,
                              spec or self.document['members'][index],bases or self.bases)

    def changed(self,index,field,data):
        b,m,sm=self.candidates[index];out=bytearray(b);h=m['hunks'][0]
        out[h['content_offset']+field:h['content_offset']+field+len(data)]=data
        return bytes(out),m,sm

    def test_complete_seven_members_and_bytes(self):
        self.assertEqual([(r['member'],r['size']) for r in self.result['contributions']],
                         [(r[0],r[3]) for r in t.EXPECTED])
        self.assertEqual(sum(r['size'] for r in self.result['contributions']),88)
        self.assertTrue(self.result['contributions'][5]['raw_equal'])
        self.assertEqual(self.result['contributions'][0]['operand_identity'][0]['original'],[1,0xa98e])
        self.assertEqual(self.result['contributions'][2]['operand_identity'][0]['original'],[1,0xb3a2])
        self.assertTrue(all(r['relocation_identity']==[] for r in self.result['contributions']))

    def test_every_ordinary_byte_rejects(self):
        for index,spec in enumerate(self.document['members']):
            field=spec['field'];b,m,sm=self.candidates[index];raw=t.n.extent(b,m,0,0,spec['size'])
            for k in range(spec['size']):
                if field is not None and k in (field,field+1):continue
                with self.subTest(member=spec['member'],byte=k),self.assertRaises(FormatError):
                    self.compare(index,self.changed(index,k,bytes([raw[k]^1])))

    def test_candidate_and_original_displacement_reject(self):
        for index,spec in enumerate(self.document['members']):
            field=spec['field']
            if field is None:continue
            b,m,sm=self.candidates[index];raw=t.n.extent(b,m,0,field,2)
            bad=((int.from_bytes(raw,'big')+2)&65535).to_bytes(2,'big')
            with self.subTest(member=spec['member']),self.assertRaises(FormatError):self.compare(index,self.changed(index,field,bad))
            ob,om=self.original;out=bytearray(ob);h=om['hunks'][0];at=h['content_offset']+spec['original']+field
            out[at+1]^=2
            with self.assertRaises(FormatError):self.compare(index,original=(bytes(out),om))

    def test_symbol_moves_and_wrong_storage_segments_reject(self):
        for index,spec in enumerate(self.document['members']):
            b,m,sm=self.candidates[index]
            bad=dict(sm);bad[(0,spec['export'])]+=2
            with self.assertRaises(FormatError):self.compare(index,(b,m,bad))
            if spec['field'] is not None:
                bad=dict(sm);key=next(k for k in bad if k[1]==spec['base']);bad[key]+=4
                with self.assertRaises(FormatError):self.compare(index,(b,m,bad))
                bad=dict(sm);off=bad.pop(key);bad[(0,spec['base'])]=off
                with self.assertRaises(FormatError):self.compare(index,(b,m,bad))
                bad=dict(sm);bad[(2,'__H2_org')]+=4
                with self.assertRaises(FormatError):self.compare(index,(b,m,bad))

    def test_added_exports_relocations_and_shortened_extent_reject(self):
        for index,spec in enumerate(self.document['members']):
            b,m,sm=self.candidates[index];bad=dict(sm);bad[(0,'private_entry')]=2
            with self.assertRaises(FormatError):self.compare(index,(b,m,bad))
            for original in (False,True):
                blob,model=(self.original if original else (b,m));bad=copy.deepcopy(model)
                bad['relocations'].append(dict(source_hunk=0,source_offset=spec['original']+2 if original else 2,
                    width=4,type='HUNK_RELOC32',target_hunk=1,addend_raw=0))
                with self.assertRaises(FormatError):
                    self.compare(index,original=(blob,bad)) if original else self.compare(index,(b,bad,sm))
            short=dict(spec,size=spec['size']-2)
            with self.assertRaises(FormatError):self.compare(index,spec=short)

    def test_nonunique_resident_whole_leaf_rejects(self):
        ob,om=self.original;out=bytearray(ob);h=om['hunks'][0];spec=self.document['members'][5]
        raw=t.n.extent(ob,om,0,spec['original'],spec['size'])
        out[h['content_offset']:h['content_offset']+len(raw)]=raw
        with self.assertRaises(FormatError):self.compare(5,original=(bytes(out),om))

    def test_wrong_original_base_identity_rejects(self):
        for index in (0,2):
            bases=copy.deepcopy(self.bases);symbol=self.document['members'][index]['base'];bases[symbol]['original']=(1,0)
            with self.assertRaises(FormatError):self.compare(index,bases=bases)

    def test_rehashed_curated_edits_reject(self):
        for key in ('members','job','library','game_sha256'):
            bad=copy.deepcopy(self.document);bad[key]=[] if key=='members' else {}
            with self.assertRaisesRegex(FormatError,'curated recipe'):t.verify(ROOT,document=bad,original=self.original)

    def test_failed_selected_step_and_extraction_reject(self):
        read=t.checked
        for cmd in ('Old2:bin/lb >extract.log Old1:lib/c.lib -x',self.document['members'][0]['link_command']):
            def changed(root,record):
                raw=read(root,record)
                if record==self.document['job']['receipt']:
                    receipt=json.loads(raw);next(s for s in receipt['steps'] if s['command']==cmd)['returncode']=1
                    return json.dumps(receipt).encode()
                return raw
            with patch.object(t,'checked',side_effect=changed),self.assertRaises(FormatError):
                t.verify(ROOT,document=self.document,original=self.original)

    def test_complete_object_header_and_archive_membership_reject(self):
        read=t.checked;claim=self.document['members'][0]['object']
        for pos in (10,14,18):
            def changed(root,record):
                raw=read(root,record)
                if record==claim:
                    out=bytearray(raw);out[pos:pos+4]=(4).to_bytes(4,'big');return bytes(out)
                return raw
            with patch.object(t,'checked',side_effect=changed),self.assertRaises(FormatError):
                t.verify(ROOT,document=self.document,original=self.original)

if __name__=='__main__':unittest.main(verbosity=2)
