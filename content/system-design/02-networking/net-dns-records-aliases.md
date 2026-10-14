---
id: net-dns-records-aliases
title: "Choose DNS records and apex aliases"
level: basic
minutes: 3
summary: "Choose record types and understand how a provider-resolved apex alias can alter CDN steering."
sourceLesson: net-dns
---
DNS records describe more than addresses. The record type determines what the next resolver does, which matters when a CDN uses the source of a DNS query to choose an edge.

## Record types you'll actually use

| Type | Maps to | Example use |
|---|---|---|
| `A` | IPv4 address | `api` → 203.0.113.10 |
| `AAAA` | IPv6 address | `api` → 2001:db8::10 |
| `CNAME` | Another name | `www` → `shop.cdn.net` |
| `NS` | Name servers | Delegating a zone |
| `MX` | Mail servers | Email for the domain |
| `TXT` | Free text | SPF, domain verification |
| `SRV` | Host + port | Service discovery |
| `CAA` | Allowed CAs | Who may issue certs |

A few gotchas worth knowing:

- **A `CNAME` can't sit at the zone apex** (`example.com` itself), because the apex must also hold `NS` and `SOA` records and a CNAME cannot coexist with ordinary data at the same owner name (DNSSEC-related records have specific exceptions). Providers offer ALIAS/ANAME records or CNAME flattening to return address records without an ordinary apex CNAME. Supported targets differ: Route 53 alias records support selected AWS resources such as CloudFront, and eligible records in the same hosted zone; they are not aliases to arbitrary external hostnames.
- **CNAME chains cost lookups.** `www` → `shop.cdn.net` → `edge.cdn.net` → IP may need extra queries if the intermediate names aren't cached.
- **`HTTPS`/`SVCB` records** (RFC 9460) are newer: they can tell a browser up front that a site supports HTTP/3, saving a round trip of discovery.

### Aliases and location signals

With an ordinary CNAME, the user’s recursive resolver looks up the CDN’s target name. With a provider-resolved ALIAS or flattening implementation, the DNS provider may perform that lookup itself and return address records. A CDN that chooses an edge from the query’s source address may then see the provider’s location instead of the user’s resolver. Client-subnet forwarding or a CDN-specific integration can change this; it is a deployment-dependent risk, not a universal defect in apex aliases. Test the apex and `www` from representative user networks before choosing the arrangement.

## Key takeaways

- A and AAAA point to addresses; CNAME points to another name.
- The zone apex needs NS and SOA data, so it cannot be an ordinary CNAME.
- Provider-side alias resolution can change the resolver-location signal seen by a CDN; behaviour depends on the integration.

## Further reading

- [DNS clarifications: CNAME data (RFC 2181)](https://www.rfc-editor.org/rfc/rfc2181)
- [CNAME flattening (Cloudflare)](https://developers.cloudflare.com/dns/cname-flattening/)
- [Alias versus CNAME targets (Amazon Route 53)](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resource-record-sets-choosing-alias-non-alias.html)
- [Choosing a routing policy (Amazon Route 53)](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html)
