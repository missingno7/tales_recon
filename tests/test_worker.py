import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from aztec_worker import collect
from common import FormatError

class WorkerCollectionTests(unittest.TestCase):
    def fixture(self, root, status):
        work=root/'sys/work';work.mkdir(parents=True)
        (root/'request.json').write_text(json.dumps({'steps':[{'returncode_file':'step-00.rc'}]}))
        (work/'done.txt').write_text('done\n')
        if status is not None:
            (work/'step-00.rc').write_text(status)
        return root

    def test_completion_is_not_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=collect(self.fixture(Path(tmp),'10\n'))
            self.assertFalse(result['all_steps_succeeded'])
            self.assertIsNone(result['reconstruction_proof_level'])

    def test_missing_status_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(OSError):
                collect(self.fixture(Path(tmp),None))

    def test_malformed_status_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FormatError):
                collect(self.fixture(Path(tmp),'$RC'))
