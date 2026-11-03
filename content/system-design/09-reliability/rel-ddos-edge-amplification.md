---
id: rel-ddos-edge-amplification
title: DDoS layers and reflection amplification
level: advanced
minutes: 3
summary: Match traffic attacks to edge absorption, origin controls and bounded expensive work.
sourceLesson: rel-security
---

Overload controls handled accidental demand. DDoS adds an adversary who deliberately maximises cost and bypasses simple limits. Network-volume attacks and apparently valid expensive requests require different layers, and all protection has finite capacity.

## DDoS mitigation

A **distributed denial-of-service** attack floods you with traffic from many sources. Types:

- **Volumetric (L3/L4)**: UDP floods, reflection/amplification (DNS, NTP, memcached). Measured in Tbps.
- **Protocol**: SYN floods exhausting connection tables.
- **Application (L7)**: HTTP floods of expensive requests (search, login), which look like real users.

Defences, layered:

1. **Absorb at the edge**: anycast CDN or DDoS service (AWS Shield, Cloudflare, Google Cloud Armor) with huge distributed capacity. Anycast can distribute traffic across an operator's sites, depending on routing and source geography; it does not guarantee even distribution or unlimited capacity.
2. **Hide the origin**: restrict origin ingress and authenticate your own edge (for example with mTLS or provider-supported origin authentication). An allow-list of shared CDN ranges alone may still admit another customer's traffic.
3. **Rate limit** per IP, per API key and per user, at the edge and the gateway.
4. **WAF rules and bot detection** for L7 patterns; challenges (CAPTCHA, proof-of-work) for suspicious clients.
5. **Make expensive endpoints cheap**: cache safe responses, require appropriate auth and use bounded admission queues. Authentication alone does not make a costly request cheap. Combine with the load shedding and autoscaling from earlier lessons.
6. **Reduce attack surface**: close unused ports, don't expose databases or admin panels publicly.

> [!example] Reflection amplification
> A memcached reflection attack sends a ~15-byte request with a spoofed source address; the server replies with up to hundreds of kilobytes to the victim. Amplification factors above 10,000× were observed in 2018, which is how attacks passed 1 Tbps. Never expose UDP services like memcached to the internet.

The mechanism behind amplification: the attacker pays for small requests, and the victim receives large replies. Use consistent payload or wire accounting when comparing amplification measurements. The 15-byte measurement is a UDP payload: IP/UDP headers, fragmentation and other network overhead lower the corresponding on-wire amplification.

Real reflection attacks are limited by how many open reflectors exist and how much each one can send, not just by the factor.

## Key takeaways

- Layer edge absorption, authenticated origin access, rate limits, bot/WAF controls and cheap admission.
- Residential-IP application floods can defeat naive per-IP limits and random-query caches.
- Reflection amplification redirects much larger replies to a spoofed victim; close exposed reflectors and filter forged source traffic.

## Further reading

- [AWS best practices for DDoS resiliency](https://docs.aws.amazon.com/whitepapers/latest/aws-best-practices-ddos-resiliency/welcome.html)
- [Denial-of-service attack (Wikipedia)](https://en.wikipedia.org/wiki/Denial-of-service_attack)
- [Cloudflare memcached amplification measurements](https://blog.cloudflare.com/memcrashed-major-amplification-attacks-from-port-11211/)
