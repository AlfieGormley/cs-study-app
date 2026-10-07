exec(open('/tmp/network04-helper.py').read());n='app-dns-wire'
md(n,'a 16-bit ID, unauthenticated UDP and caches that trust whatever arrives first.','a small transaction ID space, traditionally unauthenticated transport and the checks required before caching a response. Resolvers must not simply trust whichever datagram arrives first.','First-arrival alone never sufficient matching and validation.')
a=(r/(n+'.md')).read_text();old=a[a.index('```python'):a.index('29 bytes:')]
new='''This builds an ordinary ASCII-label question, not a full resolver. It accepts an optional final dot, checks wire-length bounds, and uses a random transaction ID unless a test ID is supplied. Internationalised presentation names require a suitable IDNA conversion before this restricted encoder.

```python
import secrets, struct

def build_query(name, qtype=1, qid=None):
    if qid is None:
        qid = secrets.randbelow(65536)
    if (type(qid) is not int
            or not 0 <= qid <= 65535
            or type(qtype) is not int
            or not 0 <= qtype <= 65535):
        raise ValueError("bad field")
    if name == ".":
        labels = []
    else:
        if name.endswith("."):
            name = name[:-1]
        labels = [p.encode("ascii")
                  for p in name.split(".")]
        if any(not 1 <= len(p) <= 63
               for p in labels):
            raise ValueError("bad label")
    qname = b"".join(
        bytes([len(p)]) + p
        for p in labels) + b"\\0"
    if len(qname) > 255:
        raise ValueError("name too long")
    header = struct.pack("!HHHHHH",
        qid, 0x0100, 1, 0, 0, 0)
    return header + qname + struct.pack(
        "!HH", qtype, 1)

q = build_query("example.com", qid=0xABCD)
print(len(q))  # 29
print(q[:4].hex(" "))  # ab cd 01 00
```

'''
md(n,old,new,'Original used Unicode character lengths with UTF8 bytes, allowedoversize/emptylabels andfixedID,blockedforever externalUDP withunvalidatedresponse andguaranteedflags. Restrictencodeandtestdeterministically.')
md(n,"The reply's flags `0x8180` decode",'A hypothetical reply with flags `0x8180` would decode','No deterministicexternalresolverflags claim.')
md(n,'The answer to the query above begins:','An illustrative uncompressed A answer could begin with this compressed owner name:','LiveanswerTTL270notguaranteed; clarifyfixture.')
md(n,'an illustrative uncompressed A','an illustrative A','Clarify onlyRDATAisaddress,ownercompressed.') if False else None
md(n,'a crafted message whose pointer points at itself has crashed many DNS libraries.','a self-referential pointer can otherwise cause an infinite loop or resource exhaustion. Parsers also need bounds and expanded-name-length checks.','Removeunverifiedprevalence; specifyactualparserinvariants.')
md(n,'If an answer does not fit, the server sets **TC** and the client retries over **TCP**','If required response data does not fit, the server sets **TC** and a resolver can retry over **TCP**','Optionaladditionalrecords mayomitwithoutTC; clientsdo notalwaysretryonegivenserver.')
md(n,'Large UDP answers get IP-fragmented, and fragments are often dropped by firewalls or can be spoofed.','UDP datagrams exceeding path capacity can be fragmented, dropped or trigger an error, depending on IP version, flags and path. Fragment handling can create reliability and spoofing risks.','IPv6routersdonotfragment andDFIPv4maydrop.')
md(n,'so a DNS message plus IPv6 and UDP headers fits within a 1,280-byte minimum IPv6 MTU, and falling back to TCP for anything larger.','because1,232+40bytes of basic IPv6 header+8bytes of UDP equals1,280. This reduces fragmentation risk with those assumptions; extension headers, tunnels and IPv4 paths can require different budgets. Larger required answers can fall back to TCP.','1232notuniversalsafeeverypath.')
md(n,"every user of that resolver is sent to the attacker's address until the TTL expires.",'later matching lookups may receive poisoned cached data until expiry or replacement. Other caches, record types, validation and application authentication affect the result.','PoisoningnotguaranteedredirecteveryuserforTTL.')
md(n,'Over UDP, the resolver accepts the first response that matches:','For ordinary outstanding UDP queries, necessary response-matching checks include:','Matchingnecessarynotalwayssufficient acceptingDNSSEC/bailiwick.')
md(n,'only the 16-bit ID is unknown: **1 in 65,536** per forged packet.','if all other checked fields are known and the ID is uniform, the ID-match probability is **1 in65,536** per distinct guess. Acceptance also depends on racing the real response and passing other checks.','Stateprobabilitymodelassumptions.')
md(n,'a random name that cannot be cached:','a fresh random name unlikely to have a cached answer:','Randomnamescanbecachedandsynthesizednegatively.')
md(n,'at **6.6.6.6** (attacker-controlled),','at **192.0.2.66** (a documentation address standing for an attacker-controlled server),','UseRFC5737exampleIPnotrealallocatedthirdpartyaddress.')
md(n,'With around 100 forged responses per attempt, each attempt has roughly 100/65,536 ≈ 0.15% chance, so a few hundred attempts (seconds of traffic) give good odds.','In a simplified model with100distinct guesses and only a uniform16-bit ID unknown, p=100/65,536≈0.153% per attempt. Independent attempts need about454trials for50% success. This is probability arithmetic, not a measured attack duration; resolver caching and checks can change feasibility.','No universal secondsclaim; quantifyindependentassumptions andtiminggap.')
md(n,"With around 28,000 usable ports (Linux's default ephemeral range is 32768 to 60999) and the 16-bit ID, an attacker must guess from about 1.8 billion combinations.",'For a hypothetical28,000independent uniformly selected ports and16-bit ID, the joint space is1,835,008,000combinations. Actual resolver pools, NAT behaviour and predictability determine effective entropy; they need not equal the OS ephemeral range.','DNSresolverportpoolnotnecessarilyLinuxdefault; explicitmodel.')
md(n,'Ignore records in a response that are outside the zone being asked about.','Restrict which supplied records can update cache entries under the responding server’s authority and the resolver’s delegation context.','Bailiwickmorecomplex thanalloutofzonefieldsdiscard.')
md(n,'Servers echo the question exactly, so each letter adds about a bit of entropy.','With compatible servers that preserve question case and a resolver that checks it, randomising each independently chosen ASCII letter adds a bit to the guessing model. Not every server preserves case, and fallback policies matter.','0x20notuniversalechoguarantee.')
md(n,'**DNS cookies** (RFC 7873) and using TCP add further proof that the response came from the real server.','**DNS cookies** (RFC7873) and TCP make some off-path spoofing harder, but do not provide DNSSEC’s signed-data chain or protect against every on-path attacker.','TCP/cookiesnotservercryptographicauthgeneral.')
md(n,'**DNSSEC**, the only defence that makes forged data detectable rather than merely hard to guess.','**DNSSEC** cryptographically authenticates covered RRsets through a configured trust chain. Other authenticated transports protect their own endpoints and hops; these guarantees are different.','Onlydefencefalse:authenticatedtransport/TSIGalsointegrity.')
md(n,'Each zone signs its records,','A signed zone publishes signatures over covered RRsets,','Manyzonesunsigned;glue/delegationexceptions.')
md(n,'| DS | Hash of a child\'s key, in the parent |','| DS | Key tag, algorithm and digest fields binding a child owner name and DNSKEY, in the parent |','DSdigestincludesownernameandDNSKEYRDATA,notjustpublickey.')
md(n,"| NSEC / NSEC3 | Signed proof a name doesn't exist |",'| NSEC / NSEC3 | RRsets used with signatures for authenticated denial of a name/type or delegation properties |','DenialincludesNODATAandwildcard/delegationnotjustnames.')
md(n,'(all records of one name and type)','(records with the same owner name, class and type)','RRset includesclass.')
md(n,'so a zone must re-sign regularly or it goes dark.','so signatures must be renewed before they expire; affected data becomes bogus for validators enforcing the chain if no valid signatures remain.','Notallclientsorallzonecontentnecessarilydark.')
md(n,"Most zones use two keys: a **key-signing key** (KSK), which signs only the DNSKEY set, and a **zone-signing key** (ZSK), which signs everything else. The parent publishes a DS record with a hash of the child's KSK, linking the two zones.",'A split-key design uses a **KSK** to authenticate the DNSKEY RRset and a **ZSK** for other signed RRsets. These are operational roles, not mandatory two-key enforcement; a combined signing key is possible. A parent DS authenticates a selected child DNSKEY, which then authenticates the child DNSKEY set.','Unverifiedmostzonesandmandatorytwo-keyclaim;DSnotnecessarilyonlyKSK.')
a='''root DNSKEY (trust anchor, built in)
  signs -> DS for com.
com DNSKEY (matches that DS)
  signs -> DS for example.com.
example.com DNSKEY (matches DS)
  signs -> RRSIG over A record'''
b='''configured root trust anchor
  verifies root DNSKEY RRset
  root key verifies DS RRset for com.
  DS authenticates com. DNSKEY
  child key verifies its DNSKEY RRset
  com. key verifies example.com DS
  DS authenticates child DNSKEY set
  child key verifies A RRset RRSIG'''
md(n,a,b,'Keys verifyRRSIGoverRRsets;RRSIGnotrecordbeingsigned;includeDNSKEYsetauthentication andconfiguredanchor.')
md(n,'If every link verifies, it sets **AD** in its response. If any link fails, it returns **SERVFAIL** rather than a possibly forged answer. Validation happens in the resolver, so the stub on your laptop must trust the resolver and the path to it.','AD can signal that the relevant answer/authority data was validated, subject to request flags and response rules. With checking enabled, bogus data normally produces SERVFAIL; an authenticated unsigned delegation is **insecure**, not automatically bogus. CD can request data without that rejection. A non-validating stub must trust the resolver and protected path for its AD assertion; a validating stub can check signatures itself.','ADnotautomaticallrequests;secure/insecure/bogus/CDdistinction andlocalvalidation.')
md(n,'proves `bravo` does not exist.','proves the exact covered name does not exist; a complete NXDOMAIN proof also needs appropriate wildcard/closest-encloser handling.','NSECgapalone notfullwildcardNXDOMAINproof.')
md(n,'by following NSEC records an attacker can list every name in the zone.','following a conventional static NSEC chain can enumerate names represented in that chain. Delegations, empty nonterminals and online-signed denial techniques require care.','Notuniversalallnameszoneenumeration.')
md(n,'and is now the usual choice.','in the compared algorithms (64-byte ECDSA signatures versus256-byte RSA-2048 signatures). No deployment-prevalence claim is made here.','Removeunverifiedusualalgorithm; retainexactmathspecifiedalgorithms.')
md(n,'take the whole domain offline for validating resolvers. Several country-code TLDs and large domains have suffered such outages.','can make affected signed data fail validation once usable cached data and overlapping valid chains are exhausted.','Avoidallqueriesimmediatelyfail/cacheexceptions andunsourcedoutagecatalogue.')
md(n,'DNSSEC protects data between authoritative servers and the validating resolver.','DNSSEC authenticates signed data to whichever endpoint performs validation, through intervening caches or transports.','Dataobjectintegritynotfixedhop.')
md(n,'Anyone on the path (café Wi-Fi, your ISP) can see and alter every name you look up.','An observer on an unprotected DNS transport can inspect its messages and attempt modification; caches avoid some lookups, and validation can detect tampering.','Notallnamesvisible ifcacheDNSSEC/VPNetc.')
md(n,'Android\'s "Private DNS" setting uses DoT.','Android supports DoT; eligible updated Android versions can also use DoH over HTTP/3 for supported resolvers. The selected transport depends on version, updates and configuration.','AndroidDoT-onlyfalse sinceDoH3support2022.')
md(n,'On port 443 it looks like any other HTTPS traffic and can share a connection with ordinary web requests, so it is hard to block.','Sharing HTTPS transport can make classification less direct than a dedicated port, but resolver addresses, endpoint policy and traffic patterns can still enable blocking. DoH is not guaranteed indistinguishable from other HTTPS.','Noindistinguishabilityorunblockabilityguarantee.')
md(n,'so that no single party sees both who you are and what you asked.','to separate client addressing from query contents under its non-collusion and deployment assumptions. Correlation, colluding parties and identifying query contents remain limits.','ODoHrequiresnoncollusion anddoesnotguaranteeanonymity.')
md(n,'It does not authenticate the *data*;','It authenticates and integrity-protects the transport to the selected resolver, but does not independently authenticate authoritative *data*;','TLSdoesprovideintegrity, contrarysummary.')
md(n,'DoH also bypasses network-level DNS controls such as enterprise filtering or parental controls,','An independently selected DoH resolver can bypass policies implemented only in the network’s default resolver,','DoHcanuseenterprisefilterresolver;notinherentbypass.')
md(n,'TC forces a TCP retry, and 1,232 bytes is the safe EDNS size.','TC signals truncation and can prompt a TCP retry. The1,232-byte recommendation assumes a basic IPv6+UDP budget and is not a universal path guarantee.','Universalretryandsafesizefalse.')
md(n,'DoT and DoH give privacy on the last hop, not integrity.','Authenticated DoT/DoH protect confidentiality and integrity on the client-resolver transport. They do not replace independent DNSSEC validation of authoritative data.','DirectfalseencryptedDNSnointegrity.')
p=r/(n+'.md');p.write_text(p.read_text()+'\n> [!note] Content omitted after review\n> Universal attack completion times, resolver port pools, DNSSEC algorithm prevalence and a current browser/device encrypted-DNS policy matrix are absent because those implementation-specific measurements were not reliably established. The retained probability and packet-size calculations state their assumptions.\n')
