from pathlib import Path
import json,re
base=Path('content/networks/05-network-security');rp=Path('docs/audit-networks-security.json');r=json.loads(rp.read_text());rows=json.loads(Path('/tmp/audit-system-design/network05-findings.json').read_text());follow=json.loads(Path('/tmp/audit-system-design/network05-source-followup.json').read_text())
initial={
'https://www.rfc-editor.org/rfc/rfc9000.html':'Anti-amplification 3xUDPpayload and Retry address validation.',
'https://www.rfc-editor.org/rfc/rfc4987.html':'SYNcookies mitigation and encoded state appendix.',
'https://www.kernel.org/doc/html/latest/networking/ip-sysctl.html':'tcp_syncookies modes1overflowfallback2unconditional.',
'https://www.rfc-editor.org/rfc/rfc4303.html':'ESPformat, sequence/replay state update afterauthentication; out-of-order replaywindow.',
'https://www.rfc-editor.org/rfc/rfc2827.html':'BCP38prefixfilterstillpermitswithinprefixspoof.',
'https://www.rfc-editor.org/rfc/rfc9293.html':'OrdinarySYNRECEIVEDack range ISS<ACK<=ISS+1.',
'https://www.christian-rossow.de/publications/amplification-ndss2014.pdf':'OriginalUDPpayloadBAFdefinitionandtableIIIexperimentmeans.',
'https://github.blog/news-insights/company-news/ddos-incident-report/':'GitHuboriginalmemcachedincident1.35Tbpsandmax51000amplification.',
'https://docs.memcached.org/releasenotes/releasenotes156/':'UDPdisabledbydefaultrelease1.5.6.',
'https://www.usenix.org/system/files/conference/usenixsecurity17/sec17-antonakakis.pdf':'OriginalMiraianalysisDynDNSimpactsection.',
'https://blog.cloudflare.com/ddos-threat-report-2025-q3/':'Datedproviderreported29.7Tbps,notglobalabsoluteceiling.',
'https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf':'Zero trust abstractandper-sessiontenets.',
'https://wiki.nftables.org/wiki-nftables/index.php/Simple_ruleset_for_a_workstation':'OriginalrulesetIPv6NDandconntrackexamples.',
'https://wiki.nftables.org/wiki-nftables/index.php/Synproxy':'SYNproxynotrackinitialSYNandstatefulfloodprotection.',
'https://wiki.nftables.org/wiki-nftables/index.php/Configuring_chains':'Acceptcanproceedtolaterbasechain;chainpriorityanddefaultpolicy.',
'https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html':'Allowunion,SGreferencesprivateIP,middleboxexception,AmazonDNSexception.',
'https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html':'StatelessorderedsubnetACLs.',
'https://docs.aws.amazon.com/vpc/latest/userguide/custom-network-acl.html':'Ephemeralportrangesvary,1024..65535broadcoverageexample.',
'https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateway-troubleshooting.html':'350sidleexpiry sendsRSTtowardsresource.',
'https://docs.kernel.org/networking/nf_conntrack-sysctl.html':'DefaultestablishedTCPconntrack432000s.',
'https://www.rfc-editor.org/rfc/rfc8446.html':'TLS1.3psk_kevsDHEFS,contextboundCertVerify,ticketidentity,earlydata,cipherandhandshakefields.',
'https://www.rfc-editor.org/rfc/rfc8470.html':'HTTPearlydatasafemethodlimits andoriginownhandshakewaitinginsufficient.',
'https://www.rfc-editor.org/rfc/rfc9849.html':'ECHinnernameprivacy,outernameandDNSlimits,sharedconfiganonymity.',
'https://www.rfc-editor.org/rfc/rfc5280.html':'Trustanchoroutsidepath,validationconstraints.',
'https://www.rfc-editor.org/rfc/rfc9001.html':'QUICusesTLShandshakebutseparatepacketprotection,partialheaderencryption.',
'https://www.wireguard.com/protocol/':'Protocolprimitivesandtimerconditions.',
'https://www.wireguard.com/quickstart/':'Keepaliveconfigurationoverview.',
'https://man7.org/linux/man-pages/man8/wg-quick.8.html':'WrapperOSrouteandMTUderivation,Tableoff/auto.',
'https://www.rfc-editor.org/rfc/rfc7296.html':'IKE8octetSPIsvsChildSAs andNAT4500switch.',
'https://www.rfc-editor.org/rfc/rfc7348.html':'VXLANSecurityVNIisolation/filtering,noconfidentiality,4789.',
'https://www.rfc-editor.org/rfc/rfc4106.html':'AESGCM16tagmandatorysupport8/12optional.',
'https://www.krackattacks.com/':'Originalresearchclientkeyreinstall,2.4+zerokey,APpatchcases.',
'https://wpa3.mathyvanhoef.com/':'OriginalDragonbloodresearchtiming/cache/downgradeimplementationlimits.'}
sources=[{'url':u,'checked':v} for u,v in initial.items()]+follow
# Keep each fetched source once and explicitly retain section-level scope.
sources=list({x['url']:x for x in sources}.values())
gaps=[]
for p in sorted(base.glob('*.md')):
 for m in re.finditer(r'^> \[!note\] Content gap\n(?:>.*\n?)+',p.read_text(),re.M):gaps.append({'file':str(p),'text':m.group(0).strip()})
limitations=[
'Full independent semantic read covers all six lessons and all 67 question prompts, options, explanations, answers, worked examples and references. This is not a claim that every factual sentence has a separate source proof; retrieved sources were checked in relevant sections, not read cover to cover.',
'All seven Python lesson fences executed: six deterministic local examples plus one real TLS handshake. No Python-labelled quiz fences. Plain protocol pseudocode is not executable production code.',
'No live firewall/Suricata/Zeek/IDS deployment, AWS account tests, WireGuard/IPsec tunnel setup, radio hardware tests or active wireless attack. The Suricata example is checked against rule/URI documentation but was not run in the engine. nftables configuration is explicitly a partial example, not a deployable complete firewall.',
'Five synthetic offline libpcap/tcpdump assertions test IPv4/IPv6 filtering and flag/payload distinctions. They do not validate live capture privileges, rotation behaviour, offload settings or every platform.',
'No measurement of global adoption, attack prevalence, detection quality or GPU performance. Explicit gap notes mark omitted measurements, rankings, chronology/attribution and unverified changing vendor incident list.',
'Target historical case is attributed to the Senate report with its provisional evidence caveat. Vendor reports/papers are evidence for their reported results, not independently reproduced incidents.',
'The global link procedure succeeded on 45 of 46 original URLs outside sandbox; the only failing Zeek master URL was replaced by a retrieved official versioned log index. Reachability does not itself prove factual support.',
'External TLS test succeeded with TLSv1.3/TLS_AES_256_GCM_SHA384 and subject rfc-editor.org; these are observations from this run, not promised fixed output. No comprehensive PKI validation-suite or CA issuance integration test.'
]
r.update(status='Independent review complete; corrections applied, execution/source closure recorded. Ready for verification stamp and scoped build.',findings=rows,sources=sources,omissions=gaps,limitations=limitations,next='Stamp verification record and run scoped build; then independently review networks/03-transport.',confidence='medium',execution={'python_harness':'/tmp/audit-system-design/network05-check.py','assertions':392157,'lesson_python_fences':7,'quiz_python_fences':0,'replay_exhaustive_sequences':38880,'live_tls_script':'/tmp/audit-system-design/network05-live-tls.py','live_tls_result':'TLSv1.3; TLS_AES_256_GCM_SHA384; subject commonName rfc-editor.org','offline_packet_harness':'/tmp/audit-system-design/network05-pcap.py','offline_packet_assertions':5,'result':'PASS'},count_method=f'{len(rows)} logged correction groups, including factual errors, scope clarifications and removed unsupported assertions; not a count of every sentence or unique atomic fact.')
rp.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
v={'module':json.loads((base/'module.json').read_text())['id'],'author':{'agent':'pre-existing authors','date':'2026-10-05'},'verifier':{'agent':'/root/audit_system_design','date':'2026-10-05','independent':True,'sources':[x['url'] for x in sources]},'summary':{'claimsChecked':len(rows),'errorsCorrected':len(rows),'hedgedOrRemoved':len(gaps)},'countMethod':r['count_method']+' hedgedOrRemoved counts visible gap notes, not all scoped edits.','corrections':[x['reason'] for x in rows],'gaps':[x['text'] for x in gaps],'lowConfidence':[],'notes':limitations,'lessons':{p.stem:{'confidence':'medium'} for p in sorted(base.glob('*.md'))},'validation':{'report':str(rp),'execution':r['execution']}}
(base/'verification.json').write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
print(len(rows),'correction groups;',len(sources),'section-checked primary sources;',len(gaps),'visible gap notes')
