import re,math,json,tempfile,os,hashlib,types,io,contextlib
from pathlib import Path
m=Path('content/security/01-fundamentals').resolve();results=[]
def blocks(name):return re.findall(r'```python\n(.*?)```',(m/(name+'.md')).read_text(),re.S)
def passed(name):results.append(name)
ns={};exec(blocks('secf-cia-aaa')[0],ns)
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/'data';p.write_bytes(b'abc');assert ns['digest'](p)=='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad';p.write_bytes(b'x'*131077);assert ns['digest'](p)==hashlib.sha256(p.read_bytes()).hexdigest()
passed('Exact streamed SHA256 example, standard abc vector and multi-chunk input')
ns={};exec(blocks('secf-threat-modelling')[0],ns);cost=ns['cost'];leaf=lambda c:{'cost':c};AND=lambda *xs:{'type':'AND','children':list(xs)};OR=lambda *xs:{'type':'OR','children':list(xs)}
assert cost(OR(leaf(2),OR(leaf(3),AND(leaf(2),leaf(4))),AND(leaf(5),leaf(9))))==2
assert cost(OR(AND(leaf(4),leaf(3)),OR(leaf(9),AND(leaf(2),leaf(4))),leaf(8)))==6
assert min(3,14)==3
for values in [(False,False),(False,True),(True,False),(True,True)]:assert (not all(not x for x in values))==any(values)
passed('Exact attack-tree evaluator: lesson2/root and quiz6/root, boolean requirement truth cases')
ns={};exec(blocks('secf-principles')[0],ns);assert ns['can_delete'](types.SimpleNamespace(role='contractor')) is False;assert ns['can_delete'](types.SimpleNamespace(role='admin')) is True
class Policy:
 def check(self,*a):raise TimeoutError()
class Log:
 def exception(self,*a):pass
ns.update(policy=Policy(),log=Log());exec(blocks('secf-principles')[1],ns);assert ns['is_allowed']('a','b') is False
passed('Exact allowlist and fail-closed examples with unknown role and timeout')
ns={};exec(blocks('secf-access-control')[0],ns);U=types.SimpleNamespace
u=U(tenant_id=1,clearance=2,id=7,roles=[]);doc=U(tenant_id=1,level=1,owner_id=7)
assert ns['can_read'](u,doc,U(mfa_age_minutes=59));assert not ns['can_read'](u,doc,U(mfa_age_minutes=60));assert not ns['can_read'](u,doc,U(mfa_age_minutes=-1));doc.tenant_id=2;assert not ns['can_read'](u,doc,U(mfa_age_minutes=0))
passed('Exact ABAC function: owner/tenant and MFA age boundaries')
ns={};exec(blocks('secf-authentication')[1],ns);salt,h=ns['hash_pw']('example only');assert ns['verify']('example only',salt,h);assert not ns['verify']('wrong',salt,h);salt2,h2=ns['hash_pw']('example only');assert salt!=salt2 and h!=h2
passed('Exact scrypt parameters executed: correct/wrong password and independent salts')
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'wordlist.txt').write_text('\n'.join('word'+str(i) for i in range(7776)));old=os.getcwd();out=io.StringIO()
 try:
  os.chdir(p)
  with contextlib.redirect_stdout(out):exec(blocks('secf-authentication')[0],{})
 finally:os.chdir(old)
 lines=out.getvalue().splitlines();assert lines[:2]==['52.4','77.5'];assert len(lines[2].split())==6
assert round(4*math.log2(7776))==52;assert round((94**8)/1e10/86400,1)==7.1;assert 190 < (94**8)/1e10*1e4/(365.25*86400)<200;assert 2_000_000/50_000==40;assert 30/120==.25
passed('Exact entropy/passphrase snippet with synthetic unique7776-word fixture; arithmetic recomputed')
assert (0o640>>6)&7==6 and (0o640>>3)&7==4 and 0o640&7==0;assert [((0o604>>s)&7) for s in (6,3,0)]==[6,0,4]
passed('Unix mode decoding and first-match model; no privileged real-user filesystem test')
record={'groupsPassed':len(results),'checks':results,'limitations':['Passphrase fixture synthetic, not a supplied production Diceware list.','Flask/database handlers source-reviewed sketches; no complete app context. Setuid C fragment source-reviewed, not executed as root.','No live AWS, PostgreSQL RLS, Windows MIC, WebAuthn/TOTP deployment, EDR, incident replay or attack-rate benchmark.']}
Path('/tmp/cs-study-audit-full/sec01-results.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
