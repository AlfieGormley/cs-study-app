---
id: wm-debug-path-and-dns
title: Interpreting traceroute, mtr and DNS evidence
level: advanced
minutes: 3
summary: A missing intermediate reply is not proof that application packets are dropped there.
sourceLesson: wm-debugging
---

Once a symptom is defined, the next questions are which way packets go and whether the name even resolves to the right place. Traceroute, mtr and dig answer those, but each shows side effects of probes rather than the path your application's packets take, so reading them carefully matters as much as running them.

## traceroute and mtr: where the path goes

`traceroute` sends probes with TTL 1, 2, 3, and so on. A router discards a unicast probe whose TTL expires and normally generates **ICMP Time Exceeded**, subject to rate limits and exceptions. Missing or filtered replies can hide hops, and probe paths can differ. Linux `traceroute` uses UDP probes to high ports by default (`-I` for ICMP, `-T` for TCP); Windows `tracert` uses ICMP.

```
 1  10.0.0.1          1.2 ms
 2  100.64.12.1       8.9 ms
 3  * * *
 4  ldn-core-2       10.4 ms
 5  nyc-core-1       78.1 ms
 6  nyc-edge-3       77.9 ms
 7  203.0.113.80     78.6 ms
```

How to read it:

- **`* * *`** at hop 3: no reply was received for those probes. Filtering, loss, rate limits or different paths can explain it. Later replies show that some probes reached farther, not that every packet passed one identified router.
- **The jump at hop 5** (10 ms → 78 ms) could be consistent with a longer path, but hostnames and hop RTT differences alone cannot identify a cable, its distance or the exact forward-link delay.
- **Latency that rises at one hop and falls again** at later hops can reflect reply processing, rate limits, differing return paths or different samples. It does not establish equivalent forwarding delay for application traffic.
- Paths are often **asymmetric**: replies may come back a different way, which traceroute cannot show. Run it in both directions when you can.

**mtr** runs traceroute continuously and shows loss and latency per hop. Low intermediate response rates with healthy destination samples often suggest reply handling rather than persistent forwarding loss. They do not prove that explanation: probes are separate samples and can take different paths. End-to-end measurements and captures are needed; genuine forwarding loss need not appear identically at every later line.

## dig: is it DNS?

```
$ dig +short api.example.com
203.0.113.80
$ dig @1.1.1.1 api.example.com
$ dig +trace api.example.com
```

- Compare resolvers with awareness of split-horizon policy, CDN/geographic responses, cache age and DNSSEC. Different answers are not automatically stale or incorrect.
- Check the **TTL** in the answer section: after a migration, caches may retain an earlier answer for its remaining TTL, while application caching and resolver serve-stale policies can alter observed timing.
- `+trace` walks from the root, showing which authoritative servers answer and where delegation breaks.
- Do not forget the client's own resolution path: `/etc/hosts`, search domains, and whether the app prefers IPv6 (an AAAA record pointing somewhere broken causes delays before falling back).

## Key takeaways
- A missing intermediate reply is not proof that application packets are dropped there.
- Compare DNS answers in context, including caches, policy and the client’s resolution path.

## Further reading
- [Traceroute — Wikipedia](https://en.wikipedia.org/wiki/Traceroute)
- [mtr on GitHub](https://github.com/traviscross/mtr)
- [BIND: dig command documentation](https://bind9.readthedocs.io/en/latest/manpages.html)
