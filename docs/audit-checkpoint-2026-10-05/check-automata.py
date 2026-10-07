from pathlib import Path
import re,json,itertools,random,io,contextlib,math
base=Path('content/theory/04-automata');checks=0;fences=0;quiz=0
ns={}
def check(x):
 global checks
 assert x
 checks+=1
def execute(c,env):
 with contextlib.redirect_stdout(io.StringIO()) as out:exec(c,env)
 return out.getvalue()
for name in ['auto-dfa','auto-nfa','auto-thompson','auto-minimisation','auto-regex-engines']:
 for c in re.findall(r'```python\n(.*?)```',(base/(name+'.md')).read_text(),re.S):
  out=execute(c,ns);fences+=1
  if name=='auto-dfa':check(out=='True\nFalse\n')
  if name=='auto-thompson':check(out=='14\n')
def words(alpha,n):
 for k in range(n+1):
  yield from map(''.join,itertools.product(alpha,repeat=k))
for w in words('01',12):
 check(ns['run_dfa'](ns['D3'],0,{0},w)==(int(w or '0',2)%3==0))
check(ns['run_dfa']({(0,'a'):None},0,{None},'a'))
for w in words('ab',10):check(ns['run_nfa'](ns['delta'],ns['start'],{ns['acc']},w)==bool(re.fullmatch('(a|b)*abb',w)))
# Use smaller domain for naive exponential teaching matcher.
for w in words('ab',6):check(ns['bt'](ns['start'],w,0)==bool(re.fullmatch('(a|b)*abb',w)))
# epsilon cycle correctly terminates in set simulation.
check(ns['close']({(0,''):{1},(1,''):{0}},{0})=={0,1})
for p in base.glob('*.questions.json'):
 for q in json.loads(p.read_text()):
  for c in re.findall(r'```python\n(.*?)```',q['prompt'],re.S):
   env=dict(ns)
   if q['id']=='auto-nfa-q7':
    env['delta']={('s',''):{'p0','r0'},('p0','a'):{'p1'},('p1','a'):{'p0'},('r0','a'):{'r1'},('r1','a'):{'r2'},('r2','a'):{'r0'}};env['acc']={'p0','r0'}
   out=execute(c,env);quiz+=1
   if q['id']=='auto-nfa-q7':check(out=='[0, 2, 3, 4, 6]\n')
   if q['id']=='auto-dfa-q8':check(out=='[True, True, False, True]\n');check(not env['run']('١'))
   if q['id']=='auto-regex-engines-q9':check(out=='True\nFalse\n')
   if q['id']=='auto-regex-engines-q1':check([bool(env[k]) for k in 'ABCD']==[True,False,False,False])
# Compare minimisation to independent product reachability equivalence on seeded machines.
rng=random.Random(129)
for n in range(1,11):
 for case in range(50):
  states=list(range(n));alpha='ab';d={(q,c):rng.randrange(n) for q in states for c in alpha};acc={q for q in states if rng.randrange(2)}
  part=ns['minimise'](iter(states),iter(alpha),d,acc)
  for p,q in itertools.product(states,repeat=2):
   todo=[(p,q)];seen=set();eq=True
   while todo:
    a,b=todo.pop()
    if (a,b) in seen:continue
    seen.add((a,b))
    if (a in acc)!=(b in acc):eq=False;break
    todo.extend((d[a,c],d[b,c]) for c in alpha)
   check((part[p]==part[q])==eq)
# Regex full-match equivalence, regular backreference example, unary composites.
for w in words('a b\t',7):check(bool(re.fullmatch(r'(\w+\s?)*',w))==bool(re.fullmatch(r'(\w+\s)*\w*',w)))
for n in range(100):
 check(bool(re.fullmatch(r'(a+)\1','a'*n))==bool(re.fullmatch('(aa)+','a'*n)))
 composite=n>1 and any(n%d==0 for d in range(2,math.isqrt(n)+1))
 check(bool(re.fullmatch(r'(..+)\1+','a'*n))==composite)
# Pumping examples: all permitted first-run splits for p<=25.
for p in range(1,26):
 for x in range(p):
  for k in range(1,p-x+1):
   check(p+k!=p);check(p*p<p*p+k<(p+1)**2)
   check(p+1-k<=p)
   w='a'*(p-k)+'b'+'a'*p+'b';check(len(w)%2==1 or w[:len(w)//2]!=w[len(w)//2:])
a,b=1,1
for i in range(2,31):a,b=b,a+b
check(b==1346269)
result={'assertions':checks,'lesson_python_fences':fences,'quiz_python_fences':quiz,'seeded_dfa_machines':500,'notes':'Finite exhaustive and seeded checks; no timing or general proof inferred.'}
print(json.dumps(result))
Path('/tmp/cs-study-audit-2026-10-04/automata-execution.json').write_text(json.dumps(result,indent=2)+'\n')
