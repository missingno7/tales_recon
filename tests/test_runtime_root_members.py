"""Whole-object root runtime acceptance and strict field/ABI rejection controls."""
import sys,copy,json,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from common import FormatError,sha256
from analysis_support import game
from census import advisory_image
import runtime_root_members as r
import runtime_entry_routes as routes

class RootRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with advisory_image():cls.original=game()[:2]
        cls.doc=json.loads((ROOT/r.RECIPE).read_text())
        cls.free,cls.obj=r.producer(ROOT,cls.doc)
        cls.crt=r.contexts(ROOT)
        cls.ids=r.anchors(ROOT,cls.doc,cls.original)

    def test_complete_members_and_all_contexts(self):
        report=r.verify(ROOT,original=self.original)
        self.assertEqual([(x['member'],x['size']) for x in report['contributions']],[('freeseg',182),('crt0',122)])
        for row in r.specimens(ROOT,report):
            expected=[{k:v for k,v in rel.items() if k in ('source_offset','target_hunk','type','width','addend_raw')} for rel in self.original[1]['relocations'] if rel['source_hunk']==0 and row['start']<=rel['source_offset']<row['end']]
            self.assertEqual(row['relocations'],expected)
            self.assertEqual(bytes.fromhex(row['actual_hex']),r.n.extent(*self.original,0,row['start'],row['end']-row['start']))
        self.assertEqual([len(x['relocation_identity']) for x in report['contributions']],[4,1])
        self.assertTrue(all(x['owned_data_size']==x['owned_bss_size']==0 for x in report['contributions']))

    def test_freeseg_complete_relocations_reject_changes(self):
        for key,value in [('target_hunk',1),('type','HUNK_RELOC16'),('width',2),('addend_raw',10),('source_offset',0x7522+20)]:
            model=copy.deepcopy(self.original[1]);next(x for x in model['relocations'] if x['source_hunk']==0 and x['source_offset']==0x7522+18)[key]=value
            with self.subTest(key=key),self.assertRaises(FormatError):r.compare_freeseg(self.free,(self.original[0],model))
        model=copy.deepcopy(self.original[1]);model['relocations']=[x for x in model['relocations'] if not (x['source_hunk']==0 and x['source_offset']==0x7522+24)]
        with self.assertRaises(FormatError):r.compare_freeseg(self.free,(self.original[0],model))

    def test_partial_objects_and_alignment_reject(self):
        with self.assertRaises(FormatError):r.compare_freeseg(self.free,self.original,size=180)
        with self.assertRaises(FormatError):r.compare_crt(self.crt[0],self.original,self.ids,size=120)
        b,m,sm=self.free;bad=bytearray(b);bad[m['hunks'][0]['content_offset']+182]=1
        with self.assertRaises(FormatError):r.compare_freeseg((bytes(bad),m,sm),self.original)

    def test_wrong_independent_global_and_entry_bindings_reject(self):
        for key in self.ids:
            ids=dict(self.ids);ids[key]+=2
            with self.subTest(key=key),self.assertRaises(FormatError):r.compare_crt(self.crt[0],self.original,ids)

    def test_masked_field_and_wrong_candidate_binding_reject(self):
        with self.assertRaises(FormatError):r.compare_crt(self.crt[0],self.original,self.ids,fields=r.c.FIELDS[:-1])
        b,m,sm=self.crt[0];sm=dict(sm);sm[(2,'__savsp')]+=4
        with self.assertRaises(FormatError):r.compare_crt((b,m,sm),self.original,self.ids)
        with self.assertRaises(FormatError):r.resolve_crt(bytes(120),[0]*7)

    def test_literal_and_ordinary_code_and_crt_relocation_reject(self):
        for off in (44,102,113):
            b,m=self.original;bad=bytearray(b);bad[m['hunks'][0]['content_offset']+0x75f2+off]^=1
            with self.subTest(off=off),self.assertRaises(FormatError):r.compare_crt(self.crt[0],(bytes(bad),m),self.ids)
        model=copy.deepcopy(self.original[1]);next(x for x in model['relocations'] if x['source_hunk']==0 and x['source_offset']==0x75f2+116)['addend_raw']+=2
        with self.assertRaises(FormatError):r.compare_crt(self.crt[0],(self.original[0],model),self.ids)

    def test_unmodified_producer_and_curated_input_reject_tampering(self):
        read=r.read
        def changed(root,path):
            raw=read(root,path)
            return raw+b'X' if path.endswith('/freeseg.o') else raw
        with patch.object(r,'read',side_effect=changed),self.assertRaises(FormatError):r.producer(ROOT,self.doc)
        doc=copy.deepcopy(self.doc);doc['anchors'].pop('resident_F_8552')
        with self.assertRaises(FormatError):r.verify(ROOT,document=doc,original=self.original)

    def test_export_public_freeseg_only(self):
        proof=r.verify(ROOT,original=self.original);export=routes.export(proof,r.OUTPUT,'x')
        self.assertEqual(set(export),{(0,0x7522)})
        self.assertEqual(export[(0,0x7522)]['symbol'],'_freeseg')
        self.assertNotIn((0,0x7664),export)
        exported=routes.load(ROOT,sha256(self.original[0]),original=self.original,audit=True)
        self.assertEqual(exported[(0,0x7522)]['symbol'],'_freeseg')
        self.assertNotIn((0,0x75f2),exported);self.assertNotIn((0,0x7664),exported)

    def test_snapshot_tracks_all_root_inputs(self):
        identity=r.input_identity(ROOT)
        for suffix in ('/freeseg.o','/freeseg.exe','/dos-first-lib.exe','/crt0-source.asm','/resident_F_8552.mixed.json','/runtime-members-root.json'):
            self.assertTrue(any(k.replace('\\','/').endswith(suffix) for k in identity),suffix)

if __name__=='__main__':unittest.main()
