---
id: ip-bgp-commercial-policy
title: Commercial routing and traffic engineering
level: advanced
minutes: 3
sourceLesson: ip-bgp
summary: Trace simplified customer, peer and provider export policy and explain traffic-steering limits.
---

Trace simplified customer, peer and provider export policy and explain traffic-steering limits.

## The economics: who carries whose traffic

Relationships between ASes are commercial:

- **Customer to provider**: the customer pays for transit to the whole Internet.
- **Inter-AS peering**: two networks exchange agreed traffic; settlement-free peering has no traffic settlement payment between them, but paid peering and infrastructure costs also exist.

A simplified commercial policy consistent with the **Gao–Rexford** model is shown below. Preferring customers over peers/providers is the key ranking restriction here; ranking peers above providers is an additional illustrative choice, not required by their Guideline A:

| Learnt from | Prefer | Export to |
|---|---|---|
| Customer | Most (they pay you) | Everyone |
| Peer | Middle | Customers only |
| Provider | Least (you pay) | Customers only |

The export rule produces **valley-free** paths: traffic goes up through providers, across at most one peer link, and down through customers. Under these BGP export restrictions a network does not provide transit between its providers. Real contracts and routing policies can differ; results about BGP convergence require additional model assumptions, including an acyclic customer-provider hierarchy.

### Traffic engineering

Operators steer traffic with the tools above:

- **LOCAL_PREF** controls which way traffic *leaves* your network.
- **AS_PATH prepending** (adding your own ASN several times) makes a path look longer, to discourage traffic *entering* via that link. Neighbours' LOCAL_PREF overrides it.
- **More-specific prefixes**: announce a /23 everywhere and two /24s from different sites. Where those more-specific routes are accepted and installed, longest-prefix match selects them.
- **Anycast**: announce the same prefix from many locations. Routing policy selects one reachable announcement; this need not be the geographically closest or lowest-latency site. DNS services can use this arrangement.

RFC 7454 documented IPv4 **/24** and IPv6 **/48** as common public-routing specificity limits in 2015, while explicitly allowing those practices to change. Acceptance depends on the receiving network and its current policy. More-specific routes can be useful in private or explicitly agreed routing; no announcement length guarantees that a route spreads everywhere.

## Key takeaways
- The Gao–Rexford model imposes ranking/export constraints and additional hierarchy assumptions.
- LOCAL_PREF steers outbound choice; prepending only influences neighbours that reach that comparison.
- Accepted more-specific routes steer their covered destinations.
- Anycast routing need not select the geographically closest or fastest site.

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
