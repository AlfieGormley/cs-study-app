from pathlib import Path
import subprocess,tempfile,os,re,io,contextlib,sqlite3,math
base=Path('content/software-engineering/04-git-cicd')
root=Path(tempfile.mkdtemp(prefix='cs-git-examples-'))
env=dict(os.environ,GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_AUTHOR_NAME='Audit',GIT_AUTHOR_EMAIL='audit@example.invalid',GIT_COMMITTER_NAME='Audit',GIT_COMMITTER_EMAIL='audit@example.invalid',GIT_EDITOR='true',GIT_SEQUENCE_EDITOR='true')
def git(p,*args,ok=True):
 r=subprocess.run(['git','-c','gc.auto=0','-c','commit.gpgsign=false','-c','core.hooksPath=/dev/null',*args],cwd=p,env=env,text=True,capture_output=True)
 if ok:assert r.returncode==0,(args,r.stdout,r.stderr)
 return r.stdout.strip() if ok else r

def repo(name):
 p=root/name;p.mkdir();git(p,'init','--object-format=sha1','-b','main');return p

def commit(p,name,body,msg):
 (p/name).parent.mkdir(parents=True,exist_ok=True);(p/name).write_text(body);git(p,'add',name);git(p,'commit','-m',msg);return git(p,'rev-parse','HEAD')

def objects(p):return set(git(p,'cat-file','--batch-all-objects','--batch-check=%(objectname)').splitlines())
p=repo('objects');commit(p,'hello.txt','hello\n','initial')
assert git(p,'hash-object','hello.txt')=='ce013625030ba8dba906f756967f9e9ca394464a'
assert git(p,'write-tree')=='aaa96ced2d9a1c8e72c56b253a0e2fe78393feb7'
code=re.findall(r'```python\n(.*?)```',(base/'git-object-model.md').read_text(),re.S)[0]
s=io.StringIO()
with contextlib.redirect_stdout(s):exec(code,{})
assert s.getvalue()=='ce013625030ba8dba906f756967f9e9ca394464a\naaa96ced2d9a1c8e72c56b253a0e2fe78393feb7\n'
before=objects(p);commit(p,'copy.txt','hello\n','copy');assert len(objects(p)-before)==2
commit(p,'src/lib/util.py','old\n','nested');before=objects(p);commit(p,'src/lib/util.py','old\nnew\n','edit');assert len(objects(p)-before)==5
before=objects(p);git(p,'branch','feature');assert objects(p)==before
git(p,'tag','v0.1');assert objects(p)==before
git(p,'tag','-a','v1.0','-m','Release');assert len(objects(p)-before)==1
old=git(p,'rev-parse','HEAD');git(p,'commit','--amend','-m','better');assert git(p,'rev-parse','HEAD')!=old and git(p,'cat-file','-t',old)=='commit'
assert old in git(p,'reflog','--format=%H').splitlines()
# Rebase onto an independent upstream change creates new ancestry; final merge FF adds no objects.
p=repo('rebase');commit(p,'base','base','base');git(p,'switch','-c','feat')
for i in range(3):commit(p,f'feature{i}',str(i),f'feature{i}')
old=git(p,'rev-parse','HEAD');git(p,'switch','main');commit(p,'upstream','one','upstream1');commit(p,'upstream','two','upstream2');git(p,'switch','feat')
before=objects(p);git(p,'rebase','main');new=objects(p)-before
assert sum(git(p,'cat-file','-t',o)=='commit' for o in new)==3
assert git(p,'rev-parse','ORIG_HEAD')==old
before=objects(p);git(p,'switch','main');git(p,'merge','--ff-only','feat');assert objects(p)==before
# Squash deletion can succeed when feat is fully merged to its configured upstream, although not main.
p=repo('squash');commit(p,'base','base','base');git(p,'switch','-c','feat');tip=commit(p,'feature','one','feat');git(p,'branch','upstream-feat');git(p,'branch','--set-upstream-to=upstream-feat','feat');git(p,'switch','main');git(p,'merge','--squash','feat');git(p,'commit','-m','squash')
assert git(p,'merge-base','--is-ancestor',tip,'main',ok=False).returncode==1
assert git(p,'branch','-d','feat',ok=False).returncode==0
# Main-only hotfix survives merging unchanged old contents from a release branch.
p=repo('hotfix');commit(p,'bug','bad\n','base');git(p,'branch','develop');commit(p,'bug','fixed\n','fix');git(p,'switch','develop');commit(p,'feature','release','release');git(p,'switch','main');git(p,'merge','--no-edit','develop');assert (p/'bug').read_text()=='fixed\n'
# Execute both code-review SQLite examples and reproduce the stated failure/injection boundary.
blocks=re.findall(r'```python\n(.*?)```',(base/'git-code-review.md').read_text(),re.S)
db=sqlite3.connect(':memory:');db.execute('CREATE TABLE orders(id INTEGER,total INTEGER,status TEXT,email TEXT)');db.executemany('INSERT INTO orders VALUES(?,?,?,?)',[(1,10,'open','a'),(2,20,'closed','b')])
e={};exec(blocks[0],e);bad=e['find_orders']
try:bad(db,'a')
except sqlite3.OperationalError:pass
else:raise AssertionError('expected malformed singleton tuple SQL')
assert len(bad(db,"x' OR 1=1 -- "))==2
e={};exec(blocks[1],e);good=e['find_orders'];assert good(db,'a')==[(1,10,'open')];assert good(db,"x' OR 1=1 -- ")==[]
statuses=['closed'];assert good(db,'b',statuses)==[(2,20,'closed')] and statuses==['closed'];assert good(db,'a')==good(db,'a')
assert (2400*.5/8+60)/60==3.5
assert (3600*.5/10+60)/60==4
assert math.isclose(1-.995**200,.6330421782738329)
assert round((1-.999**200)*100)==18
print('Git object/hash, new-object counts, rebase/FF, squash-upstream deletion, hotfix-merge, SQLite injection/parameterization and sharding/flakiness fixtures passed.')
print('Isolated fixtures retained at',root)
