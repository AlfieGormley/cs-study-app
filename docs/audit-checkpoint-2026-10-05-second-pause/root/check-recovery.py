from pathlib import Path
import json
r=json.loads(Path('docs/audit-root.json').read_text())
for f in r['findings'][-12:]:
 if 'corrections' not in f:continue
 path=f['files'][0];p=Path(path)
 s=(Path('/tmp/cs-study-audit-2026-10-04/baseline')/path).read_text()
 for c in f['corrections']:
  assert c['before'] in s,(path,c['before'])
  s=s.replace(c['before'],c['after'])
 if s!=p.read_text():
  twice=s
  for c in f['corrections']:
   if c['before'] in twice:twice=twice.replace(c['before'],c['after'])
  assert twice==p.read_text(),path
  p.write_text(s)
  print('Removed duplicated recovery insertion:',path)
