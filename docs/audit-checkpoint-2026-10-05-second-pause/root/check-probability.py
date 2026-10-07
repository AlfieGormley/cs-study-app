import re,json,io,contextlib,random,math,itertools
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
B=Path('content/theory/03-probability'); checks=0; runs=[]; envs={}
def ck(x):
 global checks
 assert x
 checks+=1
for p in sorted(B.glob('*.md')):
 env={};random.seed(4281)
 for i,c in enumerate(re.findall(r'```python\n(.*?)```',p.read_text(),re.S)):
  out=io.StringIO()
  with contextlib.redirect_stdout(out):exec(compile(c,str(p), 'exec'),env)
  runs.append({'file':str(p),'fence':i,'output':out.getvalue().strip()})
 envs[p.stem]=env
for p in sorted(B.glob('*.questions.json')):
 for q in json.loads(p.read_text()):
  for field in ['prompt','workedExample']:
   for i,c in enumerate(re.findall(r'```python\n(.*?)```',q.get(field,''),re.S)):
    env={};out=io.StringIO()
    with contextlib.redirect_stdout(out):exec(compile(c,q['id'],'exec'),env)
    runs.append({'question':q['id'],'field':field,'fence':i,'output':out.getvalue().strip()})
    if 'scan' in env: ck(sum(env['scan'](a) for a in itertools.permutations(range(4)))==50)
# Finite exact enumeration of dice, unions, independence, hats/inversions/records.
D=list(itertools.product(range(1,7),repeat=2)); ck(sum(sum(x)==7 for x in D)==6);ck(sum(sum(x)==8 for x in D)==5)
ck(F(sum(x[0]==3 and sum(x)==8 for x in D),sum(sum(x)==8 for x in D))==F(1,5))
ck(sum(sum(x)==10 for x in itertools.product(range(1,7),repeat=3))==27)
ck(F(sum(6 in x for x in itertools.product(range(1,7),repeat=4)),6**4)==1-F(5,6)**4)
ck(sum(i%2==0 or i%3==0 for i in range(1,101))==67)
for n in range(1,8):
 perms=list(itertools.permutations(range(n)))
 hats=inv=records=0
 for a in perms:
  hats+=sum(i==v for i,v in enumerate(a));inv+=sum(a[i]>a[j] for i in range(n) for j in range(i+1,n));records+=envs['prob-expectation']['scan'](a)
  ck(envs['prob-expectation']['scan'](a)==sum(a[i]==max(a[:i+1]) for i in range(n)))
 ck(F(hats,len(perms))==1);ck(F(inv,len(perms))==F(n*(n-1),4));ck(F(records,len(perms))==sum(F(1,i) for i in range(1,n+1)))
# Enumerate all small occupancy spaces; check pair and empty-bin expectations and birthday function.
f=envs['prob-algorithms']['p_collision']
for m in range(1,6):
 for n in range(0,7):
  collision=pairs=empty=0
  for a in itertools.product(range(m),repeat=n):
   c=Counter(a);collision+=len(c)<n;pairs+=sum(x*(x-1)//2 for x in c.values());empty+=m-len(c)
  ck(math.isclose(f(n,m),collision/m**n,abs_tol=1e-12));ck(F(pairs,m**n)==F(n*(n-1),2*m));ck(F(empty,m**n)==m*F(m-1,m)**n)
ck(round(f(23,365),3)==.507)
# Bayes exact fractions, repeated conditional independence, classifier iterator reuse.
def bayes(pr,t,f):return pr*t/(pr*t+(1-pr)*f)
ck(bayes(F(1,100),F(99,100),F(5,100))==F(1,6));ck(bayes(F(1,100),F(99,100)**2,F(5,100)**2)==F(99,124))
ck(round(float(bayes(F(1,1000),F(98,100),F(1,100)))*100,1)==8.9)
cl=envs['prob-bayes']['classify'];pr={'spam':.4,'ham':.6};li={'spam':{'free':.3,'winner':.2},'ham':{'free':.02,'winner':.01}}
ck(cl(['free','winner'],pr,li)=='spam');ck(cl(iter(['free','winner']),pr,li)=='spam');ck(cl([],pr,li)=='ham')
ck(F(1,2)*F(100,10)+F(1,2)*F(100,90)==F(50,9))
# Actual comparisons match qs return, under seeded examples.
class Key:
 count=0
 def __init__(self,x):self.x=x
 def __lt__(self,o):Key.count+=1;return self.x<o.x
qs=envs['prob-algorithms']['qs']
for n in range(0,101):
 for seed in range(10):
  random.seed(seed);Key.count=0;v=qs([Key(i) for i in range(n)]);ck(v==Key.count)
# Expected comparison recurrence vs indicator formula, exact rational arithmetic.
E=[F(0),F(0)]
for n in range(2,101):
 E.append(n-1+F(2,n)*sum(E[:n]));ck(E[n]==2*(n+1)*sum(F(1,k) for k in range(1,n+1))-4*n)
# Poisson tails, quorum, exact 100-dice convolution, normal percentiles.
pmf=envs['prob-distributions']['poisson_pmf'];tail=lambda cap:1-sum(pmf(k,5) for k in range(cap+1))
ck(round(tail(9),4)==.0318);ck(.00201<tail(12)<.00203);ck(.000697<tail(13)<.000699)
ck(abs(sum(math.comb(5,k)*.01**k*.99**(5-k) for k in range(3,6))-9.8506e-6)<1e-12)
c=Counter({0:1})
for _ in range(100):
 d=Counter()
 for x,n in c.items():
  for k in range(1,7):d[x+k]+=n
 c=d
ck(round(100*sum(n for x,n in c.items() if 316<=x<=384)/6**100,1)==95.7)
from statistics import NormalDist
ck(abs(NormalDist().cdf(3)-.998650101968)<1e-10)
pc=envs['prob-statistics']['percentile'];ck(pc([10]*1000+[1000]*10,99)==10);ck(pc([1,2,3],0)==1);ck(pc([1,2,3],100)==3)
for args in [([],50),([1],-1),([1],101)]:
 try:pc(*args)
 except ValueError:ck(True)
 else:ck(False)
ab=envs['prob-statistics']['ab_test'];z,p=ab(1000,10000,1100,10000);ck(round(z,2)==2.31);ck(round(p,3)==.021)
z,p=ab(500,10000,560,10000);ck(round(z,2)==1.89);ck(round(p,3)==.058)
for args in [(0,0,1,10),(11,10,1,10),(0,10,0,10),(10,10,10,10)]:
 try:ab(*args)
 except ValueError:ck(True)
 else:ck(False)
ck(round(1-.99**100,3)==.634);ck(round(1-.95**20,3)==.642)
ck(4**9<10**6<=4**10);ck(round((1-math.exp(-.7))**7*100,2)==.82)
result={'assertions':checks,'fences':runs,'limitations':'Finite numerical checks do not prove general probability theorems. Simulations seeded for reproducibility; not real system measurements.'}
Path('/tmp/cs-study-audit-2026-10-04/probability-execution.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
