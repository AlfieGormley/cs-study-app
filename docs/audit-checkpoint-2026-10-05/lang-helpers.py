import json,pathlib,copy,hashlib
root=pathlib.Path('content/languages/01-paradigms');reportpath=pathlib.Path('docs/audit-languages.json')
report=json.loads(reportpath.read_text()) if reportpath.exists() else {'scope':'Independent review of languages subject, module by module; reviewed_files is exact completed coverage.','reviewed_files':[],'findings':[],'omissions':[],'limitations':[]}
def save():reportpath.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
def lesson(n,a,b,reason,source):
 p=root/(n+'.md');s=p.read_text();assert a in s,a;p.write_text(s.replace(a,b));report['findings'].append({'file':str(p),'original':a,'correction':b,'reason':reason,'source_urls':source if isinstance(source,list) else [source],'confidence':'high'});save()
def edit(n,num,reason,source,fn):
 p=root/(n+'.questions.json');data=json.loads(p.read_text());q=data[num-1];before=copy.deepcopy(q);fn(q);assert q!=before;p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');report['findings'].append({'file':str(p),'question_id':q['id'],'original':before,'correction':q,'reason':reason,'source_urls':source if isinstance(source,list) else [source],'confidence':'high'});save()
def replace(q,a,b):
 s=json.dumps(q,ensure_ascii=False);assert a in s,a;s=s.replace(a,b);q.clear();q.update(json.loads(s))
def fields(q,**kw):q.update(kw)
def opt(q,i,text=None,explanation=None):
 if text is not None:q['options'][i]['text']=text
 if explanation is not None:q['options'][i]['explanation']=explanation
def done(n):
 for ext in ['.md','.questions.json']:
  f=str(root/(n+ext))
  if f not in report['reviewed_files']:report['reviewed_files'].append(f)
 save()
