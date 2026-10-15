---
id: ip-dhcp-discovery-dora
title: Bootstrap IPv4 with DHCP DORA
level: intermediate
minutes: 3
sourceLesson: ip-dhcp
summary: Follow initial DHCP discovery and selection, including why Requests are broadcast and addresses are probed.
---

A laptop joining a café network can obtain an IPv4 address, subnet mask, gateway and DNS settings automatically. A common mechanism is the **Dynamic Host Configuration Protocol** (DHCPv4, RFC 2131), using a protocol designed for a host that doesn't yet have an address.

This unit follows initial DHCP discovery and selection. Later units examine options, lease timers and relays before an end-to-end joining trace ties the module together.

## The chicken-and-egg problem

To ask a server for an address, you normally need an address. DHCP gets around this with two tricks:

- The client sends from source **0.0.0.0**, meaning "I don't have one yet".
- It sends to **255.255.255.255**, the limited broadcast, addressed to the local link rather than forwarded as an ordinary IP broadcast across routers. Delivery can still be filtered or lost.

DHCP runs over UDP: servers listen on **port 67**, clients on **port 68**. Fixed ports on both sides matter, because replies may be broadcast, and the client needs to recognise them.

## DORA: the four-message exchange

```
Client                       Server
  |--- DISCOVER (broadcast) --->|
  |<-- OFFER  192.168.1.42 -----|
  |--- REQUEST (broadcast) ---->|
  |<-- ACK -------------------- |
```

1. **DHCPDISCOVER** (Discover): "Is there a DHCP server? Here is my client identification." The client picks a random 32-bit **DHCP transaction ID** (`xid`) to match replies to this request.
2. **DHCPOFFER** (Offer): an eligible server may offer an address and settings, subject to pool availability and policy. Several servers might reply.
3. **DHCPREQUEST** (Request): the client picks one offer and broadcasts a Request naming that server (option 54, server identifier) and the address (option 50). Broadcasting it tells the *other* servers their offers were declined, so any temporary offer reservations can be released. A server need not reserve an offered address.
4. **DHCPACK** (Ack): the chosen server confirms. The client validates the configuration and checks for an address conflict before using it.

Before using it, the client should check nobody else already does: it sends **ARP probes** for the address (RFC 5227). A conflicting ARP announcement/reply or another host's simultaneous probe can reveal a collision. The client sends **DHCPDECLINE** and restarts after a delay (RFC 2131 recommends at least ten seconds). If all is clear, it announces itself with a **gratuitous ARP**, which can refresh peers' ARP caches; it cannot guarantee every peer updates its cache.

A server can send **DHCPNAK** when it determines that a requested configuration is invalid, such as an address on the wrong subnet. Other cases require silence rather than a NAK—for example, an unselected server hearing a Request selecting another server. A client receiving a NAK restarts configuration.

## Key takeaways
- An unconfigured client can discover servers using 0.0.0.0 and limited broadcast.
- DORA selects and confirms configuration using UDP ports 68 and 67.
- The selecting Request informs other servers which offer was accepted.
- Conflict detection can trigger DHCPDECLINE; NAK and silence apply in different server states.

## Further reading
- [RFC 2131: Dynamic Host Configuration Protocol](https://www.rfc-editor.org/rfc/rfc2131)
- [RFC 2132: DHCP Options and BOOTP Vendor Extensions](https://www.rfc-editor.org/rfc/rfc2132)
- [Dynamic Host Configuration Protocol — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_Host_Configuration_Protocol)
- [DHCP snooping — Wikipedia](https://en.wikipedia.org/wiki/DHCP_snooping)
- [RFC 5227: IPv4 Address Conflict Detection](https://www.rfc-editor.org/rfc/rfc5227)
- [RFC 9915: DHCP for IPv6 (replaces RFC 8415)](https://www.rfc-editor.org/rfc/rfc9915.html)


- [RFC 3396: long DHCPv4 options](https://www.rfc-editor.org/rfc/rfc3396)
- [RFC 3927: IPv4 link-local addressing](https://www.rfc-editor.org/rfc/rfc3927)
- [RFC 3118: DHCP authentication](https://www.rfc-editor.org/rfc/rfc3118)
