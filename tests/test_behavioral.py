"""BEHAVIORAL_CHAR_RETURN: only byte-return widening may differ; callers read D0.b only."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

import behavioral
from common import FormatError

MOVE_B = '102dfffe'   # move.b -$2(a5),d0
EXT_W = '4880'        # ext.w d0
UNLK_RTS = '4e5d4e75'


def contribution(hex_code, relocations=()):
    return dict(code_hex=hex_code, relocations=list(relocations))


class PredicateTests(unittest.TestCase):
    def test_return_widening_is_the_only_deletion(self):
        expected = bytes.fromhex(MOVE_B + UNLK_RTS)
        reduced, deletions = behavioral.reduced_contribution(expected, contribution(MOVE_B + EXT_W + UNLK_RTS))
        self.assertEqual(bytes.fromhex(reduced['code_hex']), expected)
        self.assertEqual([d['raw'] for d in deletions], [EXT_W])

    def test_branch_across_deletion_is_reencoded_and_relocations_shift(self):
        # bra.b to the epilogue crosses the widening in the candidate only.
        expected = bytes.fromhex('6004' + MOVE_B + UNLK_RTS)
        actual = '6006' + MOVE_B + EXT_W + UNLK_RTS
        reloc = dict(relative_offset=8, type='HUNK_RELOC32', width=4, target_hunk=1, addend_raw=0)
        reduced, _ = behavioral.reduced_contribution(expected, contribution(actual, [reloc]))
        self.assertEqual(bytes.fromhex(reduced['code_hex']), expected)
        self.assertEqual(reduced['relocations'][0]['relative_offset'], 6)

    def test_any_other_difference_rejects(self):
        expected = bytes.fromhex(MOVE_B + UNLK_RTS)
        for actual in ('7000' + MOVE_B + UNLK_RTS,            # extra instruction
                       '302dfffe' + EXT_W + UNLK_RTS,           # word load, not a byte return
                       MOVE_B + UNLK_RTS):                      # nothing to delete: use check_function
            with self.subTest(actual=actual), self.assertRaises(FormatError):
                behavioral.reduced_contribution(expected, contribution(actual))

    def test_widening_off_the_return_path_rejects(self):
        # The original keeps using D0 after the byte load (nop stands in), so the
        # widening is observable inside the function and is not a return widening.
        expected = bytes.fromhex(MOVE_B + '4e71' + UNLK_RTS)
        with self.assertRaises(FormatError):
            behavioral.reduced_contribution(expected, contribution(MOVE_B + EXT_W + '4e71' + UNLK_RTS))


class CallerTests(unittest.TestCase):
    def caller(self, tail):
        raw = '4eb900000000' + tail     # jsr $0.l
        return dict(id='caller', start=0x100, raw_bytes=raw)

    def callee(self):
        return dict(id='callee', callers=[dict(id='caller', site=0x100)])

    def test_byte_store_then_redefinition_is_accepted(self):
        functions = [self.caller('1b40ffff' + '7000' + '4e75')]   # move.b d0,-1(a5); moveq #0,d0; rts
        self.assertEqual(behavioral.byte_only_callers(self.callee(), functions), [dict(caller='caller', site=0x100)])

    def test_word_or_long_read_of_widened_bits_rejects(self):
        for tail in ('3b40fffe4e75',            # move.w d0,-2(a5)
                     '4a804e75',                # tst.l d0
                     '1b40ffff4e75'):           # returns D0 with untrusted upper bits
            with self.subTest(tail=tail), self.assertRaises(FormatError):
                behavioral.byte_only_callers(self.callee(), [self.caller(tail)])

    def test_branches_are_followed(self):
        # beq.b over a byte use; both paths redefine D0 before any wide read.
        tail = '6704' + '1b40ffff' + '7000' + '4e75'
        self.assertTrue(behavioral.byte_only_callers(self.callee(), [self.caller(tail)]))


class CanonicalTests(unittest.TestCase):
    def test_accepted_entries_validate_and_are_never_exact_c(self):
        ledger = json.loads((ROOT / 'recovery/ledger.json').read_text())
        entries = ledger.get(behavioral.MAP, {})
        if not entries:
            self.skipTest('no behavioral entries accepted yet')
        analysis = json.loads((ROOT / 'evidence/functions/ledger.json').read_text())
        by = {f['id']: f for f in analysis['functions']}
        for fid, item in entries.items():
            with self.subTest(fid=fid):
                self.assertNotIn(fid, ledger['functions'])
                proof = behavioral.validate(ROOT, by[fid], item, analysis)
                self.assertEqual(proof['state'], behavioral.STATE)


if __name__ == '__main__':
    unittest.main()
