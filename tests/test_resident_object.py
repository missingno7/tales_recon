import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from common import FormatError, sha256
from compiler_oracle import extract, identity
from check_unit import compare_unit
from analysis_support import decoder, K
from hunk import parse
from overlay_experiment import symbols
from resident_object import bounds, first_function
import link_line

FIXTURE = Path(__file__).parent / 'fixtures/resident-object'


class ResidentObjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'control'; shutil.copytree(FIXTURE, self.root)
        self.model = parse((self.root / 't000.exe').read_bytes())
        self.symbols = symbols((self.root / 't000.sym').read_text())

    def check_bounds(self, model=None, sy=None):
        return bounds(self.root, 't000', ['candidate'], model or self.model,
                      sy or self.symbols, 'recovered')

    def test_retained_control_is_object_bounded_not_whole_root(self):
        pins = json.loads((self.root / 'provenance.json').read_text())
        for item in pins['artifacts']:
            self.assertEqual(sha256((self.root / item['path']).read_bytes()), item['sha256'])
        c = extract(self.root, 't000', resident=True)
        self.assertEqual((c['hunk'], c['code_offset'], c['code_size']), (0, 12, 10))
        self.assertEqual(c['code_hex'], '4e55000070074e5d4e75')
        self.assertNotIn('entry_offset', c)
        self.assertLess(c['code_size'], c['hunks'][0]['initialized_size'])
        with self.assertRaisesRegex(FormatError, 'overlay contribution'):
            extract(self.root, 't000')

    def test_data_labels_and_unnamed_code_are_not_function_boundaries(self):
        self.assertEqual(first_function(self.root / 'h000.asm'), '_main')
        p = self.root / 't000.asm'; p.write_text('\tdc.w 0\n' + p.read_text())
        with self.assertRaisesRegex(FormatError, 'anonymous leading CODE'):
            self.check_bounds()

    def test_changed_harness_size_and_object_order_reject(self):
        p = self.root / 'h000.o'; raw = bytearray(p.read_bytes())
        raw[10:14] = (12).to_bytes(4, 'big'); p.write_bytes(raw)
        with self.assertRaisesRegex(FormatError, 'order/boundary'):
            self.check_bounds()

    def test_inflated_source_extent_cannot_absorb_bootstrap(self):
        p = self.root / 't000.o'; raw = bytearray(p.read_bytes())
        raw[10:14] = (12).to_bytes(4, 'big'); p.write_bytes(raw)
        with self.assertRaisesRegex(FormatError, 'absorbs another'):
            self.check_bounds()

    def test_wrong_root_entry_and_crossing_relocation_reject(self):
        sy = dict(self.symbols); sy[(0, '_recovered')] = 11
        with self.assertRaisesRegex(FormatError, 'order/boundary'):
            self.check_bounds(sy=sy)
        model = copy.deepcopy(self.model); model['hunks'][0]['node'] = 'ov03'
        with self.assertRaisesRegex(FormatError, 'root CODE'):
            self.check_bounds(model=model)
        model = copy.deepcopy(self.model)
        model['relocations'].append(dict(source_hunk=0, source_offset=20, width=4))
        with self.assertRaisesRegex(FormatError, 'straddles'):
            self.check_bounds(model=model)

    def test_root_link_omits_empty_overlay_and_keeps_real_proxy_return(self):
        meta = dict(library_guest='Old1:', library='c.lib')
        self.assertEqual(link_line.direct_arguments('t000', 'h000', 0, ['t000'], [], meta),
                         '-m -t -o t000.exe h000.o t000.o Old1:lib/c.lib')
        text = link_line.argument_file_text('h000', 0, ['t000'], ['+o1', 'p000.o'], meta)
        self.assertEqual(text, 'h000.o\nt000.o\n+o1\np000.o\n+o0\nOld1:lib/c.lib\n')
        root = identity('recovered(){return 7;}', 'aztec36-x3', 0)
        overlay = identity('recovered(){return 7;}', 'aztec36-x3')
        self.assertNotEqual(root[0], overlay[0])
        self.assertIn('resident_object_extractor_sha256', root[1])
        self.assertNotIn('resident_object_extractor_sha256', overlay[1])

    def test_root_unit_uses_physical_base_without_remapping_harness(self):
        c = extract(self.root, 't000', resident=True)
        raw = bytes.fromhex(c['code_hex'])
        f = dict(id='resident_F_0100', hunk=0, node='resident', start=256,
                 end=266, size=10, raw_bytes=raw.hex(), sha256=sha256(raw),
                 extent_status='CLOSED_CFG', referenced_data=[], direct_callees=[],
                 relocations=[], jump_tables=[])
        compiled = dict(status='COMPILED', identity=dict(profile='aztec36-x3', flags=['+X3']),
                        cache_key='synthetic-control', cache_hit=True, directory=str(self.root),
                        prefix='t000', contribution=c)
        context = dict(root=self.root, ledger=dict(functions={}))
        for gaps in (False, True):
            with self.subTest(gaps=gaps):
                result = compare_unit([f], {f['id']:'recovered'}, compiled, 32766,
                                      allow_gaps=gaps, source_text='recovered(){return 7;}',
                                      context=context)
                self.assertEqual(result['verdict'], 'EQUAL')
        broken = copy.deepcopy(compiled)
        broken['contribution']['symbols'] = [dict(s, offset=0) if s['name']=='_recovered' else s
                                              for s in c['symbols']]
        with self.assertRaisesRegex(FormatError, 'ordering/extent'):
            compare_unit([f], {f['id']:'recovered'}, broken, 32766,
                         source_text='recovered(){return 7;}', context=context)

    def test_root_unit_keeps_external_callee_and_global_coordinates(self):
        fixture = FIXTURE.parent / 'resident-reference'
        c = extract(fixture, 't000', resident=True)
        raw = bytes.fromhex(c['code_hex']); expected = bytearray(raw)
        calls = []; refs = []
        for ins in decoder().disasm(raw, 0):
            if ins.mnemonic == 'jsr':
                expected[ins.address+2:ins.address+4] = (512-256-ins.address-2).to_bytes(2, 'big', signed=True)
                calls.append(dict(id='resident_F_0200', hunk=0, offset=512, site=256+ins.address))
            for operand in ins.operands:
                if operand.type == K.M68K_OP_MEM and operand.mem.base_reg == K.M68K_REG_A4:
                    at = bytes(ins.bytes).index((operand.mem.disp & 65535).to_bytes(2, 'big'), 2)
                    expected[ins.address+at:ins.address+at+2] = (256-32766).to_bytes(2, 'big', signed=True)
                    refs.append(dict(kind='A4_RELATIVE', hunk=1, offset=256))
        self.assertEqual(len(calls), 1); self.assertEqual(len(refs), 1)
        f = dict(id='resident_F_0100', hunk=0, node='resident', start=256,
                 end=256+len(raw), size=len(raw), raw_bytes=expected.hex(), sha256=sha256(expected),
                 extent_status='CLOSED_CFG', referenced_data=refs, direct_callees=calls,
                 relocations=[], jump_tables=[])
        compiled = dict(status='COMPILED', identity=dict(profile='aztec36-x3', flags=['+X3']),
                        cache_key='synthetic-reference-control', cache_hit=True, directory=str(fixture),
                        prefix='t000', contribution=c)
        source = (fixture / 't000.c').read_text()
        for gaps in (False, True):
            result = compare_unit([f], {f['id']:'recovered'}, compiled, 32766, allow_gaps=gaps,
                                  source_text=source, context=dict(root=fixture, ledger=dict(functions={})))
            self.assertEqual(result['verdict'], 'EQUAL')
            self.assertTrue(any(p['kind']=='PC_RELATIVE_CALL_SYMBOL' for p in result['members'][0]['relocation_proof']))
