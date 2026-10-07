from pathlib import Path
import json,re,math,itertools,contextlib,io,sqlite3
b=Path('content/theory/02-discrete-structures')
checks=0;blocks=0

def ck(p):
 global checks
 assert p
 checks+=1
ns={}
for p in b.glob('*.md'):
 scope={}
 for code in re.findall(r'```python\n(.*?)```',p.read_text(),re.S):
  with contextlib.redirect_stdout(io.StringIO()): exec(compile(code,str(p),'exec'),scope)
  blocks+=1
 ns[p.stem]=scope
# Execute every Python fence in quiz prompt and worked examples, isolated per quiz.
quizblocks=0
for p in b.glob('*.questions.json'):
 for q in json.loads(p.read_text()):
  a=q['answer'];aa=a if isinstance(a,list) else [a]
  ck(all(isinstance(x,int) and 0<=x<len(q['options']) for x in aa))
  scope={}
  for field in ['prompt','workedExample']:
   for code in re.findall(r'```python\n(.*?)```',q.get(field,''),re.S):
    with contextlib.redirect_stdout(io.StringIO()): exec(compile(code,q['id'],'exec'),scope)
    quizblocks+=1
s=ns['disc-sets-functions'];ck(s['a']|s['b']=={1,2,3,4,5});ck(s['a']^s['b']=={1,2,5})
for m in range(5):
 for n in range(5):
  fs=list(itertools.product(range(n),repeat=m))
  ck(len(fs)==n**m)
  ck(sum(len(set(f))==m for f in fs)==(math.factorial(n)//math.factorial(n-m) if m<=n else 0))
for n in range(9):
 subs=[tuple(i for i in range(n) if mask>>i&1) for mask in range(1<<n)]
 ck(len(set(subs))==2**n);ck(sum(map(len,subs))==(n*2**(n-1) if n else 0))
# SQL De Morgan equivalence includes UNKNOWN in truth-table values.
with sqlite3.connect(':memory:') as c:
 for a,bb in itertools.product([None,0,1],repeat=2):
  ck(c.execute('select NOT (? OR ?), (NOT ?) AND (NOT ?)',(a,bb,a,bb)).fetchone()[0]==c.execute('select (NOT ?) AND (NOT ?)',(a,bb)).fetchone()[0])
r=ns['disc-relations'];ck(r['find']('a')==r['find']('c'))
# Exhaustively count all equivalence/reflexive relations on <=4 elements.
for n in range(5):
 pairs=list(itertools.product(range(n),repeat=2));eq=ref=0
 for mask in range(1<<len(pairs)):
  R={p for i,p in enumerate(pairs) if mask>>i&1}
  if not all((a,a) in R for a in range(n)):continue
  ref+=1
  if all((bb,a) in R for a,bb in R) and all((a,c) in R for a,bb in R for b2,c in R if bb==b2):eq+=1
 ck(ref==2**(n*n-n));ck(eq==[1,1,2,5,15][n])
R={(1,2),(2,3),(3,1),(4,3)}
while True:
 new=R|{(a,d) for a,c in R for cc,d in R if c==cc}
 if new==R:break
 R=new
ck(len(R)==12)
ck(math.isclose(1-math.perm(12,5)/12**5,.6180555555555556))
ck(math.perm(10,4)==5040);ck(math.comb(8,3)==56)
ck(len(set(itertools.permutations('BANANA')))==60)
ck(sum(sum(x)==10 for x in itertools.product(range(1,8),repeat=4))==84)
ck(36**6-26**6==1867866560)
ck(576*245+3520*244==1000000)
ck(sum(p.index(1) not in (0,4) for p in itertools.permutations(range(1,6)))==72)
ck(sum(any(k%d==0 for d in [2,3,5]) for k in range(1,1001))==734)
ck(sum(k%2!=0 and k%3!=0 for k in range(1,101))==33)
for n in range(1,9):
 der=sum(all(i!=v for i,v in enumerate(p)) for p in itertools.permutations(range(n)))
 ck(der==round(math.factorial(n)/math.e))
ck(sum(len(set(f))==3 for f in itertools.product(range(3),repeat=5))==150)
ways=ns['disc-inclusion-recurrences']['ways']
for n in range(41):
 ck(ways(n,[1,2,5])==sum(a+2*bb+5*c==n for a in range(n+1) for bb in range(n//2+1) for c in range(n//5+1)))
ck(ways(10,[1,2,5])==10);ck(ways(6,[1,2,5])==5)
ck(sum('11' not in ''.join(x) for x in itertools.product('01',repeat=6))==21)
a=[2,5];z=[1,4]
for n in range(2,30):
 a.append(5*a[-1]-6*a[-2]);z.append(4*z[-1]-4*z[-2]);ck(a[-1]==2**n+3**n);ck(z[-1]==(n+1)*2**n)
calls=[1,1]
for i in range(2,21):calls.append(calls[-1]+calls[-2]+1)
ck(calls[20]==21891)
# All 1,099 labelled simple graphs up to 5 vertices: bipartite routine against exhaustive assignments.
g=ns['disc-graphs'];graphcases=0
for n in range(1,6):
 edges=list(itertools.combinations(range(n),2))
 for mask in range(1<<len(edges)):
  adj={v:[] for v in range(n)}
  E=[e for i,e in enumerate(edges) if mask>>i&1]
  for u,v in E:adj[u].append(v);adj[v].append(u)
  ck(sum(map(len,adj.values()))==2*len(E))
  brute=any(all(colors[u]!=colors[v] for u,v in E) for colors in itertools.product(range(2),repeat=n))
  ck(g['is_bipartite'](adj)==brute);graphcases+=1
nt=ns['disc-number-theory']
for a,bb in itertools.product(range(-30,31),repeat=2): ck(nt['gcd'](a,bb)==math.gcd(a,bb))
for a,bb in itertools.product(range(50),repeat=2):
 d,x,y=nt['egcd'](a,bb);ck(d==math.gcd(a,bb) and a*x+bb*y==d)
for n in range(-2,201):
 expected=[k for k in range(2,n+1) if all(k%d for d in range(2,math.isqrt(k)+1))]
 ck(nt['primes_upto'](n)==expected)
for a,e,n in itertools.product(range(-8,9),range(20),range(1,20)):ck(nt['modpow'](a,e,n)==pow(a,e,n))
for e,n in [(-1,7),(0,0),(5,-1)]:
 try:nt['modpow'](2,e,n)
 except ValueError:ck(True)
 else:raise AssertionError('must reject invalid input')
ck(nt['egcd'](240,46)==(2,-9,47));ck(pow(7,-1,40)==23);ck(pow(3,200,13)==9)
ck(pow(65,17,3233)==2790);ck(pow(2790,2753,3233)==65)
for m in range(55):ck(pow(pow(m,3,55),27,55)==m)
for m in range(3233):ck(pow(pow(m,17,3233),2753,3233)==m)
ck(sum(math.gcd(k,561)==1 for k in range(1,562))==320)
ck(all(pow(a,560,561)==1 for a in range(1,561) if math.gcd(a,561)==1))
print(json.dumps({'assertions':checks,'lesson_python_fences':blocks,'quiz_python_fences':quizblocks,'exhaustive_graph_cases':graphcases,'result':'PASS'}))
