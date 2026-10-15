---
id: nsec-amplification-budget
title: Reflection and amplification budgets
level: basic
minutes: 5
summary: Reflection directs replies to a forged victim address.
sourceLesson: nsec-threats
---

Source-address spoofing becomes a bandwidth problem when public UDP servers send large replies to small requests. This unit traces that path and calculates its idealised byte budget.

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

### The amplification factor

To compare reflectors, and to estimate how big an attack can get, you need one number: how many bytes come back for every byte the attacker sends. That ratio is the **bandwidth amplification factor (BAF)**:

```formula
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

If every reflector answers every request, the traffic arriving at the victim is the attacker's sending rate multiplied by the BAF. The attacker's sending rate is in turn the number of bots times each bot's upload rate:

```formula
R_send = N_bots r_bot
R_victim = R_send BAF
where
R_send: the attacker's total sending rate, in megabits per second (Mbps)
N_bots: the number of compromised devices (bots) sending spoofed requests
r_bot: the upload rate of each bot, in megabits per second (Mbps)
R_victim: the traffic rate arriving at the victim, in the same unit as R_send
BAF: the bandwidth amplification factor of the reflectors used, a plain ratio
Mbps: megabits per second; 1,000 Mbps = 1 gigabit per second (Gbps)
In words: the flood hitting the victim is the attackers' combined upload multiplied by how much each reflector amplifies it.
```

This assumes a payload-rate model: reflectors have enough capacity, nothing is lost on the way, and every request is answered. Real attacks fall short of it, because reflectors' own links and rate limits cap what they can send.

**Working it out.** A botnet has 2,000 devices, each able to send 5 Mbps, reflected through open DNS resolvers with a BAF of 50:

```formula
R_send = 2000 × 5 Mbps = 10000 Mbps
R_send = 10 Gbps
R_victim = 10 Gbps × 50 = 500 Gbps
where
R_send: the botnet's total sending rate
R_victim: the traffic rate arriving at the victim
Mbps: megabits per second, millions of bits per second
Gbps: gigabits per second; 1 Gbps = 1,000 Mbps
In words: 2,000 bots at 5 Mbps send 10 Gbps in total, and a fifty-fold reflector turns that into about 500 Gbps at the victim.
```

Through exposed memcached servers even a 1 Gbps attacker could, in principle, generate tens of Tbps (terabits per second; 1 Tbps = 1,000 Gbps); in practice the reflectors' own links cap it. In 2018 GitHub absorbed a 1.35 Tbps memcached attack.

The same calculation as Python code:

```python
def attack_gbps(bots, mbps_each, baf):
    # Convert combined Mbps into Gbps.
    sent = bots * mbps_each / 1000
    # Apply the stated reflector ratio.
    return sent * baf

# Idealised victim rate in Gbps.
print(attack_gbps(2000, 5, 50))
```

This prints `500.0`.

## Key takeaways
- Reflection directs replies to a forged victim address.
- Specify which bytes a bandwidth amplification factor counts.
- The bot-rate model assumes sufficient reflector capacity and no loss.

## Further reading
- [UDP-Based Amplification Attacks — CISA](https://www.cisa.gov/news-events/alerts/2014/01/17/udp-based-amplification-attacks)
- [RFC 2827 (BCP 38): Network Ingress Filtering](https://www.rfc-editor.org/rfc/rfc2827)
- [RFC 4987: TCP SYN Flooding Attacks and Common Mitigations](https://www.rfc-editor.org/rfc/rfc4987)
- [Amplification Hell: Revisiting Network Protocols for DDoS Abuse (NDSS 2014)](https://www.ndss-symposium.org/ndss2014/programme/amplification-hell-revisiting-network-protocols-ddos-abuse/)
- [February 28th DDoS incident report — GitHub blog](https://github.blog/news-insights/company-news/ddos-incident-report/)
- [Understanding the Mirai Botnet (USENIX Security 2017)](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/antonakakis)
