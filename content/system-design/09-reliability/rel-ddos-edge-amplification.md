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

> [!example] Amplification maths
> A memcached reflection attack sends a ~15-byte request with a spoofed source address; the server replies with up to hundreds of kilobytes to the victim. Amplification factors above 10,000× were observed in 2018, which is how attacks passed 1 Tbps. Never expose UDP services like memcached to the internet.

The arithmetic behind amplification: the attacker pays for small requests, and the victim receives large replies. The following ideal model uses the same payload accounting for sizes and bit rates. The 15-byte measurement is a UDP payload: IP/UDP headers, fragmentation and other network overhead lower the corresponding on-wire amplification.

```formula
A = S_resp / S_req
B_victim = B_attack × A
B_victim = 100 Mbps × 10,000 = 1 Tbps
where
A: the amplification factor, how many times bigger each reply is than the request that triggered it
S_resp: the reflected reply’s payload size, in bytes
S_req: the spoofed request’s payload size, in bytes (about 15 in the cited memcached measurement)
B_victim: the traffic arriving at the victim, in bits per second
B_attack: the illustrative request-payload bit rate, here 100 megabits per second (Mbps), ignoring wire overhead
Mbps: megabits per second (1,000,000 bits per second)
Tbps: terabits per second (1,000,000 Mbps)
In words: with a 10,000× amplifier, an attacker sending a modest 100 Mbps of requests points 1 Tbps of replies at the victim.
```

The 100 Mbps is illustrative. Real reflection attacks are limited by how many open reflectors exist and how much each one can send, not just by the factor.

## Key takeaways

- Layer edge absorption, authenticated origin access, rate limits, bot/WAF controls and cheap admission.
- Residential-IP application floods can defeat naive per-IP limits and random-query caches.
- Reflection amplification redirects much larger replies to a spoofed victim; close exposed reflectors and filter forged source traffic.

## Further reading

- [AWS best practices for DDoS resiliency](https://docs.aws.amazon.com/whitepapers/latest/aws-best-practices-ddos-resiliency/welcome.html)
- [Denial-of-service attack (Wikipedia)](https://en.wikipedia.org/wiki/Denial-of-service_attack)
- [Cloudflare memcached amplification measurements](https://blog.cloudflare.com/memcrashed-major-amplification-attacks-from-port-11211/)
