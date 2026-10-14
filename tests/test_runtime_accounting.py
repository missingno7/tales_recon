"""Runtime accounting must replay proofs, preserve fields, and count bytes once."""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from common import FormatError,sha256
import runtime_accounting as r
from census import derive


class RuntimeAccountingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _,files,cls.model=derive(ROOT,promotion_evidence=False)
        cls.blob=files['DT1:DuckTales']
        cls.rows=r.capture_runtime_members(ROOT,cls.blob,cls.model)

    def test_complete_extents_and_serialization(self):
        self.assertEqual([(x['hunk'],x['start'],x['end']-x['start']) for x in self.rows],
            [(0,0x7978,244),(0,0x7b24,180),(0,0x7bf4,936),(0,0x7bd8,28),
             (0,0x704e,112),(0,0x70be,1124),(0,0x850a,42),(0,0x8794,210),(0,0x887e,40),(0,0x88a6,128),
             (1,0x2c64,18),(1,0x2c76,130),(1,0x2cf8,440)])
        self.assertEqual(self.rows,json.loads(json.dumps(self.rows)))
        for c in r.contributions(self.rows):
            h=next(h for h in self.model['hunks'] if h['number']==c['hunk'])
            self.assertEqual(c['bytes'],self.blob[h['content_offset']+c['start']:h['content_offset']+c['end']])

    def test_segload_carries_both_exact_relocations(self):
        self.assertEqual(self.rows[0]['relocations'],[
            dict(source_offset=0x79a0,target_hunk=0,type='HUNK_RELOC32',width=4,addend_raw=8),
            dict(source_offset=0x79b6,target_hunk=1,type='HUNK_RELOC32',width=4,addend_raw=0)])

    def test_segload_relocation_tampering_rejects(self):
        for key,value in [('target_hunk',1),('type','HUNK_RELOC16'),('width',2),('addend_raw',10)]:
            m=copy.deepcopy(self.model)
            next(x for x in m['relocations'] if x['source_hunk']==0 and x['source_offset']==0x79a0)[key]=value
            with self.subTest(key=key),self.assertRaises(FormatError):r.capture_runtime_members(ROOT,self.blob,m)

    def test_stale_report_rejects(self):
        with self.assertRaises(FormatError):r.checked_report(ROOT,r.natural.OUTPUT,dict(contributions=[]))

    def test_changed_retained_payload_rejects(self):
        read=r.natural.read
        def changed(root,path):
            b=read(root,path)
            return b+b'X' if path.endswith('/ctype.o') else b
        with patch.object(r.natural,'read',side_effect=changed),self.assertRaises(FormatError):
            r.capture_runtime_members(ROOT,self.blob,self.model)

    def test_missing_or_duplicate_runtime_and_changed_hash_reject(self):
        for mode in ('duplicate','overlap','hash','length'):
            rows=copy.deepcopy(self.rows)
            if mode=='duplicate':rows.append(copy.deepcopy(rows[0]))
            elif mode=='overlap':rows[1]['start']=rows[0]['start'];rows[1]['end']=rows[1]['start']+180
            elif mode=='hash':rows[0]['actual_sha256']='0'*64
            else:rows[0]['end']-=2
            with self.subTest(mode=mode),self.assertRaises(FormatError):r.contributions(rows)

    def test_wbparse_reclassifies_once(self):
        row=next(x for x in r.contributions(self.rows) if x['id']=='runtime_member_wbparse')
        old=[dict(id='resident_F_7B24',hunk=0,start=0x7b24,end=0x7bc2,bytes=row['bytes'][:158],category='RECOVERED_C'),
             dict(id='resident_F_7B24_tail',hunk=0,start=0x7bc2,end=0x7bd8,bytes=row['bytes'][158:],category='COMPILER_OWNED_DATA')]
        self.assertEqual(r.merge_accounting(old,[row]),[row])
        for bad in (old[:1],[dict(old[0],id='other'),old[1]],[dict(old[0],bytes=b'X'*158),old[1]]):
            with self.assertRaises(FormatError):r.merge_accounting(bad,[row])

    def test_arbitrary_or_duplicate_ownership_overlap_rejects(self):
        rows=r.contributions(self.rows)
        with self.assertRaises(FormatError):r.merge_accounting([rows[0]],rows)
        with self.assertRaises(FormatError):r.merge_accounting(rows,[rows[1]])

    def test_topology_segload_counts_once_and_data_is_separate(self):
        occupied={(0,i) for i in range(0x7978,0x7a6c)}
        union=r.candidate_union(occupied,self.rows,(0,0x7978,0x7a6c))
        self.assertEqual(len(union),244+180+936+28+1656)
        self.assertTrue(all(hn==0 for hn,_ in union))
        for extent in (None,(0,0x7978,0x7a6a)):
            with self.assertRaises(FormatError):r.candidate_union(occupied,self.rows,extent)
        with self.assertRaises(FormatError):r.candidate_union({(0,0x7bf4)},self.rows,None)

    def test_route_uses_slot_and_pc_uses_instruction_origin(self):
        pc=dict(field=2,width=2,site=0,kind='PC',original=[0,0x120])
        a4=dict(field=6,width=2,site=4,kind='A4',original=[0,0x8784],original_slot=dict(slot_hunk=1,slot_offset=0x12c))
        out=r.resolve_fields(bytes(8),0x100,[pc,a4])
        self.assertEqual(out[2:4],b'\x00\x1e')
        self.assertEqual(out[6:8],(0x12c-32766).to_bytes(2,'big',signed=True))
        with self.assertRaises(FormatError):r.resolve_fields(bytes(8),0x100,[pc,pc])

    def test_snapshot_tracks_jobs_tools_anchors_and_reports(self):
        identity=r.input_identity(ROOT)
        for suffix in ('/ctype.o','/format.o','/natural.sym','/runtime-members-relocated.json',
                       '/resident_F_7B24.c','/SYS1/lib/c.lib','/worker.uae'):
            self.assertTrue(any(k.replace('\\','/').endswith(suffix) for k in identity),suffix)

if __name__=='__main__':unittest.main()
