import math,json
from pathlib import Path
checks=0
def check(value):
 global checks
 assert value
 checks+=1
# Models taught in architecture lessons, not measured service performance.
check(round(8760*(1-0.999**6),1)==52.4)
check((20000-5000)*120==1800000)
check(1800000/5000==360)
check((30000-6000)*300/6000==1200)
check(1000/2*500==250000)
check(sum(h%4==h%5 for h in range(20))==4)
check(15000/20==750)
check((5300-5000)*86400==25920000)
check(5e9/1e8==50 and 50-32==18)
check(math.ceil(2e12/256e6)==7813)
check(2*(90/120)==1.5)
check(round(math.log10(20),2)==1.30)
check(math.log10(1000)/math.log10(10)==3)
classic=lambda tf,length=1:tf*2.2/(tf+1.2*(.25+.75*length))
for tf,want in [(1,1),(2,1.38),(10,1.96)]:check(round(classic(tf),2)==want)
check(round(classic(1,.5),2)==1.26)
check(round(classic(1,2),2)==.71)
check(20*(9990+10)==200000)
check(1-.5**2==.75)
check(90/(5-1)==22.5)
check(math.isclose(2e12/200/365/5,2e12/365000))
check(4*280-4*20==1040)
check(4*75==300)
check(math.comb(100,4)==3921225)
# Distinguish divergent values during a partition and convergent merge.
a={'eu':41,'us':61};b={'eu':40,'us':62}
merge=lambda x,y:{k:max(x[k],y[k]) for k in x}
check(sum(merge(a,b).values())==103)
check(merge(a,b)==merge(b,a))
check(merge(a,a)==a)
# Every current quiz is parsed; answer indexes remain valid.
for p in Path('content/system-design/08-architecture').glob('*.questions.json'):
 for q in json.loads(p.read_text()):
  answers=q['answer'] if isinstance(q['answer'],list) else [q['answer']]
  check(all(0<=a<len(q['options']) for a in answers))
print(f'Passed {checks} model and answer-index checks. No vendor integration benchmark inferred.')
