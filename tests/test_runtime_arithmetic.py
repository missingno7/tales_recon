import unittest
from runtime_arithmetic import aliases
from function_compare import runtime_symbol_names
from common import sha256, FormatError


class RuntimeAliasTests(unittest.TestCase):
    def setUp(self):
        self.raw=bytes.fromhex('70004e75')
        self.h=dict(number=0,type='CODE',content_offset=0,initialized_size=4)
        self.model=dict(hunks=[self.h],relocations=[])
        self.compiled=dict(identity=dict(profile='test',library_sha256='library'),
            contribution=dict(hunks=[self.h],symbols=[dict(name='.helper',hunk=0,offset=0)],all_relocations=[]))
        self.evidence=dict(game_sha256=sha256(self.raw),contributions=[dict(profile='test',library_sha256='library',
            size=4,original=dict(hunk=0,offset=0,size=4),code_sha256=sha256(self.raw),entries=[dict(name='.helper',offset=0)])])

    def resolve(self, raw=None):
        return aliases(self.compiled,self.raw if raw is None else raw,self.raw,self.model,self.evidence)

    def test_complete_match(self):
        syms,proof=self.resolve()
        self.assertEqual(syms,[dict(hunk=0,offset=0,name='F_h00_0000')])
        self.assertEqual(proof[0]['linked']['size'],4)

    def test_changed_last_instruction(self):
        self.assertEqual(self.resolve(bytes.fromhex('70004e71'))[0],[])

    def test_shifted_symbol(self):
        self.compiled['contribution']['symbols'][0]['offset']=2
        self.assertEqual(self.resolve()[0],[])

    def test_wrong_library(self):
        self.compiled['identity']['library_sha256']='other'
        self.assertEqual(self.resolve()[0],[])

    def test_candidate_relocation_rejected(self):
        self.compiled['contribution']['all_relocations']=[dict(source_hunk=0,source_offset=2,width=2)]
        self.assertEqual(self.resolve()[0],[])

    def test_original_relocation_rejected(self):
        self.model['relocations']=[dict(source_hunk=0,source_offset=2,width=2)]
        with self.assertRaises(FormatError):self.resolve()

    def test_original_hash_rejected(self):
        self.evidence['contributions'][0]['code_sha256']='wrong'
        with self.assertRaises(FormatError):self.resolve()

    def test_partial_match_rejected(self):
        self.compiled['contribution']['hunks']=[dict(self.h,initialized_size=2)]
        self.assertEqual(self.resolve()[0],[])

    def test_runtime_symbol_names_are_not_limited_to_multiply(self):
        self.evidence['contributions'][0]['entries'].append(dict(name='.divs',offset=0))
        self.assertEqual(runtime_symbol_names(self.evidence),{'.helper','.divs'})


if __name__=='__main__':unittest.main()
