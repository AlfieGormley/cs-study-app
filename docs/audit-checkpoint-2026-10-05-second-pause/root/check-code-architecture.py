import ast,contextlib,io,json,os,re,sqlite3,subprocess,sys,tempfile,types,warnings
from pathlib import Path
from decimal import Decimal
ROOT=Path('/Users/alfiegormley/Github/cs-study-app');B=ROOT/'content/software-engineering/05-code-architecture'
checks=0;blocks=0

def check(x):
 global checks
 assert x
 checks+=1

def raises(kind,f):
 try:f()
 except kind:return check(True)
 raise AssertionError(f'expected {kind}')

def fences(name,lang='python'):
 return re.findall(r'```'+lang+r'\n([\s\S]*?)```',(B/(name+'.md')).read_text())

def run(code,ns):
 global blocks
 exec(compile(code,'<lesson>', 'exec'),ns);blocks+=1

app=types.SimpleNamespace(post=lambda path:lambda f:f)
# Layered snippets execute against in-memory SQLite, with explicit shared wiring.
ns={'app':app,'request':types.SimpleNamespace(json={'code':'WINTER5'})}
conn=sqlite3.connect(':memory:');conn.row_factory=sqlite3.Row
conn.execute('create table orders(id integer primary key,total text,status text)')
conn.execute("insert into orders values(1,'100.00','open')");ns['db']=conn
s=fences('sea-layered');run(s[0],ns)
raises(UnboundLocalError,lambda:ns['apply_discount'](1))
for code in s[1:4]:run(code,ns)
repo=ns['SqlOrderRepository'](conn);ns['repo']=repo
ns['services']=types.SimpleNamespace(apply_discount=ns['apply_discount']);run(s[4],ns)
check(ns['discount_view'](1)[1]==400)
ns['request'].json={'code':'SPRING10'}
check(ns['discount_view'](1)=={'total':'90.000'})
check(conn.execute('select total from orders').fetchone()[0]=='90.000')
check(ns['discount_view'](99)[1]==404)
for value in ['NaN','Infinity',-1,101]:raises(ValueError,lambda value=value:ns['Order'](2,Decimal('10'),'open').apply_discount(value))
conn.execute("update orders set status='closed'");check(ns['discount_view'](1)[1]==409)
# Hexagonal snippets have a documented external ORM mapping/session dependency.
ns={'app':app};s=fences('sea-hexagonal')
for code in s[:3]:run(code,ns)
core=types.ModuleType('core');model=types.ModuleType('core.model');model.Order=ns['Order'];sys.modules['core']=core;sys.modules['core.model']=model
class Row:pass
ns['OrderRow']=Row
run(s[3],ns)
row=types.SimpleNamespace(id=1,status='draft')
session=types.SimpleNamespace(get=lambda cls,key:row if key==1 else None)
r=ns['SqlOrderRepository'](session);o=r.get(1);o.place();r.add(o);check(row.status=='placed');raises(LookupError,lambda:r.get(2))
for code in s[4:6]:run(code,ns)
ns['test_place_order_notifies']();check(True)
raises(ValueError,lambda:o.place())
ns.update(make_session=lambda url:session,SmtpNotifier=lambda settings:ns['FakeNotifier'](),make_flask_app=lambda use:use)
run(s[6],ns);check(callable(ns['build_app'](types.SimpleNamespace(db_url='fixture',smtp='fixture'))))
# DDD examples execute together as presented, without production services.
ns={}
for code in fences('sea-ddd'):run(code,ns)
Money=ns['Money'];Order=ns['Order'];gbp=Money(Decimal('5'),'GBP')
check(gbp+gbp==Money(Decimal('10'),'GBP'))
for value in ['NaN','Infinity','-1']:raises(ValueError,lambda value=value:Money(Decimal(value),'GBP'))
raises(TypeError,lambda:Money(1,'GBP'));raises(ValueError,lambda:gbp+Money(Decimal('1'),'USD'))
raises(TypeError,lambda:hash(ns['Customer'](1,'A')))
o=Order(1,2);raises(ns['EmptyOrder'],o.place)
for i in range(50):o.add_line(str(i),1,gbp)
raises(ns['TooManyLines'],lambda:o.add_line('51',1,gbp));o.place();check(len(o.events)==1)
raises(ns['OrderLocked'],o.place)
check(ns['LegacyCrmAdapter'](types.SimpleNamespace(fetch=lambda _:dict(CUST_NO=1,NM_FULL='McDonald'))).get(1).name=='McDonald')
db=sqlite3.connect(':memory:');db.execute('create table orders(id int,status text,version int)');db.execute("insert into orders values(42,'draft',7)")
sql=fences('sea-ddd','sql')[0];check(db.execute(sql).rowcount==1);check(db.execute(sql).rowcount==0)
# API examples: intentionally bad positional call is supplied an old API fixture.
ns={'send':lambda *args:None,'msg':'fixture'}
s=fences('sea-api-design');run(s[0],ns);raises(TypeError,lambda:ns['send']('x',True));run(s[1],ns);check(ns['clamp'](5,0,3)==3);raises(TypeError,lambda:ns['clamp'](x=5,lo=0,hi=3))
out=io.StringIO()
with contextlib.redirect_stdout(out):run(s[2],ns)
check(out.getvalue()=="['a']\n['a', 'b']\n")
run(s[3],ns);check(ns['tag']('a')==['a'] and ns['tag']('b')==['b'])
run(s[4],ns);check(issubclass(ns['CardDeclined'],ns['PaymentError']))
run(s[5],ns)
with warnings.catch_warnings(record=True) as caught:
 warnings.simplefilter('always');check(ns['fetch']('u',secs=3)==3);check(len(caught)==1)
raises(TypeError,lambda:ns['fetch']('u',timeout=2,secs=3));raises(TypeError,lambda:ns['fetch']('u',bad=1))
# AST boundary check rejects exact packages, permits flaskish and fails empty scans.
ns={};run(fences('sea-adr-evolution')[0],ns)
with tempfile.TemporaryDirectory(prefix='cs-code-architecture-') as t:
 tmp=Path(t);old=Path.cwd();os.chdir(tmp)
 try:
  raises(AssertionError,ns['test_domain_has_no_framework'])
  d=tmp/'shop/domain';d.mkdir(parents=True);p=d/'order.py';p.write_text('import flaskish\n');ns['test_domain_has_no_framework']();check(True)
  p.write_text('from flask import request\n');raises(AssertionError,ns['test_domain_has_no_framework'])
 finally:os.chdir(old)
# Actual Python import cycles, __all__ and import-linter contracts in an isolated package.
with tempfile.TemporaryDirectory(prefix='cs-imports-') as t:
 tmp=Path(t)
 def write(rel,text):
  p=tmp/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
 write('orders.py',fences('sea-modularity')[1]);write('billing.py',fences('sea-modularity')[2])
 result=subprocess.run([sys.executable,'-c','import orders'],cwd=t,capture_output=True,text=True);check(result.returncode!=0 and 'ImportError' in result.stderr)
 # Remove conflicting test module names by using a separate folder.
 package=tmp/'package';package.mkdir()
 (package/'billing').mkdir();(package/'billing/_invoices.py').write_text('class Invoice: pass\ndef create_invoice(): return Invoice()\n');(package/'billing/_tax.py').write_text('vat_rate=.2\n');(package/'billing/__init__.py').write_text(fences('sea-modularity')[0])
 result=subprocess.run([sys.executable,'-c','from billing import *; from billing._tax import vat_rate; assert vat_rate==.2; assert "_tax" not in globals()'],cwd=package,capture_output=True,text=True);check(result.returncode==0)
 for name in ['shop','shop/presentation','shop/application','shop/data','shop/domain']:
  write(name+'/__init__.py','')
 write('shop/presentation/view.py','import shop.application.services\n');write('shop/application/services.py','import shop.data.repo\n');write('shop/data/repo.py','import shop.domain.order\n');write('shop/domain/order.py','')
 write('.importlinter',fences('sea-layered','ini')[0])
 lint='/tmp/synth-content-audit-venv/bin/lint-imports'
 result=subprocess.run([lint,'--no-cache'],cwd=t,capture_output=True,text=True);check(result.returncode==0)
 write('shop/domain/order.py','import shop.presentation.view\n')
 result=subprocess.run([lint,'--no-cache'],cwd=t,capture_output=True,text=True);check(result.returncode==1)
 # Static Protocol compatibility quiz, supplied only its omitted imports/model.
 q=json.loads((B/'sea-hexagonal.questions.json').read_text())[8]
 code=re.search(r'```python\n([\s\S]*?)```',q['prompt'])[1]
 write('protocol_case.py','from typing import Protocol\nclass Order: pass\n'+code)
 result=subprocess.run(['/tmp/synth-content-audit-venv/bin/mypy','--cache-dir',str(tmp/'mypy-cache'),'protocol_case.py'],cwd=t,capture_output=True,text=True);check(result.returncode==0)
conn.close();db.close()
print(f'PASS: {blocks} Python lesson fragments executed with documented fixtures; {checks} behavioral assertions plus SQL and actual import/linter/type-checker checks.')
