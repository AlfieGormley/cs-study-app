---
id: net-dns-steering-resilience
title: "DNS steering and resilient discovery"
level: basic
minutes: 3
summary: "Use DNS for coarse routing while recognising resolver geography, health and dependency limits."
sourceLesson: net-dns
---
Once record types and expiry are clear, DNS becomes a routing layer. It is best suited to choosing a region or data centre; use per-connection or per-request balancing inside the destination.

## DNS as a load-balancing tool

The authoritative server decides what to return, and it can be clever about it.

### Round-robin DNS

Return several `A` records and rotate their order:

Illustrative zone-file fragment, not a complete zone:

```dns
; One name publishes three backend IPs.
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
- **Weighted:** choose DNS answers with 90:10 relative weights for a `v1`/`v2` canary. Resolver caching and connection reuse mean request traffic need not follow those exact percentages.
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

- Plain round-robin DNS lacks backend health awareness and can distribute traffic unevenly.
- Geo steering commonly sees the recursive resolver; EDNS Client Subnet improves the signal with privacy and cache costs.
- Independent authoritative providers can reduce a DNS-provider failure risk; Kubernetes discovery still interacts with long-lived connections.

## Further reading

- [Choosing a routing policy (Amazon Route 53)](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html)
- [Client subnet in DNS queries (RFC 7871)](https://www.rfc-editor.org/rfc/rfc7871)
- [DNS for Services and Pods (Kubernetes)](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
