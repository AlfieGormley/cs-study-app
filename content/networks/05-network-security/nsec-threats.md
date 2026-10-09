---
id: nsec-threats
title: Threats on the network
level: basic
minutes: 13
summary: Eavesdropping, spoofing, man-in-the-middle, replay and denial of service, including how amplification attacks multiply an attacker's bandwidth and how to calculate by how much.
---

Basic IPv4, ARP, UDP and traditional DNS do not by themselves cryptographically authenticate every sender or encrypt application data. Checksums detect some accidental corruption, but do not prove identity. Security extensions and deployment controls can add protections.

Missing authentication and encryption enable several important network attacks. This lesson sorts those attacks into five families. For each one, ask two questions: **what security property does it break**, and **what is the standard defence**?

The classic properties are often summarised as **CIA**:

| Property | Meaning | Broken by |
|---|---|---|
| Confidentiality | Only the intended party reads it | Eavesdropping |
| Integrity | Nobody alters it undetected | MITM, injection |
| Authenticity | It came from who it claims | Spoofing, replay |
| Availability | The service stays up | DoS / DDoS |

(Strictly, CIA is confidentiality, integrity and availability; authenticity is usually grouped with integrity. It is listed separately here because so many network attacks target it.)

## Eavesdropping

**Eavesdropping** (passive sniffing) means reading traffic you were not meant to see. The attacker changes nothing, which makes it very hard to detect.

Where can an attacker listen?

- **Shared media.** Wi-Fi is radio: a nearby receiver may capture frames on a monitored channel, subject to signal, interference and radio capabilities. An Ethernet repeater hub repeated received signals onto its other ports, subject to physical-layer error and collision handling.
- **Switched LANs.** A switch normally forwards known unicasts toward the learned destination port, while broadcasts and some unknown traffic are flooded. MAC-table exhaustion or ARP poisoning may expose additional traffic, depending on switch protections and topology.
- **On the path.** Any ISP, transit provider, café router or compromised router between you and the server sees your packets.

Even when the payload is encrypted, **metadata** leaks: source and destination addresses, packet sizes, timing, and often the server's hostname (in DNS queries and the TLS SNI field, see lesson 3).

The defence is **encryption in transit**: TLS for application traffic, VPNs for whole networks, WPA2/WPA3 for Wi-Fi. The maths behind the ciphers is covered in the Security & Cryptography subject; here we care about where encryption sits and what it leaves exposed.

## Spoofing

**Spoofing** means forging an identifier. Many packet fields can be written by a sender. Whether a forgery is accepted depends on filtering, cryptographic validation and protocol state.

| What is forged | How | Classic use |
|---|---|---|
| Source IP | Write any value in the header | Reflection DDoS |
| MAC address | Change the NIC setting | Bypass MAC filters |
| ARP reply | Send unsolicited replies | LAN MITM |
| DNS answer | Race the real reply | Redirect a domain |
| Email sender | Set the From header | Phishing |

**IP spoofing** has a catch for the attacker: replies go to the forged address, not to them. So it is mostly useful for one-way attacks where the attacker does not need the answer. That is exactly what reflection attacks need (below).

An off-path attacker who cannot observe replies has an additional obstacle when forging a TCP handshake: the acknowledgment must match the server's initial sequence number plus one in the ordinary no-data handshake. Unpredictable sequence-number generation makes blind guessing harder.

> [!tip] BCP 38: stop spoofing at the source
> RFC 2827 (BCP 38) recommends filtering customer traffic against permitted source prefixes. This blocks spoofing outside those prefixes, but does not by itself stop one host impersonating another inside an allowed prefix. More granular source validation and reflector controls are also useful.

## Man-in-the-middle

A **man-in-the-middle (MITM)** attacker sits between two parties, relaying and possibly altering traffic while each side believes it is talking directly to the other. An unmitigated MITM can threaten confidentiality, integrity and authentication; correctly authenticated encryption can prevent reading or modifying protected content even when traffic is relayed.

```
 Normal:
 Alice ------------------------> Bank

 MITM:
 Alice ----> Mallory ----> Bank
   "I am the Bank"  "I am Alice"
```

Ways to get in the middle:

- **ARP spoofing** on a LAN: tell the victim "the gateway's IP is at my MAC address".
- **Rogue Wi-Fi access points** ("evil twins", lesson 5).
- **DNS spoofing**: make the domain resolve to the attacker's IP.
- **BGP hijacking**: an unauthorised announcement may redirect traffic in networks that accept and select it.

Encryption alone does not stop MITM. If Alice does a key exchange with Mallory, she has a perfectly encrypted channel to the attacker. What stops MITM is **authentication**: Alice must verify she is talking to the real bank. In TLS that is the certificate check (lesson 3). This is why clicking through a certificate warning is so dangerous.

## Replay

In a **replay attack** the attacker captures a valid message and sends it again later. They do not need to read or change it.

> [!example] A replayed payment
> A client sends an encrypted, signed message: "pay merchant £50". The attacker cannot read it, but captures it and sends it ten more times. If the server only checks the signature, it pays out £550.

The signature is valid every time, because it is the same message. The defence is to make each message usable **once**:

- **Nonces**: include a unique value in the authenticated request; atomically reject reuse in the relevant session or account.
- **Timestamps**: an authenticated timestamp can limit the acceptance window, but a replay inside that window still needs duplicate detection. Clock and expiry rules must be defined.
- **Sequence numbers**: authenticate counters and track accepted values. An ordered channel can require the next counter; an IPsec-style sliding window can accept unseen out-of-order packets while rejecting duplicates and packets that are too old. TLS early data has separate replay caveats (lesson 3).

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

**Slowloris** is the low-and-slow variant: open many HTTP connections and send headers one byte at a time, never finishing. Thread-per-connection servers (classic Apache) run out of workers. Defences include rate limiting, CAPTCHAs or challenges, caching, and event-driven servers or reverse proxies with short header timeouts.

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

For example, a 40-byte request that triggers a 1,400-byte response has a BAF of 1,400 / 40 = 35. The ratio depends on which bytes you count (payload only, or headers too; see below) and on the particular query and server, so published figures are measurements, not constants.

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
R_send = N_bots × r_bot
R_victim = R_send × BAF
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
    sent = bots * mbps_each / 1000  # Gbps
    return sent * baf

print(attack_gbps(2000, 5, 50))
```

This prints `500.0`.

Two subtleties:

**Headers dilute the factor in this unfragmented example.** A UDP datagram carried in one IPv4 packet with no options has 28 bytes of IP and UDP headers (20 for IPv4, 8 for UDP); link-layer overhead is additional. For a 40-byte request and 1,400-byte response, the payload BAF is 35, but counting the IP and UDP headers too gives a lower ratio:

```formula
BAF_IP = (B_resp + H) / (B_req + H)
BAF_IP = (1400 + 28) / (40 + 28)
BAF_IP = 1428 / 68 = 21
where
BAF_IP: the amplification factor counting IP and UDP headers as well as payload, a plain ratio
B_resp: the response payload, in bytes; here 1,400
B_req: the request payload, in bytes; here 40
H: the IPv4 header (20 bytes) plus the UDP header (8 bytes), 28 bytes per packet
In words: adding the same 28 header bytes to both sides shrinks the ratio, and shrinks it most when the request is small: 35 on payload alone becomes 21 at the IP level.
```

A full link-level ratio also needs link-layer framing and packetisation, which dilute it further.

**Packet amplification** matters too. One request producing many response packets multiplies the packets per second, which stresses routers and firewalls as well as links.

### Defending against amplification

- **Do not be a reflector**: close open resolvers, disable NTP `monlist`, never expose memcached (UDP 11211) to the internet. Memcached disabled UDP by default from version 1.5.6 after the 2018 attacks.
- **BCP 38** ingress filtering at ISPs, so spoofed packets never leave the attacker's network.
- **Protocol design**: cap amplification before validating a peer's address. QUIC permits up to three times the received UDP payload bytes before address validation; this bounds amplification rather than eliminating it.
- **Upstream scrubbing and anycast** to spread and absorb the flood.

> [!note] Content omitted after review
> Universal attack-success rates, firewall mistake rankings and provider capacity guarantees are absent: this review has no representative measurement supporting those claims. Historical amplification figures above retain their original measurement scope.

## Key takeaways
- Basic packet identifiers are not cryptographic identities; validation and deployment controls determine which forgeries are accepted.
- Encryption protects confidentiality, but only authentication stops a man-in-the-middle.
- Replay protection needs authenticated freshness data and correct receiver state. A timestamp alone only limits the replay window.
- DDoS attacks target bandwidth (volumetric), state (protocol) or expensive work (application), and each needs a different defence.
- Amplification multiplies attacker bandwidth by the BAF; spoofed UDP plus a large response is the recipe, and source validation plus reflector controls reduce the available attack paths.

## Further reading
- [UDP-Based Amplification Attacks — CISA](https://www.cisa.gov/news-events/alerts/2014/01/17/udp-based-amplification-attacks)
- [RFC 2827 (BCP 38): Network Ingress Filtering](https://www.rfc-editor.org/rfc/rfc2827)
- [RFC 4987: TCP SYN Flooding Attacks and Common Mitigations](https://www.rfc-editor.org/rfc/rfc4987)
- [Amplification Hell: Revisiting Network Protocols for DDoS Abuse (NDSS 2014)](https://www.ndss-symposium.org/ndss2014/programme/amplification-hell-revisiting-network-protocols-ddos-abuse/)
- [February 28th DDoS incident report — GitHub blog](https://github.blog/news-insights/company-news/ddos-incident-report/)
- [Understanding the Mirai Botnet (USENIX Security 2017)](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/antonakakis)
