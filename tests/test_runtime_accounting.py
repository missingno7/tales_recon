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

    # 76 complete Aztec 3.6a c.lib DOS/exec/graphics glue objects (sol-glue-tail
    # report member table; 1,076 bytes). Fifteen already-credited members are excluded.
    GLUE=[(0x868c,4),(0x8690,12),(0x869c,12),(0x86a8,12),(0x86b4,12),(0x86c0,8),(0x86c8,8),(0x86d0,12),(0x86dc,
        4),(0x86e0,14),(0x86ee,8),(0x86f6,4),(0x86fa,14),(0x8708,4),(0x870c,14),(0x871a,14),(0x8728,14),
        (0x8736,14),(0x8744,24),(0x875c,16),(0x876c,12),(0x8778,12),(0x8866,12),(0x8872,12),(0x8938,18),
        (0x894a,22),(0x8970,4),(0x8974,8),(0x8990,12),(0x899c,12),(0x89a8,18),(0x89ba,22),(0x89e4,8),(0x89ec,
        14),(0x89fa,12),(0x8a06,12),(0x8a12,12),(0x8a1e,14),(0x8a2c,14),(0x8a3a,12),(0x8a46,34),(0x8a68,34),
        (0x8a8a,18),(0x8a9c,12),(0x8aa8,18),(0x8aba,12),(0x8ac6,12),(0x8ad2,12),(0x8ade,12),(0x8aea,12),
        (0x8b20,18),(0x8b32,12),(0x8b4c,18),(0x8b6a,12),(0x8b76,18),(0x8b88,16),(0x8b98,16),(0x8ba8,16),
        (0x8bb8,16),(0x8bc8,16),(0x8bd8,18),(0x8bea,26),(0x8c04,12),(0x8c10,18),(0x8c22,14),(0x8c30,12),
        (0x8c3c,12),(0x8c48,30),(0x8c66,8),(0x8c6e,16),(0x8c7e,8),(0x8c86,18),(0x8c98,30),(0x8cb6,14),(0x8cc4,
        12),(0x8cd0,8)]

    def test_complete_extents_and_serialization(self):
        self.assertEqual([(x['hunk'],x['start'],x['end']-x['start']) for x in self.rows],
            [(0,0x7978,244),(0,0x7b24,180),(0,0x7bf4,936),(0,0x7bd8,28),
             (0,0x704e,112),(0,0x70be,1124),(0,0x850a,42),(0,0x8794,210),(0,0x887e,40),(0,0x88a6,128),
             (1,0x2c64,18),(1,0x2c76,130),(1,0x2cf8,440)]+[(0,a,n) for a,n in self.GLUE]+[(0,0x8056,22),(0,0x83e0,88),(0,0x8438,36),(0,0x84da,48),(0,0x845c,126),(0,0x8d32,112),(0,0x7522,182),(0,0x75f2,122)])
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
        self.assertEqual(len(union),244+180+936+28+1656+sum(n for _,n in self.GLUE)+432+304)
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
