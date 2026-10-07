import re,json,subprocess,tempfile,math,sys
from pathlib import Path
from collections import deque
base=Path('content/os/02-threads-scheduling');out=Path('/tmp/cs-study-audit-full/os02');out.mkdir(exist_ok=True);checks=[]
def ck(name,value):
 assert value,name
 checks.append(name)
def run(src,lang,expected=None):
 p=out/('code'+str(len(checks))+('.c' if lang=='c' else '.py'));p.write_text(src)
 if lang=='c':
  exe=str(p.with_suffix(''));subprocess.run(['cc','-std=c11','-O2','-pthread',str(p),'-o',exe],check=True,capture_output=True);cmd=[exe]
 else:cmd=[sys.executable,str(p)]
 result=subprocess.run(cmd,check=True,capture_output=True,text=True,timeout=30).stdout
 ck(p.name, expected is None or expected in result);return result
blocks=re.findall(r'```c\n(.*?)```',(base/'sched-thread-apis.md').read_text(),re.S)
run(next(x for x in blocks if 'int main(void)' in x),'c','499999500000')
pyblocks=re.findall(r'```python\n(.*?)```',(base/'sched-thread-apis.md').read_text(),re.S)
run(pyblocks[0],'python','[0, 1, 4, 9, 16]')
# Race-demo timings/outputs are deliberately not assertions of correctness.
for code in pyblocks[1:]: run(code,'python')
for p in base.glob('*.questions.json'):
 for q in json.loads(p.read_text()):
  a=q['answer'] if isinstance(q['answer'],list) else [q['answer']]
  assert len(set(a))==len(a) and all(0<=x<len(q['options']) for x in a)
ck('66 answer indices valid',sum(len(json.loads(p.read_text())) for p in base.glob('*.questions.json'))==66)
# Independent unit-time scheduler model for integer toy examples.
def sim(arr,bur,kind,quantum=None):
 rem=bur[:];done=[None]*len(bur);first=[None]*len(bur);t=0;queue=deque();pending=list(range(len(bur)));current=None;used=0
 while any(rem):
  for i in pending[:]:
   if arr[i]<=t:queue.append(i);pending.remove(i)
  if kind=='srtf':
   if current is not None: queue.append(current)
   current=min(queue,key=lambda i:(rem[i],arr[i],i)) if queue else None
   if current is not None:queue.remove(current)
  elif current is None or (kind=='rr' and used==quantum):
   if current is not None:queue.append(current)
   current=(min(queue,key=lambda i:(bur[i],arr[i],i)) if kind=='sjf' else queue[0]) if queue else None
   if current is not None:queue.remove(current)
   used=0
  if current is not None:
   if first[current] is None:first[current]=t
   rem[current]-=1;used+=1
   if rem[current]==0:done[current]=t+1;current=None;used=0
  t+=1
 return done,[done[i]-arr[i]-bur[i] for i in range(len(bur))],[first[i]-arr[i] for i in range(len(bur))]
for kind,arr,bur,q,d,w in [('fcfs',[0]*3,[24,3,3],None,[24,27,30],[0,24,27]),('sjf',[0]*3,[24,3,3],None,[30,3,6],[6,0,3]),('rr',[0]*3,[24,3,3],4,[30,7,10],[6,4,7]),('sjf',[0,1,2,3],[8,4,9,5],None,[8,12,26,17],[0,7,15,9]),('srtf',[0,1,2,3],[8,4,9,5],None,[17,5,26,10],[9,0,15,2]),('sjf',[0,1,2,3],[6,2,8,3],None,[6,8,19,11],[0,5,9,5]),('srtf',[0,1,2,3],[6,2,8,3],None,[11,3,19,6],[5,0,9,0]),('rr',[0]*3,[5,3,1],2,[9,8,5],[4,5,4]),('rr',[0]*3,[10,10,10],1,[28,29,30],[18,19,20])]:
 actual=sim(arr,bur,kind,q);ck(str((kind,bur,q)),actual[:2]==(d,w))
for name,actual,expected in [('stackGiB',10000*8/1024,78.125),('kernelMiB',10000*36/1024,351.5625),('overhead',.5/(4.5+.5),.1),('vruntime',6*1024/335,18.34029850746269),('nice0share',1024/1844,.5553145336225597),('nice19share',15/1039,.014436958614052),('quota8',100-200/8,75),('quota10',100-300/10,70),('requestLatency',100-26+5,79),('fractionalquota',100+80-50,130),('throttlefraction',14400/36000,.4),('aging',127-20,107),('poolrule',8*(1+90/10),80)]:ck(name,math.isclose(actual,expected))
ck('EEVDF eligibility deadline',min((v+r,k) for k,v,r in [('A',8,3),('B',12,.5),('C',10,.5)] if v<=10)[1]=='C')
ck('admissionreject',.3+.4+.3>.95)
q=json.loads((base/'sched-thread-apis.questions.json').read_text());code=re.search(r'```python\n(.*?)```',next(x for x in q if x['id'].endswith('q9'))['prompt'],re.S).group(1)
p=out/'deadlock.py';p.write_text(code)
try:subprocess.run([sys.executable,str(p)],timeout=2,capture_output=True);raise AssertionError('expected deadlock')
except subprocess.TimeoutExpired:ck('barrier pool deadlock observed then process terminated',True)
(out/'results.json').write_text(json.dumps({'assertionsPassed':len(checks),'checks':checks,'limits':'Toy schedules do not benchmark Linux; intentionally racy output is not proof. Deadlock subprocess forcibly terminated after timeout.'},indent=2));print(len(checks),'checks passed')
