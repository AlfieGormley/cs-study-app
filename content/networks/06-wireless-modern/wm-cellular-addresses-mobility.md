---
id: wm-cellular-addresses-mobility
title: Mobile addressing, translation and path changes
level: intermediate
minutes: 3
summary: Shared public addresses complicate rate limiting and inbound reachability.
sourceLesson: wm-cellular
---

This unit focuses on mobile addressing, translation and path changes. It builds on the earlier units in this module; the examples below state their additional assumptions.

## Addresses, NAT and IPv6

**Carrier-grade NAT** (CGNAT) lets an operator share public IPv4 addresses among many subscribers. The number sharing one address and availability of public addressing vary. Possible consequences:

- Unsolicited inbound IPv4 connections are commonly restricted without suitable mappings/policies. Peer-to-peer applications can use ICE with STUN and, when needed, TURN relays; STUN itself is not a relay.
- NAT mappings expire after a period of idleness, according to protocol and operator policy. Long-lived idle TCP connections can silently die, which is one more reason to use the platform push service.
- Rate-limiting by public IP can group unrelated subscribers; combine appropriate account/token and abuse controls rather than treating an address as one person.

Operators can provide **IPv6-only** access with NAT64/DNS64 or **464XLAT** to reach IPv4 services. 464XLAT combines client-side stateless translation with network-side stateful translation. Apple’s IPv6-only compatibility guidance recommends hostnames and system APIs; some system APIs can synthesise an IPv6 destination even from an IPv4 literal. Raw IPv4-only socket code without translation/synthesis is a different case.

## Mobility between networks

If an application loses its cellular path and must use an independently addressed Wi-Fi path, ordinary TCP cannot simply change its endpoint tuple. Joining Wi-Fi alone does not necessarily close every existing cellular connection.

Ways to cope:

- **Retry idempotent requests** and make uploads resumable.
- **QUIC** identifies connections by a connection ID rather than the 4-tuple, so eligible client migration can preserve a confirmed connection when permitted and the new path works; validation and other conditions still apply.
- **Multipath TCP** can carry one connection over multiple subflows, for example Wi-Fi and cellular, when endpoints and policies support it. It improves mobility options without guaranteeing uninterrupted service.
- Use the OS's path monitoring (`NWPathMonitor` on iOS, `ConnectivityManager` on Android) to react to changes. Apple reports an **expensive network path** separately from a **constrained network path** (for example Low Data Mode). Android exposes its own meteredness and capability information. Use the relevant platform signals rather than reducing every policy decision to cellular versus Wi-Fi before downloading large media.

## Key takeaways
- Shared public addresses complicate rate limiting and inbound reachability.
- NAT64/DNS64 and 464XLAT solve different compatibility cases.
- Resumption, QUIC migration and MPTCP have prerequisites; a path change is not automatically seamless.

## Further reading
- [Mobile Networks — High Performance Browser Networking](https://hpbn.co/mobile-networks/)
- [Optimizing for Mobile Networks — High Performance Browser Networking](https://hpbn.co/optimizing-for-mobile-networks/)
- [464XLAT — Wikipedia](https://en.wikipedia.org/wiki/464XLAT)
- [Supporting IPv6-only networks — Apple Developer](https://developer.apple.com/support/ipv6/)
- [RFC 6877: 464XLAT](https://www.rfc-editor.org/rfc/rfc6877)
