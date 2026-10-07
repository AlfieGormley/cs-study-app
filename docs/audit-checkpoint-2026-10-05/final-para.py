exec(open('/tmp/lang-helpers.py').read())
p='https://webkit.org/blog/6240/ecmascript-6-proper-tail-calls-in-webkit/'
for n in ['para-functional-basics','para-multi-paradigm']:
 path=root/(n+'.md');text=path.read_text()
 old="only Safari's engine implements them"
 if old in text:lesson(n,old,"JavaScriptCore (used by Safari) implements them",'Avoid unsupported exhaustive engine survey.',p)
# Actual recursion behavior verified on local CPython; no general cross-engine promise.
lesson('para-functional-basics','## Trade-offs and pitfalls','> [!note] Evidence gap\n> No universal cache-lookup latency or cross-engine tail-call support matrix is supplied: this review did not establish measurements or an exhaustive current engine survey. Check the target runtime and benchmark the actual workload.\n\n## Trade-offs and pitfalls','Explicit absence of unverified universal timing and engine coverage.',p)
report['omissions'].append({'file':str(root/'para-functional-basics.md'),'claim':'Universal cache lookup latency and exhaustive current JavaScript tail-call engine support','reason':'No measured workload or exhaustive engine survey; visible evidence-gap note supplied.'})
for f in report['findings']:
 if any('openjdk.org/jeps/' in u for u in f['source_urls']):f['source_urls'].append('https://docs.oracle.com/en/java/javase/21/language/java-language-changes-release.html')
report['reviewed_files'].append(str(root/'module.json'))
module=json.loads((root/'module.json').read_text());ids=module['lessons'];findings=[f for f in report['findings'] if str(root) in f['file']];sources=sorted(set(u for f in findings for u in f['source_urls'] if 'openjdk.org/jeps/' not in u))
sources+=['https://docs.python.org/3/library/graphlib.html','https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/AbstractCollection.html','https://homepages.inf.ed.ac.uk/wadler/papers/expression/expression.txt']
count=sum(len(json.loads((root/(i+'.questions.json')).read_text())) for i in ids)
report.setdefault('modules',{})[module['id']]={'directory':str(root),'lessons':len(ids),'questions':count,'full_read':True,'correction_groups':len(findings),'validation':'/tmp/test-para-results.json: 41 executed Python/JS/Bash/SQL groups, two expected exceptions; three framework excerpts inspected, not run. Java/Haskell/Prolog runtimes unavailable locally; their examples source-checked and manually traced, not falsely reported executed.','confidence':'medium'}
report['limitations']=['Exact completed coverage is in modules and reviewed_files; unlisted modules remain pending.','Core claims checked against fetched primary documentation and executable examples; not every historical attribution separately fetched, so medium confidence.','Whole-project links, browser rendering and shared diagram integration belong to the parent agent.']
save()
record={'module':module['id'],'author':{'agent':'pre-existing project author; original provenance not independently established','date':'2026-10-05'},'verifier':{'agent':'audit_synth independent paradigms review','date':'2026-10-05','independent':True,'sources':sources},'summary':{'claimsChecked':len(findings),'errorsCorrected':len(findings),'hedgedOrRemoved':1},'corrections':[f.get('question_id',pathlib.Path(f['file']).name)+': '+f['reason'] for f in findings],'lowConfidence':[{'lesson':i,'claim':'Runtime-specific performance and historical generalisations','confidence':'medium','reason':'Core semantics verified; implementation/performance guidance qualified, no exhaustive runtime survey. Noninstalled language examples source-checked and manually traced.'} for i in ids],'gaps':report['limitations']+[report['modules'][module['id']]['validation']],'lessons':{i:{'confidence':'medium'} for i in ids}}
(root/'verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(count,len(findings))
