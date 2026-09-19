import tempfile
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import FormatError,sha256
from owned_static_data import linked_candidate_data,static_data_proof


def object_with_sizes(data,bss=0):
    raw=bytearray(22);raw[:2]=b'AJ';raw[14:18]=data.to_bytes(4,'big');raw[18:22]=bss.to_bytes(4,'big')
    return bytes(raw)


class OwnedStaticDataTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();base=Path(self.temp.name)
        (base/'t000.o').write_bytes(object_with_sizes(4))
        (base/'h000.o').write_bytes(object_with_sizes(2))
        (base/'t000.exe').write_bytes(b'abcdefZZ')
        self.model=dict(hunks=[dict(number=1,type='DATA',content_offset=0,initialized_size=8)],relocations=[],
                        symbols=[dict(hunk=1,name='_values',offset=2)])
        self.compiled=dict(status='COMPILED',directory=str(base),prefix='t000',
            contribution=dict(data_size=4,bss_size=0,symbols=self.model['symbols']))
        self.original=b'abcdefZZ';self.original_model=self.model
        self.manifest=dict(schema_version=1,id='ov99_F_0000',
            candidate_symbol='values',original=dict(hunk=1,start=2,size=4,sha256=sha256(b'cdef')))

    def tearDown(self):self.temp.cleanup()

    @patch('owned_static_data.parse')
    def test_linked_data_follows_harness_data(self,parse):
        parse.return_value=self.model
        linked=linked_candidate_data(self.compiled)
        self.assertEqual((linked['start'],linked['size'],linked['bytes']),(2,4,b'cdef'))

    @patch('owned_static_data.parse')
    def test_linked_data_uses_manifest_symbol_after_runtime_data(self,parse):
        self.model['symbols'][0]['offset']=4
        self.model['hunks'][0]['initialized_size']=10
        self.original=b'abcdefghij'
        Path(self.temp.name,'t000.exe').write_bytes(self.original)
        parse.return_value=self.model
        linked=linked_candidate_data(self.compiled,'values')
        self.assertEqual((linked['start'],linked['size'],linked['bytes']),(4,4,b'efgh'))

    @patch('owned_static_data.parse')
    def test_exact_payload_proof(self,parse):
        parse.return_value=self.model
        proof=static_data_proof(self.compiled,self.manifest,self.original,self.original_model)
        self.assertEqual(proof['kind'],'INITIALIZED_STATIC_DATA')
        self.assertEqual(proof['linked']['start'],2)

    @patch('owned_static_data.parse')
    def test_changed_payload_rejected(self,parse):
        parse.return_value=self.model
        Path(self.temp.name,'t000.exe').write_bytes(b'abcXefZZ')
        with self.assertRaisesRegex(FormatError,'bytes differ'):
            static_data_proof(self.compiled,self.manifest,self.original,self.original_model)

    @patch('owned_static_data.parse')
    def test_relocation_requires_stronger_proof(self,parse):
        parse.return_value=dict(self.model,relocations=[dict(source_hunk=1,source_offset=2,width=4)])
        with self.assertRaisesRegex(FormatError,'relocations'):
            static_data_proof(self.compiled,self.manifest,self.original,self.original_model)
