import json,sys
sys.path.insert(0,'tools')
import unit_diag
receipt_path,key=sys.argv[1:3]
r=json.load(open(receipt_path,encoding='utf-8'))
ids=[m['id'] for m in r['ordered_members']]
original=unit_diag.diag.compare_code
captured=[]
def capture(e,a,**kw):
    z=original(e,a,**kw); captured.append(z); return z
unit_diag.diag.compare_code=capture
report=unit_diag.diagnose_unit(ids,key,entry_member=r.get('id'),interval=tuple(r['natural_interval']['interval']),new_members=sorted(r.get('member_sources',{})))
for i,m in enumerate(report['members']):
    if m['id']==sys.argv[3]:
        c=captured[i]
        print(json.dumps({'id':m['id'],'state':m['state'],'expected_only':c['alignment']['expected_only'],'actual_only':c['alignment']['actual_only'],'blocks':c.get('blocks')},default=str))

