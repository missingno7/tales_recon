import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from common import FormatError
from inventory_candidate import file_kind, inventory


class HostFormatTests(unittest.TestCase):
    def test_mz_does_not_imply_windows_native(self):
        self.assertEqual(file_kind(b'MZ'+bytes(98)), 'DOS_MZ_OR_LEGACY_WINDOWS_NOT_NATIVE_PE')
        self.assertEqual(file_kind(bytes.fromhex('000003f3')), 'AMIGA_HUNK_EXECUTABLE')
        image=bytearray(128);image[:2]=b'MZ';image[60:64]=(64).to_bytes(4,'little');image[64:68]=b'PE\0\0'
        self.assertEqual(file_kind(image),'WINDOWS_PE')


@unittest.skipUnless((ROOT/'toolchain/downloads/aztecc50a.zip').exists(), 'optional local candidate is not installed')
class CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lock=json.loads((ROOT/'toolchain/candidate-lock.json').read_text())
        cls.archive=ROOT/cls.lock['archive']

    def test_bad_archive_pin_is_rejected(self):
        wrong=dict(self.lock,sha256='0'*64)
        with self.assertRaisesRegex(FormatError,'archive lock mismatch'):
            inventory(self.archive,wrong)

    def test_bad_member_pin_is_rejected(self):
        wrong=json.loads(json.dumps(self.lock));wrong['members'][0]['sha256']='0'*64
        with self.assertRaisesRegex(FormatError,'member lock mismatch'):
            inventory(self.archive,wrong)

    def test_bad_disk_is_quarantined_without_partial_extraction(self):
        report,files=inventory(self.archive,self.lock)
        self.assertEqual(report['validated_disks'],3)
        self.assertEqual(report['rejected_disks'],1)
        failed=next(d for d in report['disks'] if d['status']!='VALIDATED')
        self.assertEqual(failed['member'],'AztecCv50a3.adf')
        self.assertEqual(failed['error'],'asm/exec/exec_lib.i: invalid data block 945')
        self.assertFalse(any(p.startswith('Aztec3:') for p in files))
        self.assertEqual(report['validated_files'],339)
        for p in ('Aztec2:bin/cc','Aztec2:bin/as','Aztec2:bin/ln'):
            self.assertEqual(file_kind(files[p]),'AMIGA_HUNK_EXECUTABLE')
        self.assertFalse(report['execution_performed'])


if __name__=='__main__':
    unittest.main()
