"""Strict acceptance controls for actual retained pinned-library specimens."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from analysis_support import ROOT,game
from recovery_state import evidence
from recovery_evidence import load_promotions
from common import FormatError,sha256
from library_a4 import load_library_a4,INPUT
from hunk import parse

class LibraryA4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob,cls.model,_=game();cls.analysis=evidence()
        cls.ledger=json.loads((ROOT/'recovery/ledger.json').read_text())
        cls.promotions=load_promotions(ROOT,cls.blob,cls.model,cls.analysis)
        cls.doc=json.loads((ROOT/INPUT).read_text())
        cls.temp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.temp.cleanup)
        cls.base=Path(cls.temp.name)/'base';cls.base.mkdir()
        paths=[INPUT,cls.doc['basis']['path'],cls.doc['library']['path'],'evidence/toolchain/aztec-3.6a.json']
        paths.extend(a['path'] for a in cls.doc['archives'])
        for g in cls.doc['groups']:
            paths.extend(o['source'] for o in g['objects'])
            paths.extend(o[k]['path'] for o in g['objects'] for k in ('library','assembled'))
            paths.extend(c[k]['path'] for c in g['controls'] for k in ('executable','symbols','root_object'))
            paths.extend(c['root_source'] for c in g['controls'])
        for r in cls.doc['receipts']:
            paths.append(r['path']);receipt=json.loads((ROOT/r['path']).read_text())
            paths.extend(t['path'] for t in receipt['tool_inputs'])
        caller=cls.ledger['functions']['ov04_F_1E36'];paths.extend([caller['source'],caller['proof']])
        for p in set(paths):
            target=cls.base/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/p,target)
    def setUp(self):
        self.temp_case=tempfile.TemporaryDirectory();self.addCleanup(self.temp_case.cleanup)
        self.root=Path(self.temp_case.name)/'repo';shutil.copytree(self.base,self.root);self.document=copy.deepcopy(self.doc)
    def validate(self,**kwargs):
        return load_library_a4(self.root,self.blob,self.model,self.analysis,self.promotions,
            kwargs.get('ledger',self.ledger),document=self.document)
    def test_real_complete_units_only_count_122_runtime_bytes(self):
        rows=self.validate();self.assertEqual(len(rows),8);self.assertEqual(sum(len(r['bytes']) for r in rows),122)
        self.assertTrue(all(r['category']=='PINNED_RUNTIME' for r in rows))
        for r in rows:
            h=next(x for x in self.model['hunks'] if x['number']==r['hunk'])
            self.assertEqual(r['bytes'],self.blob[h['content_offset']+r['start']:h['content_offset']+r['end']])
    def test_legacy_absence_has_no_runtime_claim(self):
        (self.root/INPUT).unlink()
        self.assertEqual(load_library_a4(self.root,self.blob,self.model,self.analysis,self.promotions,self.ledger),[])
    def test_stale_canonical_source_and_proof_reject(self):
        for key in ('source_sha256','proof_sha256'):
            ledger=copy.deepcopy(self.ledger);ledger['functions']['ov04_F_1E36'][key]='0'*64
            with self.assertRaises(FormatError):self.validate(ledger=ledger)
    def test_wrong_game_group_base_bounds_and_reference_reject(self):
        mutations=[lambda d:d.update(game_sha256='0'*64),lambda d:d['groups'].pop(0),
            lambda d:d['groups'][0]['reference'].update(original_offset=21360),
            lambda d:d['groups'][0]['reference'].update(width=4),
            lambda d:d['groups'][0]['original'].update(size=16),
            lambda d:d['groups'][0]['definitions'][0].update(offset=2)]
        for mutate in mutations:
            self.document=copy.deepcopy(self.doc);mutate(self.document)
            with self.assertRaises(FormatError):self.validate()
    def test_same_shape_wrong_base_initview_rejects(self):
        g=next(g for g in self.document['groups'] if g['id']=='initview')
        g['original']['start']=0x89fa
        with self.assertRaises(FormatError):self.validate()
    def test_sdk_source_and_member_object_mutations_reject(self):
        for key in ('source','library','assembled'):
            self.document=copy.deepcopy(self.doc);o=self.document['groups'][0]['objects'][0]
            p=self.root/(o[key] if key=='source' else o[key]['path']);original=p.read_bytes()
            p.write_bytes(original+b'x')
            if key!='source':o[key]['sha256']=sha256(p.read_bytes())
            with self.assertRaises(FormatError):self.validate()
            p.write_bytes(original)
    def test_changed_link_recipe_rejects_even_rehashed_receipt(self):
        r=self.document['receipts'][0];p=self.root/r['path'];doc=json.loads(p.read_text())
        step=next(s for s in doc['steps'] if 'bin/ln' in s['command']);step['command']+=' +ccd'
        p.write_text(json.dumps(doc));r['sha256']=sha256(p.read_bytes())
        with self.assertRaises(FormatError):self.validate()
    def test_wrong_executable_and_map_reject_even_rehashed_metadata(self):
        for key in ('executable','symbols'):
            self.document=copy.deepcopy(self.doc);c=self.document['groups'][0]['controls'][0]
            p=self.root/c[key]['path'];original=p.read_bytes()
            p.write_bytes(original+b'x');c[key]['sha256']=sha256(p.read_bytes())
            with self.assertRaises(FormatError):self.validate()
            p.write_bytes(original)
    def test_body_and_base_mutations_with_rehashed_receipt_reject(self):
        for relative in (0,12):
            self.document=copy.deepcopy(self.doc);g=self.document['groups'][0];c=g['controls'][0]
            ep=self.root/c['executable']['path'];original=ep.read_bytes();m=parse(original);h=m['hunks'][0]
            damaged=bytearray(original);damaged[h['content_offset']+relative]^=1;ep.write_bytes(damaged)
            c['executable']['sha256']=sha256(damaged)
            r=self.document['receipts'][0];rp=self.root/r['path'];raw=rp.read_bytes();receipt=json.loads(raw)
            a=next(a for a in receipt['artifacts'] if a['path']==ep.name);a['sha256']=sha256(damaged)
            rp.write_text(json.dumps(receipt));r['sha256']=sha256(rp.read_bytes())
            with self.assertRaises(FormatError):self.validate()
            ep.write_bytes(original);rp.write_bytes(raw)
    def test_changed_library_rehashed_document_still_fails_distribution_pin(self):
        a=self.document['library'];p=self.root/a['path'];p.write_bytes(p.read_bytes()+b'x');a['sha256']=sha256(p.read_bytes())
        with self.assertRaisesRegex(FormatError,'pinned distribution'):self.validate()
    def test_extra_code_allocation_rehashed_receipt_rejects(self):
        c=self.document['groups'][0]['controls'][0];ep=self.root/c['executable']['path'];damaged=bytearray(ep.read_bytes())
        # Single root HUNK_HEADER has three allocations, beginning at byte20.
        damaged[20:24]=(6).to_bytes(4,'big');ep.write_bytes(damaged);c['executable']['sha256']=sha256(damaged)
        r=self.document['receipts'][0];rp=self.root/r['path'];receipt=json.loads(rp.read_text())
        next(a for a in receipt['artifacts'] if a['path']==ep.name)['sha256']=sha256(damaged)
        rp.write_text(json.dumps(receipt));r['sha256']=sha256(rp.read_bytes())
        with self.assertRaisesRegex(FormatError,'natural link extent'):self.validate()
    def test_legacy_six_unit_input_remains_88_bytes(self):
        self.document['groups']=self.document['groups'][:6];self.document['receipts']=self.document['receipts'][:2]
        self.assertEqual(sum(len(r['bytes']) for r in self.validate()),88)
    def test_kernel_private_helper_order_and_identity_reject(self):
        for mutate in (lambda g:g['definitions'][1].update(offset=6),
                       lambda g:g['reference'].update(original_offset=45990),
                       lambda g:g['objects'].reverse()):
            self.document=copy.deepcopy(self.doc);mutate(self.document['groups'][-1])
            with self.assertRaises(FormatError):self.validate()
