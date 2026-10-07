---
id: net-dns
title: "DNS: resolution, records, TTLs and traffic steering"
level: basic
minutes: 12
summary: How DNS resolution really works, the record types you'll use, how TTLs and caching shape failover, and how DNS doubles as a load balancer.
---

DNS (the Domain Name System) maps names like `api.example.com` to the addresses and services behind them. It's one of the oldest and largest distributed databases on the internet, and it's on the critical path of almost every request.

For a system designer, DNS matters for three reasons:

- It adds latency to the first request.
- Its **caching** decides how fast you can move traffic during a failover.
- It's a cheap, global **load-balancing and routing layer**.

## The cast of characters

| Component | Role |
|---|---|
| Stub resolver | Library in your OS; asks one resolver |
| Recursive resolver | Does the legwork, caches answers |
| Root servers | Know who runs each TLD |
| TLD servers | Know who runs each domain |
| Authoritative server | Holds the actual records |

There are 13 root server *identities* (a.root-servers.net to m.root-servers.net), run by 12 independent organisations. Each identity is served from many sites via **anycast**, and together they are deployed at many locations worldwide (the site count changes over time), so "13 root servers" is a naming detail, not a capacity limit. (The number 13 comes from fitting all their addresses into one small, original-size DNS response.)

## A full resolution, step by step

```
App -> Stub -> Recursive resolver
                 |
   1 "www.example.com?"   -> Root
     "ask .com servers"   <-
   2 "www.example.com?"   -> .com TLD
     "ask ns1.example.com"<-
   3 "www.example.com?"   -> ns1.example
     "A 192.0.2.10"       <-
                 |
          cache + return
```

1. The recursive resolver asks a **root** server, which replies with a *referral* to the `.com` servers.
2. It asks a **`.com`** server, which refers it to `example.com`'s name servers (from the `NS` records registered with the registrar).
3. It asks the **authoritative** server, which returns the answer.

The recursive resolver does **iterative** queries (it follows referrals itself); the stub makes a single **recursive** query ("give me the final answer"). In practice, the root and TLD referrals are almost always cached, so most lookups need only step 3 or are answered entirely from cache.

DNS normally runs over **UDP port 53**: one small packet each way, no handshake. If an answer is too big for the UDP size the client advertised (EDNS(0) lets clients advertise larger buffers; around 1,232 bytes is the common safe default since DNS Flag Day 2020, to avoid IP fragmentation), the server sets the *truncated* flag and the client retries over **TCP**. TCP support is mandatory, not optional (RFC 7766), and matters for DNSSEC-signed answers. DNS is also increasingly carried over TLS (DoT) or HTTPS (DoH) for privacy.

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

- **A `CNAME` can't sit at the zone apex** (`example.com` itself), because the apex must also hold `NS` and `SOA` records and a CNAME cannot coexist with ordinary data at the same owner name (DNSSEC-related records have specific exceptions). Providers work around this with "ALIAS" or "ANAME" records (Route 53 calls them alias records), which resolve the target server-side and return A records.
- **CNAME chains cost lookups.** `www` → `shop.cdn.net` → `edge.cdn.net` → IP may need extra queries if the intermediate names aren't cached.
- **`HTTPS`/`SVCB` records** (RFC 9460) are newer: they can tell a browser up front that a site supports HTTP/3, saving a round trip of discovery.

## TTLs and caching

Every record carries a **TTL** (time to live) in seconds. Any resolver can cache the answer for that long.

```
www.example.com. 300 IN A 203.0.113.10
                 ^^^
                 cache for 5 minutes
```

Caching is why DNS scales: a popular resolver answers millions of queries for `google.com` from memory. But it creates the central DNS trade-off:

| Short TTL (30–60 s) | Long TTL (hours–days) |
|---|---|
| Fast failover and changes | Slow to change |
| More queries, more latency | Fewer queries, faster |
| More load on your DNS | Resilient if DNS is down |

**Negative answers are cached too.** If a name doesn't exist (`NXDOMAIN`), resolvers cache that for the zone's negative TTL: the smaller of the `SOA` record's own TTL and its `MINIMUM` field (RFC 2308). If you query a name before creating it, clients may keep getting "doesn't exist" for a while after you add it.

**The TTL counts down in caches.** A resolver that cached a 300 s record 200 s ago hands it out with a TTL of 100. So the TTL a client sees is the *remaining* lifetime, and every cache downstream of it expires at the same moment, not 300 s after it asked.

> [!warning] TTLs are a request, not a guarantee
> Some resolvers enforce a minimum TTL, some clients (old JVMs, some mobile OSes, connection pools) cache much longer than told, and long-lived TCP connections never re-resolve at all. Many resolvers also implement **serve-stale** (RFC 8767): if the authoritative servers are unreachable, they keep answering from expired cache entries rather than failing. That's good for resilience, but it's another way old answers outlive their TTL. Plan for a long tail: after a DNS change, a small percentage of traffic often keeps hitting the old address for hours.

### The TTL-lowering playbook

If you're migrating a service to new IPs:

1. Days before, lower the TTL from, say, 86,400 s to 60 s.
2. Wait at least the *old* TTL (24 hours) so normally expiring caches no longer retain an answer with the old long TTL; caches need not refresh until queried.
3. Change the record. Most clients move within a minute or two.
4. Keep the old servers running until traffic drains.
5. Raise the TTL again.

Skipping step 2 is a classic mistake: caches still holding the 24-hour record won't look again for up to a day.

## DNS as a load-balancing tool

The authoritative server decides what to return, and it can be clever about it.

### Round-robin DNS

Return several `A` records and rotate their order:

```
api.example.com. 60 A 203.0.113.10
api.example.com. 60 A 203.0.113.11
api.example.com. 60 A 203.0.113.12
```

Clients usually try the first, so load spreads roughly evenly. (Not always: some operating systems sort addresses using RFC 6724 rules, which can undo the rotation and favour one IP.) It's simple, but crude:

- **No health awareness.** Plain DNS keeps handing out a dead server's IP.
- **Uneven.** One big corporate resolver may send thousands of users to the same IP.
- **Slow to react,** because of caching.

### Smarter answers

Managed DNS services (Route 53, Azure Traffic Manager, NS1, Cloudflare) layer policies on top:

- **Health-checked failover:** stop returning an IP when its health check fails.
- **Weighted:** send 90% to `v1`, 10% to `v2` for a canary.
- **Geo / latency-based:** return the region nearest the user (covered in the global traffic lesson).

The resolver, not the user, is what the authoritative server sees. If a user in Paris uses a resolver in Virginia, they may be sent to a US region. The **EDNS Client Subnet** extension lets resolvers pass along part of the client's IP (for example a /24) to fix this, at some cost to privacy and cache efficiency.

> [!tip] Where DNS load balancing fits
> DNS is great for coarse, global decisions: which region, which data centre. Inside a data centre, use a real load balancer, which reacts in seconds and balances per connection or per request.

## DNS as a single point of failure

If your authoritative DNS is unreachable, clients without usable cached or serve-stale answers cannot resolve your names, even if every server is healthy. In October 2016, a DDoS on Dyn made Twitter, GitHub, Netflix and others unreachable for many users.

Mitigations:

- Use a provider with a large **anycast** network.
- Consider **two independent DNS providers** (both listed in your `NS` records).
- Don't set TTLs so low that a short DNS outage immediately becomes a full outage.

## Inside your own systems

DNS is also the default service-discovery mechanism inside clusters. In Kubernetes, a normal `orders.prod.svc.cluster.local` Service resolves to a stable virtual IP; routing updates behind it handle changing Pods without a DNS change. Headless Services instead return Pod addresses, so DNS caching matters directly. Long-lived connections can stay attached to an existing backend in either case.

## Key takeaways

- Resolution goes stub → recursive resolver → root → TLD → authoritative, with caching at every level.
- Know `A`, `AAAA`, `CNAME`, `NS`, `MX`, `TXT`, `SRV` and why a CNAME can't sit at the apex.
- TTL is a trade-off between agility and query load; lower it well before a planned change.
- TTLs are often not honoured exactly, so expect a long tail of stale clients.
- DNS can do coarse load balancing and failover, but it's slow to react and sees the resolver, not the user.
- Your DNS provider is a critical dependency; treat it like one.

## Further reading

- [Domain Name System (Wikipedia)](https://en.wikipedia.org/wiki/Domain_Name_System)
- [List of DNS record types (Wikipedia)](https://en.wikipedia.org/wiki/List_of_DNS_record_types)
- [RFC 1035: Domain names, implementation and specification](https://www.rfc-editor.org/rfc/rfc1035)
- [RFC 2308: Negative caching of DNS queries](https://www.rfc-editor.org/rfc/rfc2308)
- [Choosing a routing policy (Amazon Route 53)](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html)
