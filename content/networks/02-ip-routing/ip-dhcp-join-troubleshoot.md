---
id: ip-dhcp-join-troubleshoot
title: Trace joining a network end to end
level: intermediate
minutes: 5
sourceLesson: ip-dhcp
summary: Combine IPv4 configuration, IPv6 alternatives, ARP, DNS, routing and NAPT in one bounded trace.
---

Combine IPv4 configuration, IPv6 alternatives, ARP, DNS, routing and NAPT in one bounded trace.

## When there's no DHCP server

Depending on operating-system configuration, a host may self-configure an IPv4 **link-local** address (RFC 3927, called APIPA on Windows). Automatic selection uses 169.254.1.0 through 169.254.254.255, excluding the first and last /24 of 169.254.0.0/16, and probes for conflicts. Such traffic remains on the link; routers must not forward it.

> [!tip] Diagnosing with the address
> An automatically configured address in 169.254.0.0/16 can suggest missing routable IPv4 configuration, so check DHCP logs, VLANs, relays and server reachability when DHCP was expected. The address alone does not prove DHCP failed: link-local can be intentional and can coexist with other configuration.

### And IPv6?

IPv6 hosts can configure addresses with SLAAC from suitable router advertisements (see the NAT and IPv6 lesson). **DHCPv6** exists alongside it, on UDP ports 546 (client) and 547 (server), with a common four-message exchange: Solicit, Advertise, Request, Reply. Rapid Commit permits a two-message exchange, and other exchanges serve other purposes. DHCPv6 does not provide the standard default-router discovery mechanism: hosts normally learn default routers from RAs, but static routes are also possible. **Prefix delegation** can give a requesting router a prefix, such as /56 or /48; actual sizes depend on provider policy.

## Joining a network, end to end

This hypothetical IPv4 trace assumes Ethernet-like LAN/WAN links, a fresh DHCP lease, uncached DNS using the gateway resolver, a TCP connection, one NAPT gateway and ordinary IP forwarding. The public-looking addresses are documentation ranges, not live endpoints. Other networks may use different discovery, DNS, transport and forwarding mechanisms.

```
laptop          home router (NAT)
192.168.1.42 -> 192.168.1.1
                203.0.113.7 -> ISP
ISP routers (OSPF inside, BGP at edge)
  -> ... -> server 198.51.100.80
```

**1. Link up.** The Wi-Fi association completes. The laptop has a MAC but no IP.

**2. DHCP.** DORA gives it 192.168.1.42/24, gateway 192.168.1.1, DNS 192.168.1.1, 24-hour lease. It probes for conflicts with ARP and sends a gratuitous ARP. Its routing table is now a connected route for 192.168.1.0/24 and a default route via 192.168.1.1. In parallel, SLAAC may give it IPv6 addresses.

**3. ARP for the gateway.** The laptop needs 192.168.1.1's MAC, for DNS and for everything off-link. It broadcasts an ARP request and caches the reply.

**4. DNS.** It resolves the server's name by sending a UDP query to 192.168.1.1, which forwards it to the ISP's resolvers. (With Happy Eyeballs, it asks for AAAA and A records and may race IPv6 and IPv4.)

**5. Route lookup.** For 198.51.100.80, longest-prefix match finds only the default route. The SYN goes in a frame addressed to the router's MAC, with IP destination 198.51.100.80 and TTL 64.

**6. The home router.** It decrements TTL to 63, looks up the destination (its own default route, towards the ISP), and applies NAPT: source 192.168.1.42:51000 becomes 203.0.113.7:40000. It fixes the IP and TCP checksums and sends a new frame on its WAN link.

**7. Across the ISP.** Each router decrements TTL and does LPM. Inside the ISP, an IGP such as OSPF or IS-IS provides paths to the ISP's own border routers. At the border, a BGP-learnt route for the server's prefix (perhaps a /24 announced by a hosting provider) says which neighbouring AS to hand it to.

**8. The server and back.** The SYN arrives with source 203.0.113.7:40000. The SYN-ACK goes back to that address, perhaps by a different path. The home router finds the mapping, rewrites the destination to 192.168.1.42:51000 and delivers it. The TCP handshake completes.

No end-to-end timing bound follows from this trace: association, address-conflict checks, DNS and network latency all contribute. These symptoms suggest investigations rather than unique diagnoses:

| Symptom | Possible investigation |
|---|---|
| Unexpected automatic 169.254.0.0/16 address | DHCP and interface configuration |
| Reachable known IP but name resolution fails | DNS configuration and resolver path |
| LAN works, Internet doesn't | Gateway, NAT, ISP |
| Small transfers work, large transfers hang | MTU / PMTUD, loss and transport behaviour |
| Two devices interfere with each other | Check for duplicate IPs and link faults |

> [!note] Content omitted after review
> Universal setup times, operating-system fallback behaviour and provider prefix-size prevalence are omitted because this review did not establish reliable versioned evidence. The packet trace is an illustrative model, not a measured deployment.

## Key takeaways
- A link-local address can suggest missing configuration without uniquely diagnosing DHCP.
- IPv6 SLAAC and DHCPv6 complement router-advertisement default-router discovery.
- The hypothetical trace chains configured routing, NAPT and return mapping.
- Troubleshooting symptoms suggest several checks and do not establish one cause.

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
