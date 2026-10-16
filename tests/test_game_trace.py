from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys

PAYLOAD=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PAYLOAD/"tools"))
import game_trace as gt

FIXTURE=PAYLOAD/"tests"/"fixtures"/"trace"/"decoder-values.json"

def test_decoder_fixture_covers_int16_long_ffp_and_struct_fields():
    fixture=json.loads(FIXTURE.read_text(encoding="utf-8"))
    raw=bytes.fromhex(fixture["hex"]);expected=fixture["expected"]
    assert gt.decode_value(raw[:2],"int",{})["value"]==expected["int16"]
    assert gt.decode_value(raw[2:6],"long",{})["value"]==expected["long"]
    assert gt.decode_value(raw[6:10],"float",{})["value"]==expected["ffp"]
    structs={"Pair":{"size":6,"fields":[{"name":"first","type":"int","offset":0},{"name":"second","type":"long","offset":2}]}}
    pair=gt.decode_value(bytes.fromhex(fixture["pair_hex"]),"struct Pair",structs)
    assert pair["fields"]["first"]["value"]==-2
    assert pair["fields"]["second"]["value"]==expected["long"]
    assert pair["raw"]==fixture["pair_hex"]

def test_input_validation_accepts_ordered_joystick_events_and_rejects_bad_ranges():
    events=[{"frame":0,"event":"JOY2_FIRE_BUTTON","value":1},{"frame":3,"event":"JOY2_RIGHT","value":0}]
    assert gt.validate_input(events,4)==events
    for bad in ([{"frame":4,"event":"JOY2_RIGHT","value":1}],
                [{"frame":2,"event":"JOY2_RIGHT","value":1},{"frame":1,"event":"JOY2_RIGHT","value":0}],
                [{"frame":0,"event":"SPC_STATESAVE","value":1}],
                [{"frame":0,"event":"JOY2_RIGHT","value":True}]):
        try: gt.validate_input(bad,4)
        except (gt.TraceError,ValueError): pass
        else: raise AssertionError(f"invalid event stream accepted: {bad}")

def test_schema_is_derived_from_model_and_semantic_names(tmp_path):
    data={"globals":{"G_h1_0010":{"type":"int","extent":2,"basis":"CURATED"},
                      "G_h2_0000":{"type":"unsigned long","extent":4,"basis":"CURATED"},
                      "G_h3_0000":{"type":"int","extent":2}},"structs":{"Pair":{"size":6,"fields":[]}}}
    names={"globals":{"G_h1_0010":{"name":"score"}}}
    d,n=tmp_path/"data.json",tmp_path/"names.json"
    d.write_text(json.dumps(data),encoding="utf-8");n.write_text(json.dumps(names),encoding="utf-8")
    schema=gt.make_schema(d,n)
    assert [(g["id"],g["frame_offset"]) for g in schema["globals"]]==[("G_h1_0010",16),("G_h2_0000",46044)]
    assert schema["globals"][0]["name"]=="score"
    assert schema["structs"]==data["structs"]

def test_compare_reports_first_resident_byte_divergence(tmp_path):
    gt.select_root(tmp_path)
    left,right=tmp_path/"left",tmp_path/"right";left.mkdir();right.mkdir()
    schema={"frame_bytes":gt.FRAME_BYTES,"globals":[{"id":"G_h1_0010","frame_offset":10,"extent":2}],"structs":{}}
    meta={"frame_bytes":gt.FRAME_BYTES,"count":1,"checkpoint_sha256":"c","input_sha256":"i","schema_sha256":"s","boundary":"vblank"}
    row={"frame":0,"offset":0,"sha256":"","overlay":None,"overlay_basis":"UNRESOLVED","loaded":{},"pc":100,
         "beam":[0,0],"chip_cycles":None,"cia_a_tod":1,"cycle_clock":1,"callers":[],"interrupted":None}
    a=bytearray(gt.FRAME_BYTES);b=bytearray(gt.FRAME_BYTES);b[11]=7
    for folder,raw in ((left,a),(right,b)):
        (folder/"trace-schema.json").write_text(json.dumps(schema),encoding="utf-8")
        (folder/"trace-meta.json").write_text(json.dumps(meta),encoding="utf-8")
        row_copy=dict(row,sha256=hashlib.sha256(raw).hexdigest())
        (folder/"index.jsonl").write_text(json.dumps(row_copy)+"\n",encoding="utf-8")
        (folder/"trace.bin").write_bytes(raw)
        (folder/"named.jsonl").write_text("{}\n",encoding="utf-8")
    result=gt.compare("left","right")
    assert result["identical"] is False
    assert result["first_divergence"]=={"frame":0,"frame_offset":11,"hunk":1,"hunk_offset":11,"a":0,"b":7,
                                         "globals":[{"id":"G_h1_0010","frame_offset":10,"extent":2}]}

def test_run_paths_cannot_escape_the_output_root(tmp_path):
    try: gt.run_path(tmp_path, '../escape')
    except ValueError: pass
    else: raise AssertionError('path traversal run name accepted')
