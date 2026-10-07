exec(open('/tmp/cs-study-audit-full/helper.py').read())
b=Path('content/security/02-crypto-basics');q=b/'crypto-symmetric.questions.json'
for field in ['prompt','workedExample']:
 item=next(x for x in json.loads(q.read_text()) if x['id']=='crypto-symmetric-q1')
 qe(q,item['id'],field,item[field].replace('country=GB;tier=A','country=GB;tier='),'Execution caught audit regression: original country=GB;tier= is exactly16ASCIIbytes; revert mistakenly added A',['Local Python len() execution'])
save([q])
p=Path('/tmp/cs-study-audit-full/check_sec02.py');p.write_text(p.read_text().replace("len(b'country=GB;tier=A')==16","len(b'country=GB;tier=')==16"))
