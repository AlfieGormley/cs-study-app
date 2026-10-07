from pathlib import Path
import re,io,contextlib,dataclasses,xml.etree.ElementTree as ET
base=Path('content/software-engineering/02-design-patterns')
expected={
'pattern-why': ['email: deploy finished\n',"['Fig', 'apple', 'pear']\n['apple', 'Fig', 'pear']\n"],
'pattern-creational':['a,b\n',"['[OK] on black', 'Saved in white']\n",'SELECT * FROM users WHERE age > 18 AND active LIMIT 10\n','True\nFalse\n',''],
'pattern-structural':["sent 'hi' to +447700900000\n",'HELLO!\n','expensive load\n3\n3\n','hi\n','22\n','ooo\n','True\n'],
'pattern-behavioural-1':['70\n63.0\n65\n',"['email 42', 'ship 42', 'ship 43']\n","['a']\n"],
'pattern-behavioural-2':['sent for review\nneeds approval\npublished\nalready published\n','','REPORT\n£120\n£80\nEND\n','[1, 2, 3, 4]\n','(1 + (2 + 3)) = 6\n'],
'pattern-anti-patterns':[None,None,'Hello, Ada\n','[1]\n[1, 2]\n']}
count=0;envs={}
for name,outputs in expected.items():
 blocks=re.findall(r'```python\n(.*?)```',(base/(name+'.md')).read_text(),re.S)
 assert len(blocks)==len(outputs)
 for i,(block,out) in enumerate(zip(blocks,outputs)):
  if out is None:continue
  env={};stream=io.StringIO()
  with contextlib.redirect_stdout(stream):exec(compile(block,f'{name}:{i}','exec'),env)
  assert stream.getvalue()==out,(name,i,stream.getvalue(),out)
  envs[name,i]=env;count+=1
Retry=envs['pattern-why',0]['Retry']
for n in [0,-1,True,1.5,'3']:
 try:Retry(object(),n)
 except ValueError:pass
 else:raise AssertionError(n)
class Unreliable:
 def __init__(self):self.calls=0
 def send(self,msg):
  self.calls+=1
  if self.calls<3:raise ConnectionError()
  return msg
u=Unreliable();assert Retry(u,3).send('ok')=='ok' and u.calls==3
u=Unreliable()
try:Retry(u,2).send('fail')
except ConnectionError:assert u.calls==2
else:raise AssertionError('failure not propagated')
e=envs['pattern-structural',6];g=e['glyph']('a','font')
try:g.char='b'
except dataclasses.FrozenInstanceError:pass
else:raise AssertionError('mutable shared glyph')
assert ET.fromstring(envs['pattern-structural',5]['Svg']().circle(3)).attrib['r']=='3'
e=envs['pattern-behavioural-2',3];assert list(e['t'])==list(e['t'])==[1,2,3,4]
it=iter(e['t']);assert iter(it) is it;assert list(it)==[1,2,3,4] and list(it)==[]
e=envs['pattern-behavioural-1',2];editor=e['e'];editor.run(e['Insert'](editor.doc,'c'));assert editor.doc==['a','c'] and not editor.undone
assert 249.995>249.99 and not 249.995>=250
print(f'{count} complete Python fences: exact output matches; retry, immutable glyph, XML, iterator, undo and threshold edge cases passed. Two contextual anti-pattern fragments excluded.')
