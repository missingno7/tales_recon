import json
import sys
sys.path.insert(0, 'tools')
import unit_diag
receipt_path, key = sys.argv[1:3]
r = json.load(open(receipt_path, encoding='utf-8'))
ids = [m['id'] for m in r['ordered_members']]
old = unit_diag.diag.compare_code
captured = []
def capture(e,a,**kw):
    z=old(e,a,**kw); captured.append(z); return z
unit_diag.diag.compare_code = capture
report=unit_diag.diagnose_unit(ids,key,entry_member=r.get('id'),interval=tuple(r['natural_interval']['interval']),new_members=sorted(r.get('member_sources',{})))
for i,m in enumerate(report['members']):
    if False and m['id']=='ov11_F_4EC6':
        c=captured[i]
        print(json.dumps({'id':m['id'],'hypotheses':c.get('hypotheses'),'reference_identity':c.get('reference_identity')},default=str))
    if False and m['id']=='ov11_F_487E':
        b=captured[i].get('blocks',{})
        print(json.dumps({'id':m['id'],'blocks':b},default=str))
    if m['id']=='ov11_F_51C0':
        b=captured[i].get('blocks',{})
        print(json.dumps({'id':m['id'],'blocks':b},default=str))
