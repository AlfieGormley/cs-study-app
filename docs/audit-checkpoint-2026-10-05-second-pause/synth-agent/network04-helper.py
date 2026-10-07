from pathlib import Path
import json
r=Path('content/networks/04-application');report=Path('docs/audit-networks-application.json')
if not report.exists():report.write_text(json.dumps({'date':'2026-10-05','status':'Independent verification in progress; no stamp yet.','coverage':{'lessons':0,'questions':0,'full_read_files':[]},'findings':[],'sources':[],'omissions':[],'tests':[]},indent=2)+'\n')
def rec(p,old,new,why,qid=None):
 d=json.loads(report.read_text());f={'file':str(p),'original':old,'correction':new,'reason':why,'confidence':'high'}
 if qid:f['question']=qid
 d['findings'].append(f);report.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def md(n,old,new,why):
 p=r/(n+'.md');s=p.read_text();assert old in s;p.write_text(s.replace(old,new));rec(p,old,new,why)
def q(n,i,path,new,why):
 p=r/(n+'.questions.json');d=json.loads(p.read_text());t=d[i-1]
 for k in path[:-1]:t=t[k]
 old=t[path[-1]];assert old!=new;t[path[-1]]=new;p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');rec(p,old,new,why,d[i-1]['id'])
def qr(n,i,path,old,new,why):
 t=json.loads((r/(n+'.questions.json')).read_text())[i-1]
 for k in path:t=t[k]
 assert old in t;q(n,i,path,t.replace(old,new),why)
def coverage(n):
 d=json.loads(report.read_text());files=[str(r/(n+'.md')),str(r/(n+'.questions.json'))]
 if files[0]not in d['coverage']['full_read_files']:
  d['coverage']['full_read_files']+=files;d['coverage']['lessons']+=1;d['coverage']['questions']+=len(json.loads((r/(n+'.questions.json')).read_text()))
 report.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
