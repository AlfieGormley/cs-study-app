exec(open('/tmp/network06-helper.py').read())
md('wm-debugging','assumes one ACK per segment, adequate data/window','assumes periodic loss, one ACK per segment, adequate data/window','Original Mathis Table1 distinguishes periodic1.22 from random-loss1.31 and delayed-ACKcoefficients.')
md('wm-sdn','if no table-miss entry is installed, unmatched packets are dropped;','if no table-miss entry is installed, unmatched packets are dropped by default;','OpenFlow1.3.5section5.4 permits configuration overriding default.')
md('wm-internet-structure','Nominal 10 Gbit/s symmetric line rate; shared and before protocol overhead','10 Gbit/s class (9.95328 Gbit/s nominal each way); shared and before protocol overhead','ITU distinguishes10Gbps class from precise nominal line rate.')
for n,txt in {
 'wm-cellular':'- [ITU-R M.2410: IMT-2020 evaluation requirements](https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-M.2410-2017-PDF-E.pdf)\n- [3GPP TS23.501 Release17: 5G system architecture](https://www.etsi.org/deliver/etsi_ts/123500_123599/123501/17.09.00_60/ts_123501v170900p.pdf)',
 'wm-debugging':'- [Mathis et al.: The Macroscopic Behavior of the TCP Congestion Avoidance Algorithm](https://www.cs.utexas.edu/~lam/395t/papers/Mathis1998.pdf)',
 'wm-sdn':'- [P4 language specification1.2.4](https://p4.org/wp-content/uploads/sites/53/p4-spec/docs/P4-16-v1.2.4.html)',
 'wm-internet-structure':'- [ITU-T G.984.2: GPON physical layer](https://www.itu.int/rec/T-REC-G.984.2)'
}.items():
 p=r/(n+'.md');p.write_text(p.read_text().rstrip()+'\n'+txt+'\n')
d=json.loads(report.read_text())
for u in ['https://www.cs.utexas.edu/~lam/395t/papers/Mathis1998.pdf','https://p4.org/wp-content/uploads/sites/53/p4-spec/docs/P4-16-v1.2.4.html','https://www.itu.int/rec/dologin_pub.asp?id=T-REC-G.984.2-201908-I!!PDF-E&lang=e&type=items','https://www.itu.int/epublications/ar/publication/itu-t-g-9807-1-2023-02-10-gigabit-capable-symmetric-passive-optical-network-xgs-pon']:
 d['sources'].append({'url':u,'scope':'Final primary closure: MathisTable1 coefficient/ACK/loss model; P4 target limits; GPON8.2.1 nominal rates; XGS9.95328Gbps.'})
d['limitations']=[
'All six complete lesson bodies and all72 complete question records independently read. Specific primary-source checks support the core, but this is not every-sentence primary-clause certification: all lessons medium.',
'All five Python fences executed independently using author harness with25,966 assertions and a real offline TLS handshake/hostname rejection. Arithmetic/hash/queue/propagation/table traces are models; no real Wi-Fi, cellular modem, OpenFlow switch, AWS VPC, WAN or PON hardware tested.',
'Wi-FiDCF timings corroborated by IEEE coexistence contribution and upstreamns3 implementation, not a full finalIEEE802.11clause audit. Ofcom2026decision explicitly separated from draft implementation regulations.',
'ITU/3GPP/P4/OpenFlow sources were inspected for relevant claims, not read exhaustively. Alternate primary publication/search extracts used for some initial page failures (Dunant,RIPE). No facts removed solely because one fetch failed.',
'Some optional further-reading links remain outside individual link validation; parent owns whole-project link sweep, shared diagrams,390pxrendering and integrationtests.',
'claimsChecked counts72questionrecords plus grouped corrections, not unique atomic factual claims. errorsCorrected includes clarifications and scope corrections.'
]
d['omissions']=[{'scope':n,'reason':'Visible Evidence limits note retains explicit absent unsupported deployment statistics, universal timing/energy/performance promises or unmeasured hardware behaviour. No low-confidence quantitative claim is supplied as established fact.'} for n in json.loads((r/'module.json').read_text())['lessons']]
d['status']='Independent full semantic verification complete6lessons72questions; mediumconfidence; scopebuild pending after stamp.'
d['resume']='Parent integration: wholebuild/linkcheck/sharedmanualdiagrams/mobile. Security04 next after coordination.'
report.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
lessons=json.loads((r/'module.json').read_text())['lessons']
v={'module':'net-modern','author':{'agent':'root author audit pass on pre-existing curriculum; see docs/audit-networks-modern.json','date':'2026-10-05'},'verifier':{'agent':'audit_synth independent full review; corrections in verifier role','date':'2026-10-05','independent':True,'sources':[s['url']for s in d['sources']]},'summary':{'claimsChecked':72+len(d['findings']),'errorsCorrected':len(d['findings']),'hedgedOrRemoved':sum(1 for f in d['findings']if any(t in f['reason'].lower()for t in ['universal','avoid','unsupported','qualif','remove','conditional']))},'corrections':[f['file'].split('/')[-1]+': '+f['reason']for f in d['findings']],'lowConfidence':[{'lesson':n,'claim':'Deployment-specific performance, evolving products and release-specific implementation details','confidence':'medium','reason':'Core source-checked and examples run; no complete standards-clause or hardware interoperability certification. Unsupported universal specifics explicitly omitted or qualified.'}for n in lessons],'gaps':d['limitations'],'lessons':{n:{'confidence':'medium'}for n in lessons}}
(r/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print('Reviewed',d['coverage'],'correctiongroups',len(d['findings']))
