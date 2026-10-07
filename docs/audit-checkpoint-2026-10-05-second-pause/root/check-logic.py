from pathlib import Path
import json,re,itertools,io,contextlib,math,random,sqlite3,bisect,textwrap
from types import SimpleNamespace
from fractions import Fraction
base=Path('content/theory/01-logic-proofs');checks=0;lessonf=0;quizf=0;sqlf=0;envs={}
def check(v):
 global checks
 assert v
 checks+=1
def run(code,env):
 with contextlib.redirect_stdout(io.StringIO()) as out:exec(code,env)
 return out.getvalue()
for p in base.glob('*.md'):
 env={'users':[SimpleNamespace(admin=True,verified=True),SimpleNamespace(admin=False,verified=False)]};envs[p.stem]=env
 for c in re.findall(r'```python\n(.*?)```',p.read_text(),re.S):
  out=run(c,env);lessonf+=1
  if p.stem=='logp-propositional':check(out=='(True, None)\n(False, (False, True))\n')
  if 'xs = [3, 1, 2]' in c:check(out=='False\nTrue\n')
# arithmetic/induction and executable invariant examples
E=envs['logp-invariants'];rec=envs['logp-induction']['total']
for n in range(8):
 for t in itertools.product([-1,0,1],repeat=n):
  a=list(t);check(E['total'](a)==sum(a));check(rec(a)==sum(a));check(E['insertion_sort'](a.copy())==sorted(a))
  for x in [-2,-1,0,1,2]:check(E['bsearch'](sorted(a),x)==bisect.bisect_left(sorted(a),x))
for a,b in itertools.product(range(60),repeat=2):check(E['gcd'](a,b)==math.gcd(a,b))
for a in range(-8,9):
 for n in range(45):check(E['power'](a,n)==a**n)
for bad in [-1,2.5,'a']:
 try:E['power'](2,bad)
 except ValueError:check(True)
 else:check(False)
for n in range(1,101):
 check(sum(range(1,n+1))==n*(n+1)//2)
 check(sum(Fraction(1,k*k) for k in range(1,n+1))<=2-Fraction(1,n))
 if n>=5:check(2**n>n*n)
 if n>=12:check(any(4*a+5*b==n for a in range(n//4+1) for b in range(n//5+1)))
for n in range(40):check(all((n*n+n+41)%d for d in range(2,math.isqrt(n*n+n+41)+1)))
check(40**2+40+41==41**2);check(59*509==30031)
# SAT DPLL vs exhaustive truth assignments, including empty and tautological clauses.
D=envs['logp-sat']['dpll'];rng=random.Random(763)
def sat(cnf,n):
 return any(all(any(bits[abs(l)-1]==(l>0) for l in clause) for clause in cnf) for bits in itertools.product([False,True],repeat=n))
clauses=[frozenset(l for l,on in zip([-2,-1,1,2],bits) if on) for bits in itertools.product([False,True],repeat=4)]
for n in range(1,7):
 for case in range(250):
  cnf=[frozenset(rng.choice([-1,1])*rng.randint(1,n) for _ in range(rng.randrange(5))) for _ in range(rng.randrange(12))]
  model=D(cnf);check((model is not None)==sat(cnf,n))
  if model is not None:
   check(not any(-l in model for l in model));check(all(any(l in model for l in c) for c in cnf))
for cnf in itertools.product(clauses,repeat=3):check((D(list(cnf)) is not None)==sat(cnf,2))
# Truth-table equivalences and gate encodings.
imp=lambda p,q:not p or q
for p,q,r in itertools.product([False,True],repeat=3):
 check(imp(p,q)==imp(not q,not p));check(not(p and q)==(not p or not q));check((p or(p and q))==p)
 check(imp((p or q)and imp(p,r)and imp(q,r),r))
 check(((not r or p)and(not r or q)and(r or not p or not q))==(r==(p and q)))
 check(((not r or p or q)and(r or not p)and(r or not q))==(r==(p or q)))
# Tseitin projection example (a AND b) OR c, including output assertion.
for a,b,c in itertools.product([False,True],repeat=3):
 has=any((g==(a and b))and(h==(g or c))and h for g,h in itertools.product([False,True],repeat=2));check(has==((a and b)or c))
# K3/K4 coloring CNFs and documented count.
for n in [3,4]:
 cnf=[]
 for v in range(n):
  ids=[3*v+c+1 for c in range(3)];cnf.append(frozenset(ids));cnf.extend(frozenset([-a,-b]) for a,b in itertools.combinations(ids,2))
 for u,v in itertools.combinations(range(n),2):cnf.extend(frozenset([-3*u-c-1,-3*v-c-1]) for c in range(3))
 check((D(cnf)is not None)==(n==3))
 if n==4:check(len(cnf)==34)
# Every quiz Python fence, supplying only missing context described in prompts.
for p in base.glob('*.questions.json'):
 for q in json.loads(p.read_text()):
  for code in re.findall(r'```python\n(.*?)```',q['prompt'],re.S):
   e={'a':[4,1,8],'b':True,'x':SimpleNamespace(size=3),'n':10,'process':lambda x:None}
   if q['id']=='logp-propositional-q4':e['a']=False
   if q['id']=='logp-invariants-q2':code='def max_example(a):\n'+textwrap.indent(code,'    ')
   if q['id']=='logp-invariants-q6':e['x']=2
   if q['id']=='logp-invariants-q9':e['x']=3
   out=run(code,e);quizf+=1
   if q['id']=='logp-propositional-q7':check(out=='True False\n')
   if q['id']=='logp-predicate-q5':check(out=='True False\n')
   if q['id']=='logp-invariants-q2':check(e['max_example']([4,1,8])==8)
   if q['id']=='logp-invariants-q6':check(e['result']==1024)
   if q['id']=='logp-invariants-q7':check(e['s']==13)
   if q['id']=='logp-invariants-q9':check(e['x']==1)
   if q['id']=='logp-invariants-q10':check(e['r']==3)
   if q['id']=='logp-induction-q4':
    check(e['half'](4)==2)
    try:e['half'](1)
    except RecursionError:check(True)
    else:check(False)
# Relational division SQL examples with all subsets of four possible order pairs.
queries=[]
for p in base.glob('*.md'):queries+=re.findall(r'```sql\n(.*?)```',p.read_text(),re.S)
for p in base.glob('*.questions.json'):
 for q in json.loads(p.read_text()):queries+=re.findall(r'```sql\n(.*?)```',q['prompt'],re.S)
for query in queries:
 sqlf+=1
 for mask in range(16):
  db=sqlite3.connect(':memory:');db.executescript('CREATE TABLE customers(id INTEGER);CREATE TABLE products(id INTEGER);CREATE TABLE orders(customer_id INTEGER,product_id INTEGER);INSERT INTO customers VALUES(1),(2);INSERT INTO products VALUES(1),(2);')
  pairs=list(itertools.product([1,2],repeat=2));rows=[p for i,p in enumerate(pairs) if mask>>i&1];db.executemany('INSERT INTO orders VALUES(?,?)',rows)
  check(sorted(x[0] for x in db.execute(query))==[c for c in [1,2] if all((c,p) in rows for p in [1,2])]);db.execute('DELETE FROM products');check(sorted(x[0] for x in db.execute(query))==[1,2]);db.close()
# Counterexample establishing replacement Hoare distractor is false.
I=False;B=True;check(not(I and B));B=False;check(not(I and not B))
result={'assertions':checks,'lesson_python_fences':lessonf,'quiz_python_fences':quizf,'sql_fences':sqlf,'random_cnf_cases':1500,'all_three_clause_two_variable_cases':4096,'limitations':'Finite tests support examples, not universal proof. SQL executed in SQLite, not PostgreSQL; no runtime performance benchmarks.'}
print(json.dumps(result));Path('/tmp/cs-study-audit-2026-10-04/logic-execution.json').write_text(json.dumps(result,indent=2)+'\n')
