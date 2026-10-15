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

### Volumetric

Fill the victim's pipe with more traffic than it can carry. If the link is 10 Gbps and 50 Gbps arrives, legitimate packets are dropped upstream, before your servers ever see them. You cannot filter your way out on your own equipment; mitigation must happen upstream, at your ISP or a scrubbing service (Cloudflare, Akamai, AWS Shield) with sufficient capacity and filtering for the particular attack. Cloudflare reported a 29.7 Tbps attack in its [2025 Q3 report](https://blog.cloudflare.com/ddos-threat-report-2025-q3/); this is a provider-reported measurement, not a guaranteed limit on future attacks.

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
- [UDP-Based Amplification Attacks — CISA](https://www.cisa.gov/news-events/alerts/2014/01/17/udp-based-amplification-attacks)
- [RFC 2827 (BCP 38): Network Ingress Filtering](https://www.rfc-editor.org/rfc/rfc2827)
- [RFC 4987: TCP SYN Flooding Attacks and Common Mitigations](https://www.rfc-editor.org/rfc/rfc4987)
- [Amplification Hell: Revisiting Network Protocols for DDoS Abuse (NDSS 2014)](https://www.ndss-symposium.org/ndss2014/programme/amplification-hell-revisiting-network-protocols-ddos-abuse/)
- [February 28th DDoS incident report — GitHub blog](https://github.blog/news-insights/company-news/ddos-incident-report/)
- [Understanding the Mirai Botnet (USENIX Security 2017)](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/antonakakis)
