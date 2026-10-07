import re,json,math,hashlib,io,tarfile,subprocess,sys
from pathlib import Path
mod=Path('content/os/08-virtualisation');checks=[]
def check(name):checks.append(name)
s=(mod/'virt-hypervisors.md').read_text();code=re.search(r'```python\n(.*?)```',s,re.S)[1];env={};exec(code,env);v=env['VCPU']();env['run_guest'](['add','cli','mov','sti','cli'],v);assert not v.interrupts;assert sum(i in env['PRIV'] for i in ['add','cli','mov','sti','cli'])==3;check('exact toy VMM instruction trace')
s=(mod/'virt-isolation-security.md').read_text();code=next(b for b in re.findall(r'```[^\n]*\n(.*?)```',s,re.S) if 'NAMES =' in b);env={};exec(code,env);assert len(env['decode']('a80425fb'))==14;assert set(env['decode']('a82425fb'))-set(env['decode']('a80425fb'))=={'SYS_ADMIN'};check('exact capability decoder and mask delta')
s=(mod/'virt-k8s-os-view.md').read_text();code=next(b for b in re.findall(r'```[^\n]*\n(.*?)```',s,re.S) if 'PERIOD =' in b);env={};exec(code,env);assert [env['cpu_max'](x) for x in [1,500,2000,None]]==['1000 100000','50000 100000','200000 100000','max 100000'];assert [env['shares'](x) for x in [0,250,1000,999999]]==[2,256,1024,262144];check('exact quota/share model including clamps')
assert [(n+1)*(m+1)-1 for n,m in [(4,4),(4,3),(3,3),(5,5)]]==[24,19,15,35];assert 2*1024*1024//4096==512;check('nested walk and huge-page coverage calculations')
size=16.;rate=1.25;dirty=.2;trace=[]
for _ in range(4):
 t=size/rate;trace.append((size,t));size=t*dirty
assert abs(trace[3][1]-.0524288)<1e-10;assert 8*.25**2==.5;assert 1.5/1.25==1.2;check('precopy toy arithmetic and final stop-copy time')
assert 50000*2/1e6==.1;assert 50/4==12.5 and 100-100/8==87.5;assert 512*1024**2==536870912;assert 1000-1000*16/64==750;assert 900+200>1024;check('quota, memory and OOM-score example arithmetic')
def weight(s):
 if s<=2:return 1
 if s>=262144:return 10000
 l=math.log2(s);return math.ceil(10**((l*l+125*l)/612-7/34))
assert weight(1024)==100;assert weight(512)/weight(256)!=2;check('current upstream nonlinear weight conversion does not preserve request ratios')
assert sum([300,600])==900 and 600==900-300;assert 50*200==10000;check('uncompressed image-data and copy-count arithmetic')
# Validate shell continuation produces exactly one overlay -o argument.
s=(mod/'virt-container-primitives.md').read_text();cmd=next(b for b in re.findall(r'```[^\n]*\n(.*?)```',s,re.S) if b.startswith('mount -t overlay'));probe='mount() { printf "%s\\n" "$@"; };\n'+cmd;r=subprocess.run(['/bin/sh','-c',probe],capture_output=True,text=True,check=True);args=r.stdout.splitlines();assert args==['-t','overlay','overlay','-o','lowerdir=/l/app:/l/python:/l/debian,upperdir=/c1/upper,workdir=/c1/work','/c1/merged'],args;check('exact overlay shell fragment argument parsing, without performing privileged mount')
wide=[]
for p in mod.glob('*.md'):
 for b in re.findall(r'```[^\n]*\n(.*?)```',p.read_text(),re.S):
  wide += [(p.name,len(line),line) for line in b.splitlines() if len(line)>44]
for p in mod.glob('*.questions.json'):
 d=json.loads(p.read_text())
 for q in d:
  assert isinstance(q['answer'],int) if q['type']=='single' else isinstance(q['answer'],list)
  for b in re.findall(r'```[^\n]*\n(.*?)```',json.dumps(q,ensure_ascii=False).replace('\\n','\n'),re.S):wide += [(q['id'],len(l),l) for l in b.splitlines() if len(l)>40]
Path('/tmp/cs-study-audit-full/os08/host-results.json').write_text(json.dumps({'checks':checks,'count':len(checks),'nonlinearWeights':{'256shares':weight(256),'512shares':weight(512)},'widthProblems':wide},indent=2));print(json.dumps({'checks':len(checks),'widthProblems':wide}))
