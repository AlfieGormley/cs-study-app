import json,hashlib
from pathlib import Path
P=Path('docs/audit-systems-full.json')
r=json.loads(P.read_text()) if P.exists() else {'date':'2026-10-05','agent':'audit_systems','scope':['content/os','content/networks','content/security','content/architecture'],'coverage':[],'findings':[],'limitations':['Full semantic reading is recorded per file; primary-source checks and code execution are separately documented, not inferred from inventory.']}
def edit(p,old,new,reason,sources):
 p=Path(p);s=p.read_text();assert old in s,(p,old);p.write_text(s.replace(old,new));r['findings'].append({'file':str(p),'original':old,'correction':new,'reason':reason,'sources':sources,'confidence':'high'})
def qe(p,id,key,new,reason,sources,option=None):
 p=Path(p);d=json.loads(p.read_text());q=next(x for x in d if x['id']==id);o=q if option is None else q['options'][option];old=o[key];o[key]=new;p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n');r['findings'].append({'file':str(p),'questionId':id,'field':key,'option':option,'original':old,'correction':new,'reason':reason,'sources':sources,'confidence':'high'})
def save(paths):
 for p in paths:
  p=Path(p);r['coverage']=[x for x in r['coverage'] if x['file']!=str(p)];e={'file':str(p),'scope':'Full semantic reading of all fields with selected source checks','sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
  if p.name.endswith('.questions.json'):e['questionIds']=[x['id'] for x in json.loads(p.read_text())]
  r['coverage'].append(e)
 P.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
