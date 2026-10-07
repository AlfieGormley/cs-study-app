from pathlib import Path
import re,io,contextlib,itertools,random,json,math,subprocess
root=Path('content/architecture/04-pipelining');env={};outputs={};checks=0
def check(v):
 global checks
 assert v
 checks+=1
for p in root.glob('*.md'):
 ns={};out=io.StringIO()
 with contextlib.redirect_stdout(out):
  for lang,code in re.findall(r'^```([^\n]*)\n(.*?)^```',p.read_text(),re.M|re.S):
   if lang=='python':exec(compile(code,str(p),'exec'),ns)
 env[p.stem]=ns;outputs[p.stem]=out.getvalue()
check(outputs['pipe-iron-law']=='2.2\n')
check(outputs['pipe-branch-prediction']=='200 101\n3\n')
check(outputs['pipe-out-of-order']=='p32 = mul(p2, p3)\np33 = add(p32, p5)\np34 = add(p6, p7)\np35 = add(p34, p2)\n')
check(outputs['pipe-power-wall']=='2 1.82\n4 3.08\n8 4.71\n64 8.77\n1000000000 10.0\n')
f=env['pipe-branch-prediction'];transition={0:{False:0,True:1},1:{False:0,True:2},2:{False:1,True:3},3:{False:2,True:3}}
for n in range(11):
 for seq in itertools.product((False,True),repeat=n):
  for start in range(4):
   state=start;miss=0
   for taken in seq:
    miss+=((state in (2,3)) != taken);state=transition[state][taken]
   check(f['two_bit'](seq,start)==miss)
  for start in (False,True):
   expected=sum(a!=b for a,b in zip((start,)+seq,seq));check(f['one_bit'](seq,start)==expected)
  for bits in (1,2,4):
   # Oracle indexes explicit recent history tuples, fixed PC=0.
   hist=(False,)*bits;table={};miss=0
   for taken in seq:
    state=table.get(hist,1);miss+=(state>=2)!=taken;table[hist]=transition[state][taken];hist=hist[1:]+(taken,)
   check(f['gshare'](seq,pc=0,hbits=bits)==miss)
check(f['gshare'](f['loop'])==108)
check(f['two_bit']([1,0,0,1,1],2)==3)
for period in (4,10,100):
 seq=([True]*(period-1)+[False])*100
 check(f['two_bit'](seq)==101);check(f['one_bit'](seq)==200)
for bad in (-1,4,1.5,True):
 try:f['two_bit']([],bad)
 except ValueError:check(True)
 else:check(False)
for bad in (0,-1,17,2.5,True):
 try:f['gshare']([],hbits=bad)
 except ValueError:check(True)
 else:check(False)
for n in range(101):
 out=io.StringIO()
 with contextlib.redirect_stdout(out):env['pipe-five-stage']['diagram'](n)
 check(out.getvalue().splitlines()[-1]==f'cycles: {n+4 if n else 0}')
 lines=out.getvalue().splitlines()[:-1]
 for i,line in enumerate(lines):check(line[4:].split()==['IF','ID','EX','MEM','WB'])
stalls=env['pipe-hazards']['stalls']
naive=[('lw',1,[]),('lw',2,[]),('add',3,[1,2]),('sw',None,[3]),('lw',4,[]),('lw',5,[]),('add',6,[4,5]),('sw',None,[6])]
scheduled=[naive[i] for i in [0,1,4,2,5,3,6,7]]
check((stalls(naive),stalls(naive,False))==(2,8));check((stalls(scheduled),stalls(scheduled,False))==(0,4))
# Independent timing oracle: enumerate issue times using producer EX/MEM/WB events.
rng=random.Random(9371)
for k in range(5000):
 prog=[(rng.choice(['lw','add','sw']),rng.randrange(4),[rng.randrange(4),rng.randrange(4)]) for _ in range(rng.randrange(1,30))]
 prog=[(op,None if op=='sw' else dst,srcs) for op,dst,srcs in prog]
 for fw in (True,False):
  issued=[];cycle=0
  for op,dst,srcs in prog:
   while True:
    okay=True
    for src in srcs:
     if src==0:continue
     for pop,pdst,psrcs,start in reversed(issued):
      if pdst==src:
       # Consumer EX starts issue+2; producer data ready at end EX or MEM.
       ready=start+(4 if pop=='lw' else 3) if fw else start+4
       consumed=cycle+2 if fw else cycle+1
       if consumed<ready:okay=False
       break
    if okay:break
    cycle+=1
   issued.append((op,dst,srcs,cycle));cycle+=1
  check(stalls(prog,fw)==cycle-len(prog))
# Execute renamed generic arithmetic in dependency-valid random order; compare architectural results.
rename=env['pipe-out-of-order']['rename']
for _ in range(1000):
 regs={f'x{i}':rng.randrange(-10,11) for i in range(8)};initial=regs.copy();prog=[]
 for j in range(24):
  op=rng.choice(['add','sub']);dst=f'x{rng.randrange(8)}';srcs=[f'x{rng.randrange(8)}' for _ in range(2)];prog.append((op,dst,srcs));a,b=[regs[x] for x in srcs];regs[dst]=a+b if op=='add' else a-b
 out=io.StringIO()
 with contextlib.redirect_stdout(out):rename(prog,8,40)
 pending=[];latest={f'x{i}':f'p{i}' for i in range(8)};physical={f'p{i}':initial[f'x{i}'] for i in range(8)}
 for ins,line in zip(prog,out.getvalue().splitlines()):
  dst,op,a,b=re.fullmatch(r'(p\d+) = (\w+)\((p\d+), (p\d+)\)',line).groups();pending.append((dst,op,a,b));latest[ins[1]]=dst
 while pending:
  ready=[x for x in pending if x[2] in physical and x[3] in physical];check(bool(ready));dst,op,a,b=rng.choice(ready);physical[dst]=physical[a]+physical[b] if op=='add' else physical[a]-physical[b];pending.remove((dst,op,a,b))
 for r,v in regs.items():check(physical[latest[r]]==v)
for p in (0,.1,.5,.8,.9,.95,1):
 for n in range(1,100):
  a=env['pipe-power-wall']['amdahl'](p,n);check(1-1e-12<=a<=n+1e-10);check(math.isclose(a,n/(n*(1-p)+p)))
# Both shown C loop bodies with documented types; verify byte range and modulo arithmetic.
src='''#include <stdint.h>
#include <stddef.h>
#include <assert.h>
uint64_t branch(const uint8_t *data,size_t n,uint64_t sum) { for(size_t i=0;i<n;i++) if(data[i]>=128) sum+=data[i]; return sum; }
uint64_t select_sum(const uint8_t *data,size_t n,uint64_t sum) { for(size_t i=0;i<n;i++) sum+=(data[i]>=128)?data[i]:0; return sum; }
int main(void) {uint8_t data[256]; for(int i=0;i<256;i++)data[i]=(uint8_t)i; for(size_t n=0;n<=256;n++){uint64_t expect=0;for(size_t i=128;i<n;i++)expect+=i;assert(branch(data,n,0)==expect);assert(select_sum(data,n,0)==expect);assert(branch(data,n,UINT64_MAX)==select_sum(data,n,UINT64_MAX));}return 0;}
'''
outdir=Path('/tmp/cs-study-audit-2026-10-04/pipeline-tests');outdir.mkdir(exist_ok=True);(outdir/'loops.c').write_text(src)
for target in ('arm64','x86_64'):
 subprocess.run(['clang','-arch',target,'-O2','-Wall','-Wextra','-Werror',str(outdir/'loops.c'),'-o',str(outdir/target)],check=True);subprocess.run([str(outdir/target)],check=True)
checks+=257*3*2
r={'assertions':checks,'lesson_python_fences':7,'c_targets':['arm64 native','x86_64 local compatibility'],'outputs':outputs,'limitations':['Symbolic pipeline/assembly traces are models, not measured hardware; performance, physical power and Linux perf counters not measured.','Tomasulo snapshot verified by dependence tracing, not an IBM simulator.']};(outdir/'results.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
