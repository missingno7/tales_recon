import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import declaration_views as dv
import fleet


SOURCES = {
    "src/recovered/ov11/a.c": (
        "struct Object { int x; int y; char pad[4]; struct Object *next; };\n"
        "extern int G_h01_94AE; extern struct Object *G_h01_94DA;\n"
        "extern struct Object G_h01_A464[2];\n"
        "extern int F_h00_30F0();\nrecovered() { }\n"),
    "src/recovered/ov11/b.c": (
        "struct Object { int x; int y; struct Object *next; };\n"
        "extern int G_h01_94AE;\nextern struct Object *G_h01_94DA;\nextern void F_h00_30F0();\n"
        "recovered() { }\n"),
    "src/recovered/ov11/c.c": (
        "/* extern long G_h01_94AE; is a comment */\n"
        "extern short G_h01_94AE;\nextern struct Object *G_h01_94DA;\n"
        "struct Object { int x; int y; char pad[4]; struct Object *next; };\n"
        "extern int F_h00_30F0();\nextern short G_h01_8B1C[40][4];\nrecovered() { }\n"),
    # Not canonical: not named by the recovery ledger.
    "src/recovered/ov11/stray.c": "extern long G_h01_94AE;\n",
}


class DeclarationViewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for relative, text in SOURCES.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="ascii")
        ledger = {"functions": {"ov11_F_%04X" % i: {"source": s} for i, s in enumerate(sorted(SOURCES)) if "stray" not in s}}
        (self.root / "recovery").mkdir()
        (self.root / "recovery/ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
        (self.root / "evidence").mkdir()
        access = lambda fid, w: dict(function=fid, width_bytes=w)
        (self.root / "evidence/types.json").write_text(json.dumps(dict(globals=[
            dict(data_hunk_offset=0x94AE, observed_widths_bytes=[2], accesses=[access("t", 2), access("o", 2)],
                 address_taken=[])])), encoding="utf-8")
        self.functions = {"t": dict(
            referenced_data=[dict(kind="A4_RELATIVE", hunk=1, offset=0x94AE, instruction_offset=4),
                             dict(kind="A4_RELATIVE", hunk=1, offset=0x94DA, instruction_offset=8),
                             dict(kind="A4_RELATIVE", hunk=1, offset=0xA46A, instruction_offset=12),
                             dict(kind="A4_RELATIVE", hunk=1, offset=0x0036, instruction_offset=20),
                             dict(kind="A4_RELATIVE", hunk=1, offset=0x1234, instruction_offset=24)],
            direct_callees=[dict(hunk=0, offset=0x30F0, site=20, basis="A4_RELOCATED_JMP_STUB")])}

    def tearDown(self):
        self.temp.cleanup()

    def test_parser_handles_multi_declarator_lines_arrays_and_functions(self):
        externs, structs, unparsed = dv.parse_source(
            "extern int a; extern char *b, c[3];\nextern short d[40][4];\nextern long F();\nextern int (*fp)();\n")
        self.assertEqual([(e["name"], e["view"]) for e in externs],
                         [("a", "int"), ("b", "char *"), ("c", "char [3]"), ("d", "short [40][4]"), ("F", "long ()")])
        self.assertEqual(unparsed, ["int (*fp)()"])
        self.assertEqual(dv.render_declaration("d", "short [40][4]"), "extern short d[40][4];")
        self.assertEqual(dv.render_declaration("p", "struct Object *"), "extern struct Object *p;")
        self.assertEqual(dv.render_declaration("F", "char * ()"), "extern char *F();")

    def test_majority_view_alternatives_structs_and_widths(self):
        views = dv.views_for(["t"], root=self.root, functions=self.functions)
        by = {r["name"]: r for r in views["symbols"]}
        # Only ledger-named sources count; the comment and the stray file do not.
        self.assertEqual(views["canonical_sources"], 3)
        self.assertEqual((by["G_h01_94AE"]["view"], by["G_h01_94AE"]["count"]), ("int", 2))
        self.assertEqual([(a["view"], a["count"]) for a in by["G_h01_94AE"]["alternatives"]], [("short", 1)])
        self.assertEqual(by["G_h01_94AE"]["widths"], dict(program=[2], target=[2], program_accesses=2, address_taken=0))
        self.assertEqual(by["F_h00_30F0"]["declaration"], "extern int F_h00_30F0();")
        self.assertIn("G_h01_94AE", views["conflicting_symbols"])
        # The jump-stub slot at the call site is not a data global.
        self.assertNotIn("G_h01_0036", [m["name"] for m in views["without_canonical_view"]])
        # struct Object: the majority body among sources using the chosen view.
        (obj,) = views["structs"]
        self.assertEqual(obj["definition"], "struct Object { int x; int y; char pad[4]; struct Object *next; };")
        self.assertEqual(obj["uses"], 2)
        self.assertEqual(len(obj["alternatives_among_chosen"]), 1)
        self.assertEqual(views["struct_conflicts"], ["Object"])
        missing = {m["name"]: m for m in views["without_canonical_view"]}
        self.assertEqual(missing["G_h01_A46A"]["within_declared_view"]["name"], "G_h01_A464")
        self.assertEqual(missing["G_h01_A46A"]["within_declared_view"]["displacement"], 6)
        self.assertNotIn("within_declared_view", missing["G_h01_1234"])
        self.assertIn("not historical type provenance", views["policy"])

    def test_struct_size_estimate(self):
        defs = {"Object": "int x; int y; char pad[4]; struct Object *next;", "Odd": "char a; int b; char c;"}
        self.assertEqual(dv.struct_size("Object", defs), 12)
        self.assertEqual(dv.struct_size("Odd", defs), 6)
        self.assertEqual(dv.view_extent("struct Object [2]", defs), 24)
        self.assertEqual(dv.view_extent("short [40][4]", defs), 320)
        self.assertIsNone(dv.view_extent("struct Unknown [1]", defs))

    def test_extern_block_is_paste_ready(self):
        block = dv.extern_block(dv.views_for(["t"], root=self.root, functions=self.functions))
        self.assertIn("candidate views, not provenance", block)
        self.assertIn("extern int G_h01_94AE; /* 2x; alt short x1; w2 */", block)
        self.assertIn("extern struct Object *G_h01_94DA; /* 3x */", block)
        self.assertLess(block.index("struct Object {"), block.index("extern struct Object *G_h01_94DA"))
        self.assertIn("/* G_h01_A46A: inside G_h01_A464+6 (struct Object [2]) */", block)
        self.assertIn("/* G_h01_1234: no canonical view */", block)

    def test_conflict_clusters(self):
        report = dv.conflict_clusters(self.root)
        self.assertEqual(report["struct_tag_variants"], [dict(tag="Object", distinct_bodies=2, sources=3)])
        self.assertEqual(report["top"][0]["cluster"], "G_h01_94xx")
        self.assertGreaterEqual(report["top"][0]["pairwise_conflicts"], 1)


class PacketDeclarationTests(unittest.TestCase):
    VIEWS = dict(symbols=[dict(name="G_h01_94AE")], conflicting_symbols=["G_h01_94AE"], struct_conflicts=[],
                 without_canonical_view=[], structs=[])

    def test_section_points_to_sidecar_and_inlines_block_within_target(self):
        text, block = fleet.declaration_section(dict(self.VIEWS, symbols=[
            dict(name="G_h01_94AE", declaration="extern int G_h01_94AE;", count=2, alternatives=[])]), "experiments/fleet/fn-x")
        self.assertIn("candidate views, not provenance", text)
        self.assertIn("experiments/fleet/fn-x/" + fleet.DECLARATIONS_SIDECAR, text)
        self.assertIn("controlled change", text)
        self.assertIn("extern int G_h01_94AE;", block)
        inline = fleet._clip_block(block, 4000)
        self.assertTrue(inline.startswith("```c\n") and "extern int G_h01_94AE;" in inline)
        self.assertEqual(fleet._clip_block(block, 50), "")

    def test_unavailable_views_never_block_a_packet(self):
        text, block = fleet.declaration_section(dict(status="UNAVAILABLE", reason="boom"), "d")
        self.assertIn("Unavailable: boom", text)
        self.assertEqual(block, "")

    def test_clip_section_prefers_line_ends(self):
        text = "".join("- line %02d xxxxxxxxxx\n" % i for i in range(40))
        clipped = fleet._clip_section(text, 200)
        self.assertLessEqual(len(clipped), 260)
        self.assertTrue(clipped.split("\n")[-3].endswith("xxxxxxxxxx"))
        self.assertIn("clipped", clipped)
        self.assertEqual(fleet._clip_section("short\n", 200), "short\n")


if __name__ == "__main__":
    unittest.main()
