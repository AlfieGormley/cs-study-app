import json
from pathlib import Path
base=Path('content/networks/03-tcp')
finding=Path('/tmp/audit-system-design/network03-findings.json')
rows=json.loads(finding.read_text()) if finding.exists() else []
def save():finding.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
def edit(n,old,new,reason,sources=[]):
 p=base/(n+'.md');s=p.read_text();assert old in s,(n,old);p.write_text(s.replace(old,new));rows.append(dict(file=str(p),original=old,correction=new,reason=reason,sources=sources,confidence='high'));save()
def qedit(n,num,field,new,reason,sources=[]):
 p=base/(n+'.questions.json');a=json.loads(p.read_text());q=a[num-1];o=q
 keys=field.split('.')
 for k in keys[:-1]:o=o[int(k)] if isinstance(o,list) else o[k]
 k=keys[-1];k=int(k) if isinstance(o,list) else k;old=o[k];assert old!=new;o[k]=new
 p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n');rows.append(dict(file=str(p),question_id=q['id'],field=field,original=old,correction=new,reason=reason,sources=sources,confidence='high'));save()
def qreplace(n,num,field,old,new,reason,sources=[]):
 a=json.loads((base/(n+'.questions.json')).read_text());o=a[num-1]
 for k in field.split('.'):o=o[int(k)] if isinstance(o,list) else o[k]
 assert old in o,(n,num,field,old);qedit(n,num,field,o.replace(old,new),reason,sources)
rfc=lambda n:['https://www.rfc-editor.org/rfc/rfc'+str(n)+'.html']
