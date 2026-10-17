from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().with_name('game_build.py')
if not SOURCE.is_file():
    SOURCE = Path(__file__).resolve().parents[1] / 'tools' / 'game_build.py'
spec = importlib.util.spec_from_file_location('game_build_under_test', SOURCE)
game_build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(game_build)


class GameBuildPureTests(unittest.TestCase):
    def test_selection_filters_unaccepted_old_66fe_and_provider_overlap(self):
        inv = {'sources': [
            {'source': 'src/recovered/ov11/ov11_F_66FE.c', 'selected': True, 'source_sha256': 'old', 'profiles': ['aztec36']},
            {'source': 'src/recovered/complete-c/ov11_F_66FE.c', 'selected': True, 'source_sha256': 'c66', 'profiles': ['aztec36-large-data']},
            {'source': 'src/recovered/data/g_data.c', 'selected': True, 'source_sha256': 'data', 'profiles': ['aztec36']},
            {'source': 'src/recovered/ov11/ov11_F_1111.c', 'selected': True, 'source_sha256': 'fn', 'profiles': ['aztec36-x3']},
        ]}
        ledger = {
            'functions': {'ov11_F_66FE': {'source': 'src/recovered/ov11/ov11_F_66FE.c', 'source_sha256': 'old'}},
            'mixed_source_objects': {'complete_c_66FE': {'source': 'src/recovered/complete-c/ov11_F_66FE.c', 'source_sha256': 'c66'}},
            'behavioral_functions': {'ov11_F_1111': {'source': 'src/recovered/ov11/ov11_F_1111.c', 'source_sha256': 'fn'}},
            'data_providers': {'g_data': {'source': 'src/recovered/data/g_data.c'}},
            'code_data_providers': {},
        }
        src_rows, overlaps, providers = game_build.select_accepted_sources(
            inv, ledger, Path('.'), lambda _path, _root: True,
            lambda path: {'src/recovered/complete-c/ov11_F_66FE.c': 'c66', 'src/recovered/ov11/ov11_F_1111.c': 'fn'}[path.as_posix()])
        self.assertEqual([row['source'] for row in src_rows], [
            'src/recovered/complete-c/ov11_F_66FE.c', 'src/recovered/ov11/ov11_F_1111.c'])
        self.assertEqual(src_rows[0]['profiles'], ['aztec36-large-data'])
        self.assertEqual(src_rows[1]['profiles'], ['aztec36-x3'])
        self.assertEqual(overlaps, ['src/recovered/data/g_data.c'])
        self.assertEqual(providers, {'src/recovered/data/g_data.c'})

    def test_unit_container_is_rejected_even_if_accepted(self):
        inv = {'sources': [{'source': 'src/recovered/units/ov11_unit.c', 'selected': True, 'source_sha256': 'u'}]}
        ledger = {'functions': {'unit': {'source': 'src/recovered/units/ov11_unit.c', 'source_sha256': 'u'}}}
        with self.assertRaisesRegex(ValueError, 'unit-container'):
            game_build.select_accepted_sources(inv, ledger, Path('.'), lambda _path, _root: True, lambda _path: 'u')

    def test_worker_job_names_are_safe_and_ledger_scoped(self):
        job = game_build.unique_job_name('abcdef1234567890', Path('build/worker-jobs'))
        self.assertTrue(job.startswith('luna-game-build-abcdef123456'))
        self.assertEqual(game_build.unique_job_name('a'*64, Path('build/worker-jobs'), 'explicit_job-1'), 'explicit_job-1')
        with self.assertRaisesRegex(ValueError, 'only letters'):
            game_build.unique_job_name('a'*64, Path('build/worker-jobs'), '../bad')

    def test_data_provider_source_can_only_be_selected_once(self):
        rows = game_build.unique_data_provider_rows({'data_providers': {
            'a': {'source': 'src/data/a.c'}, 'b': {'source': 'src/data/b.c'}}})
        self.assertEqual([row[0] for row in rows], ['a', 'b'])
        with self.assertRaisesRegex(ValueError, 'selected more than once'):
            game_build.unique_data_provider_rows({'data_providers': {
                'a': {'source': 'src/data/a.c'}, 'b': {'source': 'src/data/a.c'}}})

    def test_entry_names_are_unique_case_insensitively(self):
        self.assertTrue(game_build.assert_unique_entry_names(['obj_a.o', 'obj_b.o']))
        with self.assertRaisesRegex(ValueError, 'duplicate staged entry names'):
            game_build.assert_unique_entry_names(['Objects/One.o', 'objects/one.O'])

    def test_typed_alias_views_keep_array_address_semantics(self):
        expr, dims = game_build.alias_view_expression('unsigned char [6]', '_G_h01_4528', 3, (6,))
        self.assertEqual(expr, '((unsigned char *)((char *)&G_h01_4528 + 3))')
        self.assertEqual(dims, (6,))
        scalar, dims = game_build.alias_view_expression('unsigned short', '_G_h01_1234', 2)
        self.assertEqual(scalar, '(*(unsigned short *)((char *)&G_h01_1234 + 2))')
        self.assertEqual(dims, ())
        with self.assertRaises(ValueError):
            game_build.alias_view_expression('UNKNOWN', '_G_h01_1234', 2)

    def test_missing_symbol_derivation_excludes_accepted_alias_and_code(self):
        rows = [
            {'symbol': '_G_data', 'cause': 'UNDEFINED_BSS_GLOBAL'},
            {'symbol': '_G_alias', 'cause': 'UNDEFINED_INITIALIZED_DATA'},
            {'symbol': '_G_planned', 'cause': 'UNDEFINED_BSS_GLOBAL'},
            {'symbol': '_F_missing', 'cause': 'UNDEFINED_CODE'},
        ]
        missing = game_build.derive_missing_symbols(rows, {'_G_data'}, {'_G_alias': ('_G_base', 4)}, {'_G_planned': ('_G_target', 4, 'DATA', 'interior')})
        self.assertEqual([row['symbol'] for row in missing], ['_G_planned'])

    def test_report_states_stub_free_and_stub_bytes(self):
        clean = game_build.format_build_report({}, [], [], [], 0)
        self.assertIn('STUB_FREE: YES', clean)
        self.assertIn('Objects by proof category:', clean)
        stubbed = game_build.format_build_report({},
            [{'symbol': '_G_missing', 'bytes': 6, 'cause': 'UNDEFINED_BSS_GLOBAL'}],
            [{'object': 'link_stub_bss_00.o', 'symbols': ['_G_missing']}], [], 6)
        self.assertIn('link_stub_bss_00.o: 6 bytes', stubbed)
        self.assertIn('_G_missing: 6 bytes', stubbed)
        self.assertIn('STUB_FREE: NO', stubbed)


if __name__ == '__main__':
    unittest.main()


def test_command_groups_pair_each_compile_with_its_assembly_step():
    import game_build
    commands = ['C:FailAt 1000000',
                'Old2:bin/lb Old1:lib/c.lib -x crt0 >crt0-extract.log',
                'Old1:bin/cc <compiler-input.txt >a-cc.log -a tu/a.c',
                'Old1:bin/as <compiler-input.txt >a-as.log -o a.o tu/a.asm',
                'Old1:bin/as <compiler-input.txt >b-as.log -o b.o b.asm',
                'Old1:bin/ln <compiler-input.txt >link-ln.log -m -t -o DuckTales -f link.lnk']
    groups, link = game_build.command_groups(commands)
    assert link.startswith('Old1:bin/ln')
    assert [len(g) for g in groups] == [1, 2, 1]
    assert groups[1][0].endswith('tu/a.c') and groups[1][1].endswith('tu/a.asm')


def test_numeric_a4_displacement_is_rewritten_to_the_original_layout_symbol():
    import game_build
    source = '\tfar data\n\tdseg\n\tcseg\n_x\n\tlea.l -$2c5c(a4),a1\n\trts\n\tend\n'
    out = game_build.symbolize_a4_displacements(source, {0x53A2: 'G_h01_53A2'}, 'obj')
    assert 'lea.l _G_h01_53A2,a1' in out and '\tpublic _G_h01_53A2\n' in out
    assert '(a4)' not in out
