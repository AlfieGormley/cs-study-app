from pathlib import Path
code=Path('/tmp/cs-study-audit-2026-10-04/fix-root11.py').read_text()
code=code.replace(",\n('A 5,000-line', 'A 5,000-line')",'')
helper='''
def patch(path,changes,reason,sources):
 p=Path(path);s=p.read_text()
 for a,b in changes:
  if a in s:s=s.replace(a,b)
  elif b not in s:raise ValueError((path,a[:100]))
 p.write_text(s)
 findings.append(dict(files=[path],reason=reason,corrections=[{'before':a,'after':b} for a,b in changes],sources=sources,confidence='high'))
def questions(path,edit,reason,sources):
 p=Path(path)
 if 'pattern-anti-patterns' in path:
  before=json.loads(p.read_text());q=json.loads(p.read_text());edit(q)
  p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\\n')
 else:
  before=json.loads((Path('/tmp/cs-study-audit-2026-10-04/baseline')/path).read_text())
  q=json.loads(json.dumps(before));edit(q)
  assert q==json.loads(p.read_text()),path
 findings.append(dict(files=[path],reason=reason,changed_question_ids=[b['id'] for a,b in zip(before,q) if a!=b],sources=sources,confidence='high'))
'''
code=code.replace("b='content/software-engineering/02-design-patterns/'",helper+"\nb='content/software-engineering/02-design-patterns/'")
exec(compile(code,'recovered-root11','exec'))
print('Recovered all 12 lesson/quiz correction groups and full-read coverage.')
