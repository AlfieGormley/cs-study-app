---
id: nsec-amplification-budget
title: Reflection and amplification budgets
level: basic
minutes: 4
summary: Reflection directs replies to a forged victim address.
sourceLesson: nsec-threats
---

Source-address spoofing becomes a bandwidth problem when public UDP servers send large replies to small requests. This unit traces that path and explains what limits how big the resulting flood can get.

## Amplification attacks

One important family of volumetric attacks combines spoofing with **reflection and amplification**:

```
 Attacker            Reflectors       Victim
   |  small query,       |               |
   |  src = victim IP    |               |
   |-------------------->|               |
   |                     | big response  |
   |                     |-------------->|
   |                     |  (x N)        |
```

1. The attacker sends a small UDP request to a public server (DNS resolver, NTP server, memcached instance), with the **source IP forged as the victim's**.
2. The server replies, to the victim, with a much larger response.
3. Thousands of reflectors do the same, all aiming at the victim.

UDP is used because there is no handshake to verify the source. The reflectors are innocent and the victim sees traffic from thousands of legitimate servers, which is hard to block.

> [!analogy] Real-world analogy: free catalogues sent to someone else's address
> Imagine posting thousands of one-line postcards to mail-order firms, each asking for their heaviest free catalogue and each giving your victim's address. Every firm innocently posts a catalogue, and the victim's doormat is buried under mail they never asked for.
>
> **How it maps:** The postcard is the small spoofed request, the firms are the reflectors, the forged address is the victim's IP in the source field, and the catalogue's weight compared with the postcard is the amplification factor. The firms cannot easily tell the request was forged, and the victim cannot simply refuse mail from well-known firms.
>
> **Where it stops:** Network reflection happens in milliseconds and at enormous scale, and each request costs the attacker almost nothing. Reflectors are limited by their own links and rate limits in a way the analogy hides, and networks can drop forged-source packets at the sender's ISP (BCP 38), which has no postal equivalent.

### The amplification factor

To compare reflectors, you need one number: how many bytes come back for every byte the attacker sends. That ratio is the **bandwidth amplification factor (BAF)**:

```formula essential
BAF = B_resp / B_req
where
BAF: the bandwidth amplification factor, a plain ratio with no unit; 1 means no amplification
B_resp: the size of the response the reflector sends to the victim, in bytes (B)
B_req: the size of the request the attacker sends to the reflector, in bytes (B)
B: bytes; one byte is 8 bits
In words: the amplification factor is how many times bigger the reflected response is than the spoofed request that triggered it.
```

For example, a 40-byte request that triggers a 1,400-byte response has a payload BAF of 35. The ratio depends on which bytes you count (payload only, or headers too; the next unit compares them) and on the particular query and server, so published figures are measurements, not constants.

The following historical examples use UDP-payload ratios. Rossow's 2014 measurements report sample means for particular queries and servers; GitHub's 2018 incident report cites an upper memcached example. They are not fixed protocol constants or current guarantees:

| Protocol | Approx. BAF |
|---|---|
| DNS | 28.7 (open resolvers), 54.6 (authoritative servers) |
| SSDP | 30.8 |
| NTP (monlist) | 556.9 |
| CharGEN | 358.8 |
| Memcached | Up to 51,000 in the cited 2018 report |

### How big can the flood get?

In an idealised model, the traffic arriving at the victim is the attackers' combined sending rate multiplied by the BAF. For example, 2,000 bots each sending 5 Mbps give 10 Gbps of requests; reflected through DNS servers with a BAF of about 50 (a round figure near the table's authoritative-server measurement), that is up to about 500 Gbps at the victim.

That figure is a ceiling, not a prediction. It assumes every request reaches a reflector, every reflector answers, and nothing is lost. Real attacks fall short because:

- **Reflectors have their own limits.** Each reflector's uplink, CPU and any response rate limiting cap what it can send, however many requests arrive.
- **Requests and replies are lost** along congested paths.
- **The BAF varies** by query and server, and the attacker may not find enough high-amplification reflectors.

Through exposed memcached servers even a 1 Gbps attacker could, in principle, generate tens of Tbps (terabits per second; 1 Tbps = 1,000 Gbps); in practice the reflectors' own links capped it. In 2018 GitHub absorbed a 1.35 Tbps memcached attack.

The practical lesson is that the BAF tells you which services are dangerous to leave exposed, while the reflectors' total capacity and the attacker's sending rate decide how large an attack actually gets.

## Key takeaways
- Reflection directs replies to a forged victim address.
- Specify which bytes a bandwidth amplification factor counts.
- Multiplying sending rate by BAF gives a ceiling that assumes sufficient reflector capacity and no loss.

## Further reading
- [UDP-Based Amplification Attacks — CISA](https://www.cisa.gov/news-events/alerts/2014/01/17/udp-based-amplification-attacks)
- [Amplification Hell: Revisiting Network Protocols for DDoS Abuse (NDSS 2014)](https://www.ndss-symposium.org/ndss2014/programme/amplification-hell-revisiting-network-protocols-ddos-abuse/)
- [February 28th DDoS incident report — GitHub blog](https://github.blog/news-insights/company-news/ddos-incident-report/)
