---
id: tcp-udp-operational-risks
sourceLesson: tcp-udp-ports
title: Congestion, reflection and UDP deployment
level: basic
minutes: 3
summary: The duties UDP leaves to the application: congestion control, reflection attacks, NAT timeouts and fragmentation.
---

## Pitfalls of UDP

- **You own congestion control.** UDP will happily send faster than the network can carry, hurting everyone. [RFC 8085](https://www.rfc-editor.org/rfc/rfc8085) requires applications to account for congestion and describes suitable control or rate-limiting behaviour for different traffic patterns; low-volume applications are not universally exempt.
- **Amplification attacks.** With no handshake, an attacker can spoof a victim's source address and send small queries to open servers that reply with much bigger responses. Cloudflare documented large amplification from exposed Memcached UDP services in 2018. Amplification depends on the request, stored response and counting of protocol overhead; the attack does not follow merely from choosing UDP.
- **NAT and firewalls.** Idle mapping lifetimes vary. RFC 4787 specifies a normal minimum of two minutes, with a defined exception for some well-known destination ports; actual equipment may differ. Applications needing inbound reachability must account for the relevant timeout and keepalive policy. Some corporate networks block UDP outright, so clients supporting HTTP/2 or HTTP/1.1 can fall back to TCP; a QUIC-only application has no automatic TCP fallback.
- **Fragmentation.** Oversized datagrams may fail locally or require permitted fragmentation. Fragment loss or filtering can prevent reassembly; UDP does not retransmit the missing data.

> [!analogy] Real-world analogy: Catalogue requests in someone else's name
> A prankster fills in hundreds of free postcards asking companies to post a heavy catalogue, writing a neighbour's address as the sender's address. Each postcard is light, but the neighbour's doormat is buried under catalogues.
>
> **How it maps:** The postcards are small spoofed UDP queries; the companies are open servers that reply without checking who asked; the catalogues are much larger responses, all delivered to the victim whose address was forged. The size ratio is the amplification factor.
>
> **Where it stops:** Network traffic arrives in seconds rather than days, and many networks can filter forged source addresses before they leave. Some UDP-based protocols also limit replies to an address they have not validated; QUIC, for example, caps a server at three times the bytes it has received until the client's address is validated.

## Key takeaways

- UDP applications must account for congestion; choosing datagrams does not remove network responsibility.
- Spoofed requests and large open-server replies can create reflection amplification.
- Mapping lifetimes, fragmentation and UDP reachability vary across paths and deployments.

## Further reading

- [RFC 8085: UDP Usage Guidelines](https://www.rfc-editor.org/rfc/rfc8085)
- [Memcrashed: amplification attacks from port 11211 — Cloudflare blog](https://blog.cloudflare.com/memcrashed-major-amplification-attacks-from-port-11211/)
- [User Datagram Protocol — Wikipedia](https://en.wikipedia.org/wiki/User_Datagram_Protocol)
