"""Adversarial format and provenance tests against independently mutated fixtures."""
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from common import FormatError
from ofs import OFSDisk
from hunk import parse, manx_overlay
from census import derive, verify_lock, fixture_identity
from compare import compare


def set_long(data, offset, value):
    struct.pack_into('>I', data, offset, value)


def repair_checksum(data, block):
    base = block * 512
    set_long(data, base+20, 0)
    checksum = -sum(struct.unpack_from('>128I', data, base)) & 0xffffffff
    set_long(data, base+20, checksum)


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.disk = sorted((ROOT / 'assets').glob('*.adf'))[0].read_bytes()
        d = OFSDisk(cls.disk)
        cls.fs = d.parse()
        cls.exe = d.files['DuckTales']
        cls.model = parse(cls.exe)

    def test_complete_measured_topology(self):
        m = self.model
        self.assertEqual(m['size'], 193004)
        self.assertEqual([h['number'] for h in m['hunks']], list(range(16)))
        self.assertEqual(m['record_counts']['HUNK_BREAK'], 14)
        self.assertEqual(len(m['relocations']), 1445)
        self.assertIn('HUNK_SYMBOL', m['absent_records'])
        self.assertIn('HUNK_DEBUG', m['absent_records'])
        self.assertEqual(m['hunks'][1]['zero_fill_size'], 34088)
        cursor = 0
        for record in m['records']:
            self.assertEqual(record['file_offset'], cursor)
            cursor = record['end_offset']
        self.assertEqual(cursor, len(self.exe))

    def test_overlay_descriptors_and_trampolines(self):
        tree = manx_overlay(self.model, self.exe)
        self.assertEqual(tree['slot_count'],14)
        self.assertEqual(tree['slots'][3]['status'],'EMPTY')
        self.assertEqual(sum(len(e['symbols']) for e in tree['slots']),26)
        self.assertEqual(tree['manager_entry_offsets'],[0x798a])
        self.assertEqual(tree['slots'][5]['node'],'ov07')
        self.assertEqual([s['target_offset'] for s in tree['slots'][5]['symbols']], [0,0x1a02])

    def test_unknown_record_and_trailing_bytes_fail(self):
        b=bytearray(self.exe);set_long(b,0x20,0x7fff)
        with self.assertRaisesRegex(FormatError,'0x20'):
            parse(b)
        with self.assertRaises(FormatError):
            parse(self.exe+b'\0')

    def test_truncation_in_every_record_fails(self):
        for r in self.model['records']:
            with self.subTest(offset=r['file_offset']):
                with self.assertRaises(FormatError):
                    parse(self.exe[:r['file_offset']+1])

    def test_missing_final_overlay_break_fails(self):
        with self.assertRaisesRegex(FormatError,'final BREAK'):
            parse(self.exe[:-4])

    def test_wrong_bridge_relocation_fails(self):
        b=bytearray(self.exe)
        bridge_rel=next(r for r in self.model['relocations'] if r['source_hunk']==1 and r['source_offset']==0x31a)
        set_long(b,self.model['hunks'][1]['content_offset']+0x318,0x4e750000)
        with self.assertRaisesRegex(FormatError,'JMP absolute bridge'):
            manx_overlay(parse(b),b)

    def test_allocation_too_small_fails(self):
        b=bytearray(self.exe);set_long(b,20,0x40000001)
        with self.assertRaisesRegex(FormatError,'exceeds allocation'):
            parse(b)

    def test_relocation_site_outside_hunk_fails(self):
        b=bytearray(self.exe)
        set_long(b,self.model['relocations'][0]['entry_offset'],0x100000)
        with self.assertRaisesRegex(FormatError,'relocation site'):
            parse(b)

    def test_relocation_target_outside_topology_fails(self):
        b=bytearray(self.exe)
        set_long(b,self.model['relocations'][0]['record_offset']+8,100)
        with self.assertRaisesRegex(FormatError,'relocation target'):
            parse(b)

    def test_wrong_overlay_pointer_fails(self):
        b=bytearray(self.exe);set_long(b,self.model['overlay']['content_offset']+4,0xd15c)
        with self.assertRaisesRegex(FormatError,'overlay offset'):
            manx_overlay(parse(b),b)

    def test_wrong_trampoline_node_fails(self):
        b=bytearray(self.exe);b[self.model['hunks'][1]['content_offset']+0x248+4]=0
        with self.assertRaisesRegex(FormatError,'trampoline'):
            manx_overlay(parse(b),b)

    def test_disk_corruption_fails(self):
        b=bytearray(self.disk);b[880*512+50]^=1
        with self.assertRaisesRegex(FormatError,'checksum'):
            OFSDisk(b).parse()
        with self.assertRaises(FormatError):
            OFSDisk(self.disk[:-1])
        b=bytearray(self.disk);b[3]=1
        with self.assertRaises(FormatError):
            OFSDisk(b)

    def test_chain_cycle_with_valid_checksums_fails(self):
        entry=next(e for e in self.fs['entries'] if e['path']=='DuckTales')
        block=entry['data_blocks'][0]['block'];b=bytearray(self.disk)
        set_long(b,block*512+16,block);repair_checksum(b,block)
        with self.assertRaisesRegex(FormatError,'duplicate use'):
            OFSDisk(b).parse()

    def test_crosscheck_detects_pointer_disagreement(self):
        entry=next(e for e in self.fs['entries'] if e['path']=='DuckTales')
        h=entry['header_block'];b=bytearray(self.disk)
        set_long(b,h*512+77*4,entry['data_blocks'][1]['block']);repair_checksum(b,h)
        with self.assertRaisesRegex(FormatError,'pointers disagree'):
            OFSDisk(b).parse()

    def test_bitmap_and_disk2_boot_observations(self):
        d=OFSDisk(sorted((ROOT/'assets').glob('*.adf'))[1].read_bytes()).parse()
        self.assertEqual(d['volume'],'DT2')
        self.assertFalse(d['boot']['checksum_valid'])
        self.assertEqual(d['bitmap']['allocated_unreferenced_blocks'],[])
        self.assertEqual(self.fs['startup_sequences'][0]['text'],'DuckTales\nendcli >nil:\n')

    def test_complete_partition_and_determinism(self):
        a,files,m=derive(ROOT);b,_,_=derive(ROOT)
        self.assertEqual(a,b)
        self.assertEqual(len(files),39)
        ranges=a['evidence/executable/byte-map.json']['ranges']
        for h in m['hunks']:
            cursor=0
            for r in (r for r in ranges if r['hunk']==h['number']):
                self.assertEqual(r['start'],cursor);cursor=r['end']
            self.assertEqual(cursor,h['allocated_size'])
        self.assertFalse(a['docs/progress.json']['pilot_complete'])

    def test_lock_detects_changed_and_added_fixtures_without_rewriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'assets').mkdir();(root/'evidence').mkdir()
            p=root/'assets/test.adf';p.write_bytes(b'original')
            lock=root/'evidence/fixture-lock.json'
            lock.write_text(json.dumps(dict(supplied_inputs=fixture_identity(root))))
            before=lock.read_bytes();verify_lock(root);p.write_bytes(b'changed')
            with self.assertRaisesRegex(FormatError,'lock mismatch'):
                verify_lock(root)
            self.assertEqual(lock.read_bytes(),before)
            p.write_bytes(b'original');(root/'assets/extra').write_bytes(b'added')
            with self.assertRaises(FormatError):verify_lock(root)

    def test_comparison_separates_bytes_and_relocations(self):
        same=compare(self.exe,self.exe)
        self.assertTrue(same['whole_file_equal']);self.assertIsNone(same['reconstruction_proof_level'])
        b=bytearray(self.exe);b[0x28+100]^=1
        diff=compare(self.exe,b)
        self.assertFalse(diff['hunk_content_equal']);self.assertTrue(diff['relocations_equal'])
        self.assertEqual(diff['hunks'][0]['first_mismatch']['offset'],100)
        b=bytearray(self.exe)
        rel=self.model['relocations'][0]
        # Keep a valid target but change its identity.
        set_long(b,rel['record_offset']+8,(rel['target_hunk']+1)%3)
        diff=compare(self.exe,b)
        self.assertTrue(diff['hunk_content_equal']);self.assertFalse(diff['relocations_equal'])


if __name__=='__main__':
    unittest.main()
