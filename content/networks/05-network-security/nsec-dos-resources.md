---
id: nsec-dos-resources
title: Which resource does a denial of service exhaust?
level: basic
minutes: 3
summary: Volumetric, protocol-state and application attacks exhaust different resources.
sourceLesson: nsec-threats
---

Traffic can be authentic and still exhaust a service. Identify the constrained resource before choosing a defence: link capacity, retained state and expensive application work need different controls.

## Denial of service

A **denial-of-service (DoS)** attack stops a service working for its legitimate users. A **distributed** DoS (DDoS) uses many sources, typically a **botnet** of compromised machines. The Mirai botnet of 2016, built from hacked cameras and routers, disrupted DNS resolution at Dyn and access to many customer websites.

DDoS attacks are classified by the resource they exhaust:

| Class | Exhausts | Measured in | Example |
|---|---|---|---|
| Volumetric | Link bandwidth | bits/s | UDP reflection |
| Protocol | State tables | packets/s | SYN flood |
| Application | Server CPU / app | requests/s | HTTP flood |

> [!analogy] Real-world analogy: three ways to stop a restaurant serving
> A restaurant can be stopped in three different ways. A traffic jam can block the only road in, so no customers arrive. Pranksters can book every table and never turn up, so real diners are turned away while the tables sit empty. Or a few customers can order the most elaborate dishes again and again, so the kitchen falls behind.
>
> **How it maps:** The road is link bandwidth (volumetric attacks), the reserved tables are connection state such as half-open TCP entries (protocol attacks), and the overworked kitchen is application CPU or worker threads (application-layer attacks). Each needs its own fix: a wider road or diversion upstream, a booking rule that holds no table until the guest confirms (SYN cookies), or limits and caching in the kitchen.
>
> **Where it stops:** Real attacks often mix types, and network traffic can be forged in ways diners cannot: thousands of sources may be spoofed or hijacked devices. A restaurant also cannot clone itself across the world the way an anycast scrubbing network spreads load.

### Volumetric

Fill the victim's pipe with more traffic than it can carry. If the link is 10 Gbps and 50 Gbps arrives, legitimate packets are dropped upstream, before your servers ever see them. You cannot filter your way out on your own equipment; mitigation must happen upstream, at your ISP or a scrubbing service (Cloudflare, Akamai, AWS Shield) with sufficient capacity and filtering for the particular attack. Cloudflare reported a record 31.4 Tbps attack, lasting about 35 seconds, in its [2025 Q4 report](https://blog.cloudflare.com/ddos-threat-report-2025-q4/) (published February 2026, and still its largest reported figure as of October 2026); this is a provider-reported measurement, not a limit on future attacks.

### Protocol

Exhaust a stateful resource with relatively little bandwidth. The classic is the **SYN flood**: send many TCP SYNs (often with spoofed sources) and never complete the handshake. Each one occupies a slot in the server's half-open connection queue until it times out.

The standard defence is **SYN cookies**. For a SYN handled with a cookie, the server avoids retaining a per-request half-open connection entry. It encodes limited information in the SYN-ACK's initial sequence number; the client's acknowledgment is that number plus one. The server validates the cookie and reconstructs connection state. Shared keys, counters and transient packet processing still exist. Firewalls and load balancers with connection tables are also protocol-attack targets.

### Application layer

Send requests that look legitimate but are expensive: searches, logins, uncached pages. A few thousand requests per second hitting a slow database query can do more damage than gigabits of junk.

**Slowloris** is the low-and-slow variant: open many HTTP connections and send headers one byte at a time, never finishing. Thread-per-connection servers (classic Apache) run out of workers. Defences include rate limiting, CAPTCHAs or challenges, caching, and event-driven servers or reverse proxies with short deadlines for receiving headers.

## Key takeaways
- Volumetric, protocol-state and application attacks exhaust different resources.
- A SYN handled by a cookie avoids a retained per-request half-open entry.
- A saturated access link needs mitigation before that link.

## Further reading
- [RFC 4987: TCP SYN Flooding Attacks and Common Mitigations](https://www.rfc-editor.org/rfc/rfc4987)
- [Understanding the Mirai Botnet (USENIX Security 2017)](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/antonakakis)
- [Slowloris (computer security) — Wikipedia](https://en.wikipedia.org/wiki/Slowloris_(computer_security))
