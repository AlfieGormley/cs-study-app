import pathlib,re,json,subprocess,io,contextlib,types,datetime,sqlite3
root=pathlib.Path('content/languages/01-paradigms');res=[];expected={'para-imperative-declarative-q3':'42','para-functional-basics-q3':'14\n0','para-oop-q5':'DBCA','para-scope-closures-q1':'3 1','para-scope-closures-q3':'[2, 2, 2]','para-scope-closures-q5':'[0, 1]','para-scope-closures-q6':"['a', 'b']",'para-scope-closures-q9':'[1, 3] 1','para-multi-paradigm-q9':"Cart(items=['tea'])"}
items=[]
for p in root.glob('*.md'):items.append((p.name,p.read_text()))
for p in root.glob('*.questions.json'):
 for q in json.loads(p.read_text()):
  for k,v in q.items():
   if isinstance(v,str):items.append((q['id']+':'+k,v))
for label,s in items:
 for i,(lang,code) in enumerate(re.findall(r'```(\w+)\n(.*?)```',s,re.S)):
  if lang not in ['python','javascript','bash','sql']:continue
  if 'Order.objects' in code or '<p>' in code or 'signal(' in code:
   res.append({'label':label,'status':'framework-dependent, inspected not executed'});continue
  scope={'nums':[3,4,7,10,1],'cart':[],'item':'tea'};out=io.StringIO()
  try:
   if lang=='python':
    with contextlib.redirect_stdout(out):exec(compile(code,label,'exec'),scope)
    if 'Account' in scope:
     a=scope['Account']();a.deposit(100);a.withdraw(30);assert a.balance==70
     for bad in [-1,0,float('nan'),True]:
      for method in [a.deposit,a.withdraw]:
       try:method(bad);raise AssertionError('invalid accepted')
       except (ValueError,TypeError):pass
    if 'outer' in scope:assert scope['outer']()=='enclosing'
    if 'Config' in scope:
     try:scope['Config']().get();raise AssertionError('expected NameError')
     except NameError:pass
    if 'apply_discount' in scope:assert scope['apply_discount'](types.SimpleNamespace(total=100),datetime.date(2026,10,2))==90
    if 'f' in scope and 'print(x)' in code:
     try:scope['f']();raise AssertionError('expected UnboundLocalError')
     except UnboundLocalError:pass
   elif lang=='sql':
    db=sqlite3.connect(':memory:');db.execute('create table nums(n integer)');db.executemany('insert into nums values(?)',[(3,),(4,),(7,),(10,),(1,)]);assert db.execute(code).fetchone()[0]==116;db.execute('delete from nums');assert db.execute(code).fetchone()[0]==0
   else:
    prefix='const nums=[3,4,7,10,1]; const xs=[-1,2];\n' if lang=='javascript' else ''
    result=subprocess.run(['node','-e',prefix+code] if lang=='javascript' else ['bash','-c',code],capture_output=True,text=True,timeout=10);assert result.returncode==0,result.stderr;out.write(result.stdout)
   qid=label.split(':')[0]
   if qid in expected and label.endswith(':prompt'):assert out.getvalue().strip()==expected[qid],(label,out.getvalue())
   res.append({'label':label,'language':lang,'status':'pass','output':out.getvalue()})
  except (RecursionError,UnboundLocalError) as exc:
   assert 'rsum' in code or 'total = total + 1' in code;res.append({'label':label,'status':'expected '+type(exc).__name__})
pathlib.Path('/tmp/test-para-results.json').write_text(json.dumps(res,indent=2));print('PASS',len(res),'groups',sum(x['status']=='pass' for x in res),'executed normally')
