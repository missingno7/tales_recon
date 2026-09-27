"""Adversarial contracts for the non-authoritative 68k diagnostic API."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import diag


class DiagnosticContractTests(unittest.TestCase):
    def compare(self, expected, actual):
        result = diag.compare_code(bytes.fromhex(expected), bytes.fromhex(actual))
        self.assertEqual(result['status'], 'DIAGNOSTIC_ONLY', result)
        self.assertEqual(result['claim'], 'DIAGNOSTIC_ONLY_NO_EQUALITY_OR_SEMANTIC_CLAIM')
        for forbidden in ('verdict', 'proof_level', 'promotion', 'equal'):
            self.assertNotIn(forbidden, result)
        return result

    def test_external_bsr_target_is_not_an_intraprocedural_edge(self):
        # BSR.W from PC+2 with +0x10 points beyond this complete byte extent.
        raw = bytes.fromhex('610000104e75')
        insns, error = diag._decode(raw)
        self.assertIsNone(error)
        self.assertEqual(insns[0].mnemonic.lower(), 'bsr.w')
        self.assertFalse(diag._is_branch(insns[0]))
        self.assertIsNone(diag._branch_target(insns[0]))
        result = self.compare(raw.hex(), raw.hex())
        self.assertEqual(result['blocks']['unresolved_edges'],
                         {'expected': None, 'actual': None})
        self.assertTrue(all(block['target'] is None for block in
                            diag._blocks(diag._decode(bytes.fromhex('610000104e75'))[0])[0]))

    def test_bne_byte_and_word_encodings_have_direct_branch_blocks(self):
        byte = diag.compare_code(bytes.fromhex('66024e714e75'),
                                  bytes.fromhex('660000024e714e75'))
        self.assertEqual(byte['status'], 'DIAGNOSTIC_ONLY')
        for side in ('expected', 'actual'):
            blocks, error = diag._blocks(diag._decode(
                bytes.fromhex('66024e714e75' if side == 'expected' else '660000024e714e75'))[0])
            self.assertIsNone(error)
            self.assertEqual(blocks[0]['terminator'], 'branch')
            self.assertEqual(blocks[0]['condition'], 'bne')
            self.assertEqual(blocks[0]['target'], 4)

    def test_btst_is_not_a_branch(self):
        insns, error = diag._decode(bytes.fromhex('080000014e75'))
        self.assertIsNone(error)
        self.assertEqual(insns[0].mnemonic.lower().split('.', 1)[0], 'btst')
        self.assertFalse(diag._is_branch(insns[0]))
        blocks, error = diag._blocks(insns)
        self.assertIsNone(error)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]['terminator'], 'return')

    def test_dbra_is_a_conditional_branch_with_a_target(self):
        insns, error = diag._decode(bytes.fromhex('51c8fffe4e75'))
        self.assertIsNone(error)
        self.assertEqual(insns[0].mnemonic.lower().split('.', 1)[0], 'dbra')
        blocks, error = diag._blocks(insns)
        self.assertIsNone(error)
        self.assertEqual(blocks[0]['terminator'], 'branch')
        self.assertEqual(blocks[0]['condition'], 'dbra')
        self.assertEqual(blocks[0]['target'], 0)

    def test_a5_frame_displacement_is_reported_as_a_frame_reference(self):
        # MOVE.W 8(A5),D0 versus MOVE.W 10(A5),D0.
        result = self.compare('302d00084e75', '302d000a4e75')
        hypotheses = {h['category'] for h in result['hypotheses']}
        self.assertIn('frame_or_stack_reference', hypotheses)
        evidence = next(e for h in result['hypotheses'] if h['category'] == 'frame_or_stack_reference'
                        for e in h['evidence'])
        expected, error = diag._decode(bytes.fromhex(evidence['expected']['raw']))
        actual, actual_error = diag._decode(bytes.fromhex(evidence['actual']['raw']))
        self.assertIsNone(error)
        self.assertIsNone(actual_error)
        self.assertTrue(any(o.type == diag.K.M68K_OP_MEM and o.mem.base_reg == diag.K.M68K_REG_A5 and o.mem.disp == 8
                            for o in expected[0].operands))
        self.assertTrue(any(o.type == diag.K.M68K_OP_MEM and o.mem.base_reg == diag.K.M68K_REG_A5 and o.mem.disp == 10
                            for o in actual[0].operands))

    def test_register_role_swap_is_visible_even_when_register_sets_match(self):
        # Both instructions mention D0 and D1, but source/destination roles swap.
        result = self.compare('22004e75', '20014e75')
        assignment = next(h for h in result['hypotheses']
                          if h['category'] == 'register_assignment')
        self.assertGreater(assignment['count'], 0)

    def test_branch_target_and_polarity_changes_are_visible(self):
        target_change = self.compare('66024e714e75', '66024e714e714e75')
        self.assertTrue(any(b['target_check'] == 'different_or_unresolved'
                            for b in target_change['blocks']['paired']))

        polarity_change = self.compare('66024e714e75', '67024e714e75')
        self.assertTrue(any(b['conditions'] == ['bne', 'beq'] and
                            b['target_check'] == 'different_or_unresolved'
                            for b in polarity_change['blocks']['paired']))

    def test_truncated_instruction_stream_fails_closed(self):
        result = diag.compare_code(bytes.fromhex('4e75'), bytes.fromhex('4e'))
        self.assertEqual(result['status'], 'UNSUPPORTED')
        self.assertIsNone(result['alignment'])
        self.assertEqual(result['decode']['actual']['reason'], 'UNDECODABLE_OR_TRUNCATED')
        for forbidden in ('verdict', 'proof_level', 'promotion', 'equal'):
            self.assertNotIn(forbidden, result)


if __name__ == '__main__':
    unittest.main()
