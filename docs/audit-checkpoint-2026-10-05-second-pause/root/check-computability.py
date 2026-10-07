from pathlib import Path
import re,json,itertools,math,contextlib,io,subprocess,sys
B=Path('content/theory/05-computability');ns={};assertions=0;fences=0;outputs={}
def check(x):
 global assertions
 assert x
 assertions+=1
for p in sorted(B.glob('*.md')):
 env={};out=io.StringIO()
 with contextlib.redirect_stdout(out):
  for lang,code in re.findall(r'```([^\n]*)\n(.*?)```',p.read_text(),re.S):
   if lang=='python':exec(compile(code,str(p),'exec'),env);fences+=1
 ns[p.stem]=env;outputs[p.stem]=out.getvalue()
def words(alpha,maxn):
 for n in range(maxn+1):
  yield from map(''.join,itertools.product(alpha,repeat=n))
c=ns['compu-cfg']
for n in range(9):
 expected=[]
 for w in words('()',n):
  b=0;good=True
  for x in w:
   b+=1 if x=='(' else -1
   if b<0:good=False
  if good and b==0:expected.append(w)
 check(c['generate'](c['P'],'S',n)==sorted(expected,key=lambda x:(len(x),x)))
for n in range(1,15):check(c['trees'](n)==math.comb(2*n-2,n-1)//n)
for w in words('ab',10):check(c['cyk'](w)==(len(w)>0 and len(w)%2==0 and w=='a'*(len(w)//2)+'b'*(len(w)//2)))
p=ns['compu-pda-pumping']
for w in words('ab',10):check(p['run'](p['PAL'],'p',{'f'},w)==(len(w)%2==0 and w==w[::-1]))
t=ns['compu-turing-machines']
for n in range(1024):
 state,steps,tape=t['run'](t['INC'],bin(n)[2:],'R',{'H'})
 check(state=='H');check(int(''.join(tape[i] for i in sorted(tape)).strip('_'),2)==n+1)
for w in words('abc',8):check((t['run'](t['ABC'],w,'q0',{'acc'})[0]=='acc')==(len(w)%3==0 and w=='a'*(len(w)//3)+'b'*(len(w)//3)+'c'*(len(w)//3)))
for n in range(1,50):
 _,steps,_=t['run'](t['ABC'],'a'*n+'b'*n+'c'*n,'q0',{'acc'},max_steps=20000)
 check(steps==4*n*n+3*n+1)
check(t['run'](t['INC'],'111','R',{'H'})[1]==8)
check(t['run'](t['BB2'],'','A',{'H'},blank='0')[1]==6)
check(t['run']({},'','R',{'H'})[0]=='reject')
check(t['run']({},'','R',{'H'},max_steps=0)[0]=='timeout')
for kwargs in ({'max_steps':-1},):
 try:t['run']({},'','R',{'H'},**kwargs);check(False)
 except ValueError:check(True)
c=ns['compu-church-turing'];nums=[c['zero']]
for i in range(12):nums.append(c['succ'](nums[-1]))
for i,a in enumerate(nums):
 for j,b in enumerate(nums):
  check(c['to_int'](c['add'](a)(b))==i+j);check(c['to_int'](c['mul'](a)(b))==i*j)
check(c['bf']('++++++++[>++++++++<-]>++.')=='B')
for v in range(256):check(c['bf']('+'*v+'.')==chr(v))
check(c['bf']('-.')==chr(255));check(c['bf']('[[]]')=='')
for code,err in [('[',ValueError),(']',ValueError),(',',ValueError),('<',IndexError),('>'*30000,IndexError)]:
 try:c['bf'](code);check(False)
 except err:check(True)
h=ns['compu-halting']
for n in range(1000):check(h['decide'](h['is_square'],h['not_square'],n)==(math.isqrt(n)**2==n))
for n in range(-3,1000):check(h['is_prime'](n)==(n>1 and not any(n%d==0 for d in range(2,n))))
for n in range(4,1000,2):check(h['two_primes'](n))
try:h['halts'](lambda:None,None);check(False)
except NotImplementedError:check(True)
r=ns['compu-reductions-rice'];calls=[]
def accept(x):calls.append(x);return True
def reject(x):calls.append(x);return False
f,w=r['f'](accept,'w');check(calls==[]);check(f(w)==True);check(calls==['w']);calls.clear()
for M in [accept,reject]:
 for T in [lambda x:True,lambda x:False,lambda x:x=='a']:
  mapped=r['rice_map'](M,'w',T)
  for x in ['','a','b']:check(mapped(x)==(M('w') and T(x)))
# Verify genuine divergence by a bounded child process; compile actual lesson definitions.
r_code='\n'.join(code for lang,code in re.findall(r'```([^\n]*)\n(.*?)```',(B/'compu-reductions-rice.md').read_text(),re.S) if lang=='python')
for expr in ['f(lambda x: False, "w")[0]("w")','rice_map(lambda x: spin(), "w", lambda x: True)("x")']:
 try:subprocess.run([sys.executable,'-c',r_code+'\ndef spin():\n while True: pass\n'+expr],timeout=.5,check=True);check(False)
 except subprocess.TimeoutExpired:check(True)
# Every marked Python quiz fence executes with its lesson environment. Other fences are diagrams/pseudocode.
quiz_fences=0
for p in B.glob('*.questions.json'):
 env=ns[p.name.split('.questions')[0]]
 for q in json.loads(p.read_text()):
  for text in [q['prompt'],q.get('workedExample','')]+[o['text']+'\n'+o['explanation'] for o in q['options']]:
   for code in re.findall(r'```python\n(.*?)```',text,re.S):
    with contextlib.redirect_stdout(io.StringIO()):exec(code,env)
    quiz_fences+=1
check(c['to_int'](c['add'](c['mul'](c['two'])(c['two']))(c['three']))==7)
report={'assertions':assertions,'lessonPythonFences':fences,'markedQuizPythonFences':quiz_fences,'outputs':outputs,'limitations':['Goldbach counterexample search deliberately not run without bound; finite checks do not prove the conjecture.','Nonterminating recogniser/reduction cases tested only through bounded subprocess observations, not an empirical proof of divergence.','No code can execute a genuine halting oracle; the proof placeholder is tested to raise NotImplementedError.','Other quiz code/diagram fences reviewed manually; Church and Brainfuck quiz results checked explicitly.']}
Path('/tmp/cs-study-audit-2026-10-04/computability-execution.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
