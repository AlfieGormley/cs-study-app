---
id: ip-bgp
title: BGP, hijacks and RPKI
level: advanced
minutes: 17
summary: How independent networks glue the Internet together with BGP, how routes are chosen by policy rather than distance, how hijacks and leaks happen, and what RPKI does and doesn't fix.
---

OSPF computes paths within a routing domain using configured costs; that does not make its routers inherently trustworthy. Internet inter-domain routing must also accommodate independent networks, many of them competitors, with different policies. They need to exchange reachability without revealing their insides or giving up control.

That protocol is the **Border Gateway Protocol**, BGP-4 (RFC 4271). It's often called the glue of the Internet, and it runs on trust to a degree that surprises people.

## Autonomous systems

An **autonomous system** (AS) is a network under one administrative policy: an ISP, a cloud provider, a university, a large company. Public ASNs are allocated through Internet number registries; private ASNs can be used in appropriate private routing contexts.

- ASN fields expanded from 16 to 32 bits (RFC 6793). Not every encodable value is assignable: 65535 and 4294967295, for example, are reserved.
- Private ranges exist for internal use: 64512–65534 and 4200000000–4294967294.
- AS numbers in the examples below illustrate routing policy; they are not instructions to announce those routes publicly.

An AS can use an IGP such as OSPF or IS-IS internally, alongside internal BGP. eBGP exchanges routes between ASes; designs can also use eBGP inside one organisation.

## A path-vector protocol

BGP is a **path-vector** protocol. Like distance vector, routers tell neighbours what they can reach. But instead of a distance, an ordinary **AS_PATH** sequence records advertised AS traversal, with repeated entries possible for prepending. It is not cryptographic proof of the actual forwarding path. For example:

```
203.0.113.0/24
  AS_PATH: 3356 1299 65010
            ^         ^
         neighbour   origin
```

That list does two jobs:

- **Loop prevention**: normal AS-loop checking excludes a received route containing the local ASN. Explicit configuration exceptions exist; this mechanism does not eliminate every possible forwarding loop or policy oscillation.
- **Policy**: operators can filter or rank the advertised path, subject to the limits of trusting that advertisement.

### Sessions

BGP routers ("speakers") form sessions over **TCP port 179**, using configured peer relationships. Base BGP has no OSPF-style multicast Hello discovery, although implementations can automate provisioning or accept dynamic peers under configured rules. Its four base message types are:

| Message | Purpose |
|---|---|
| OPEN | Start session, exchange ASN and hold time |
| UPDATE | Announce or withdraw prefixes |
| KEEPALIVE | Maintain liveness; one third of a nonzero hold time is a suggested maximum interval |
| NOTIFICATION | Error; close the session |

After the initial permitted route exchange, normal updates are incremental. Route-refresh extensions can request re-advertisements. KEEPALIVE or UPDATE receipt can reset the hold timer; negotiated hold time zero disables this timer and KEEPALIVEs. Memory needs depend on prefixes, paths, attributes and implementation.

### eBGP and iBGP

- **eBGP** runs between different ASes, usually over a direct link.
- **iBGP** runs between routers in the *same* AS, to distribute BGP reachability internally, subject to selection and export policy.

iBGP does not prepend the local ASN, so the AS_PATH cannot record internal router traversal. In base iBGP, an iBGP-learned route is not re-advertised to another internal peer. A full mesh therefore needs n(n−1)/2 sessions: 4,950 for 100 routers. **Route reflectors** (RFC 4456) relax that restriction: selected client routes can be reflected to clients and non-clients, while non-client routes are reflected to clients. ORIGINATOR_ID and CLUSTER_LIST support reflection-loop detection. Confederations are another scaling approach.

## Path attributes and best-path selection

Each route carries **attributes**:

- **AS_PATH**: the advertised AS traversal, possibly including prepending.
- **NEXT_HOP**: where to send the traffic.
- **LOCAL_PREF**: a preference set *inside* your AS and shared over iBGP. Higher wins.
- **MED** (multi-exit discriminator): a hint from a neighbour about which of several links into it you should use. Lower wins.
- **Communities**: tags like `65010:100` that carry meaning by agreement, such as "don't announce this to peers" or "prepend twice towards Europe".

Among eligible routes for the same prefix, a common Cisco-style sequence is below. Reachability checks, vendor-specific steps (including Cisco weight before LOCAL_PREF), configuration and multipath settings matter; this is not a universal BGP ordering:

1. Highest **LOCAL_PREF**.
2. Prefer routes originated locally.
3. Shortest **AS_PATH**.
4. Lowest **origin** attribute (IGP, then EGP, then incomplete). These are attribute codes, not proof that the route was learned through an IGP.
5. Lowest **MED** (normally only between routes from the same neighbouring AS).
6. **eBGP** over iBGP.
7. Lowest IGP cost to the NEXT_HOP ("hot potato").
8. Further implementation-dependent tie-breakers, including route age in some eBGP cases and router IDs.

This executable teaching model ranks already eligible routes, assumes equal weight/local-origination status, counts AS_SEQUENCE entries, compares MED across all candidates, and uses input order for complete ties. It deliberately omits the rest of real BGP selection:

```python
def rank(r):
    return (-r["lp"],
            len(r["path"]),
            r["origin"],
            r["med"],
            0 if r["ebgp"] else 1,
            r["igp"])

routes = [
    dict(name="transit", lp=100,
         path=[64500, 3356, 65010],
         origin=0, med=0,
         ebgp=True, igp=10),
    dict(name="peer", lp=200,
         path=[64600, 64700, 65010],
         origin=0, med=0,
         ebgp=True, igp=10),
    dict(name="customer", lp=300,
         path=[65010, 65010, 65010],
         origin=0, med=0,
         ebgp=True, igp=10),
]
best = min(routes, key=rank)
print(best["name"])  # customer
```

> [!example] A worked choice
> Your AS hears 203.0.113.0/24 three ways:
> - From a transit provider: LOCAL_PREF 100, path `64500 3356 65010` (3 ASes).
> - From a peer: LOCAL_PREF 200, path `64600 64700 65010` (3 ASes).
> - From customer 65010 directly: LOCAL_PREF 300, path `65010 65010 65010` (prepended to 3).
>
> With all eligibility checks passed and earlier vendor-specific preferences equal, LOCAL_PREF decides: the customer route wins at 300. The customer's prepending was meant to push traffic away, but it only affects step 3, which is never reached.

Note what's missing: bandwidth, latency, congestion. BGP picks paths by **policy** and AS count, not performance. The shortest AS_PATH may cross an ocean twice.

## The economics: who carries whose traffic

Relationships between ASes are commercial:

- **Customer to provider**: the customer pays for transit to the whole Internet.
- **Peer to peer**: two networks exchange agreed traffic; settlement-free peering has no traffic settlement payment between them, but paid peering and infrastructure costs also exist.

A simplified commercial policy consistent with the **Gao–Rexford** model is shown below. Preferring customers over peers/providers is the key ranking restriction here; ranking peers above providers is an additional illustrative choice, not required by their Guideline A:

| Learnt from | Prefer | Export to |
|---|---|---|
| Customer | Most (they pay you) | Everyone |
| Peer | Middle | Customers only |
| Provider | Least (you pay) | Customers only |

The export rule produces **valley-free** paths: traffic goes up through providers, across at most one peer link, and down through customers. Under these export restrictions a network does not provide transit between its providers. Real contracts and routing policies can differ; convergence results require additional model assumptions, including an acyclic customer-provider hierarchy.

### Traffic engineering

Operators steer traffic with the tools above:

- **LOCAL_PREF** controls which way traffic *leaves* your network.
- **AS_PATH prepending** (adding your own ASN several times) makes a path look longer, to discourage traffic *entering* via that link. Neighbours' LOCAL_PREF overrides it.
- **More-specific prefixes**: announce a /23 everywhere and two /24s from different sites. Where those more-specific routes are accepted and installed, longest-prefix match selects them.
- **Anycast**: announce the same prefix from many locations. Routing policy selects one reachable announcement; this need not be the geographically closest or lowest-latency site. DNS services can use this arrangement.

RFC 7454 documented IPv4 **/24** and IPv6 **/48** as common public-routing specificity limits in 2015, while explicitly allowing those practices to change. Acceptance depends on the receiving network and its current policy. More-specific routes can be useful in private or explicitly agreed routing; no announcement length guarantees global propagation.

## When BGP goes wrong

BGP believes what neighbours tell it unless operators filter. Mistakes and attacks spread as fast as legitimate updates.

### Hijacks

A **hijack** is an unauthorised route announcement for address space. A more-specific announcement is especially effective, because longest-prefix match prefers it where it is accepted and installed alongside the covering route.

- **Pakistan Telecom and YouTube, February 2008.** Ordered to block YouTube domestically, Pakistan Telecom (AS17557) announced 208.65.153.0/24, a more specific part of YouTube's 208.65.152.0/22. Its upstream, PCCW, passed it on without filtering, and much of the world's YouTube traffic was drawn to Pakistan and dropped, during the interval documented by RIPE RIS from 18:47 to 21:01 UTC on 24 February. YouTube first counter-announced the /24, then two /25s; acceptance varied by network.
- **Amazon Route 53, April 2018.** Attackers announced more-specific routes for some of Amazon's DNS address space via a small ISP (eNet, AS10297). For about two hours, DNS queries for the cryptocurrency site MyEtherWallet were answered by an attacker's server, which sent users to a phishing copy. Cloudflare documented the redirection and certificate-warning risk; this lesson does not establish a reliable total financial loss.

### Leaks

A **route leak** breaks the export rules: a network re-announces routes it should have kept to itself, usually from one provider to another.

- **Verizon and DQE, June 2019.** DQE Communications used a "BGP optimiser" that generated more-specific routes internally. These leaked to a customer, Allegheny Technologies, which announced them to its other provider, Verizon (AS701). Verizon accepted and propagated them, and traffic for parts of Cloudflare, Amazon and others was drawn through a small network that couldn't carry it.

### Self-inflicted: Facebook, October 2021

On 4 October 2021 a maintenance command accidentally disconnected Facebook's backbone. Facebook's DNS servers are built to **withdraw** their BGP announcements if they can't reach the data centres, so they did. The prefixes holding Facebook's authoritative DNS vanished from the Internet, `facebook.com` stopped resolving, and the backbone disconnection disrupted Facebook services. Cached DNS answers could still exist; DNS failure was a consequence that compounded the underlying network outage. Internal tools depended on the same network, which slowed the recovery.

## RPKI: authorising route origins

The **Resource Public Key Infrastructure** adds cryptographic evidence about who may originate a prefix.

1. Resource certificates form a validation chain rooted in configured trust anchors. They attest resource control within this system, rather than legal ownership.
2. A holder signs a **ROA** (route origin authorisation): "AS X may originate prefix P, up to length L."
3. Validator software checks signed objects and supplies validated prefix/origin/max-length records to routers. For the simple AS_SEQUENCE paths here, the origin is the final ASN.

**Route origin validation** (ROV, RFC 6811) gives each route one of three states:

| State | Meaning |
|---|---|
| Valid | At least one covering validated record authorises both origin and length |
| Invalid | Covering validated records exist, but none authorises both origin and length |
| NotFound | No ROA covers it |

Operators choose how to use validation states; **dropping Invalid** routes is a filtering policy, not an automatic effect of computing ROV. Had YouTube's /22 had a ROA with max length 22, Pakistan Telecom's /24 would have been Invalid twice over (wrong origin, too long).

> [!warning] Max length cuts both ways
> In a hypothetical prefix-arithmetic example, a ROA for 192.0.0.0/22 with max length 24 authorises your /24s, but if you only announce the /22, an attacker can announce a /24 with *your* ASN as origin and pass validation. RFC 9319 recommends ROAs that match exactly what you announce.

### What RPKI doesn't fix

ROV checks the **origin only**. An attacker who announces your prefix with a fake path ending in your ASN (`666 65010`) can be Valid when origin and prefix length are authorised. ROV does not validate the intervening path or detect a leak that retains an authorised origin.

- **BGPsec** (RFC 8205) provides signed AS-path propagation for participating BGPsec speakers. Its protection depends on cryptographic validation and deployment; it is not a claim that every forwarding router signs every packet.
- **ASPA** (autonomous system provider authorisation) publishes authorised provider relationships. The IETF verification draft retrieved for this review is work in progress (August 2026); detection depends on relationship data, direction and validation rules, and is not guaranteed for every forged path.
- **Filtering** remains the basic defence: providers should accept from customers only the prefixes they're registered to announce, and cap how many. The MANRS initiative publishes these practices as baseline norms.

> [!note] Content omitted after review
> Current AS/route counts, adoption percentages, router performance guarantees and the Route 53 incident's financial loss are omitted because this review did not establish reliable dated evidence for them. No live Internet routing changes were performed to validate the examples.

## Key takeaways
- BGP connects autonomous systems; it's a path-vector protocol whose AS_PATH supports AS-loop checks and policy.
- Sessions run over TCP 179; iBGP needs a full mesh or route reflectors because base iBGP restricts re-advertising internally learned routes; confederations provide another design option.
- LOCAL_PREF and AS_PATH are major selection inputs; exact ordering and tie-breaks depend on implementation and configuration.
- Commercial relationships drive policy: prefer customers, export peer and provider routes only to customers.
- Hijacks exploit trust and longest-prefix match; leaks break export rules; both have caused global outages.
- RPKI ROV classifies origin authorisation; local policy decides rejection. It does not prove the whole path or eliminate route leaks.

## Further reading
- [RFC 4271: A Border Gateway Protocol 4 (BGP-4)](https://www.rfc-editor.org/rfc/rfc4271)
- [Border Gateway Protocol — Wikipedia](https://en.wikipedia.org/wiki/Border_Gateway_Protocol)
- [Understanding how Facebook disappeared from the Internet — Cloudflare blog](https://blog.cloudflare.com/october-2021-facebook-outage/)
- [How Verizon and a BGP Optimizer Knocked Large Parts of the Internet Offline — Cloudflare blog](https://blog.cloudflare.com/how-verizon-and-a-bgp-optimizer-knocked-large-parts-of-the-internet-offline-today/)
- [RFC 6811: BGP Prefix Origin Validation](https://www.rfc-editor.org/rfc/rfc6811)
- [BGP hijacking — Wikipedia](https://en.wikipedia.org/wiki/BGP_hijacking)
- [MANRS](https://www.manrs.org/)

- [RIPE NCC: YouTube hijacking presentation and timeline](https://ripe56.ripe.net/presentations/Refice-YouTube_Prefix_Hijacking.pdf)
- [Meta: October 2021 outage details](https://engineering.fb.com/2021/10/05/networking-traffic/outage-details/)
- [Cloudflare: BGP leaks and cryptocurrencies](https://blog.cloudflare.com/bgp-leaks-and-crypto-currencies/)
- [Cisco: BGP best-path algorithm](https://www.cisco.com/c/en/us/support/docs/ip/border-gateway-protocol-bgp/13753-25.html)
- [IETF: ASPA verification draft](https://datatracker.ietf.org/doc/draft-ietf-sidrops-aspa-verification/)
- [RFC 9319: RPKI maxLength](https://www.rfc-editor.org/rfc/rfc9319)
