---
id: ip-nat-ipv6
title: NAT and IPv6
level: intermediate
minutes: 16
summary: How NAT and port translation stretch IPv4, why they break end-to-end connectivity, how STUN, TURN and ICE get around them, and how IPv6 addressing, SLAAC and dual stack work.
---

IPv4 has 2³² possible address values, about 4.3 billion, with some reserved for special purposes. **NAT** shares or translates address space; **IPv6** provides a much larger address space. They address different aspects of connectivity and coexist in deployed networks.

## Network address translation

A **NAT** device, usually your home router or a cloud NAT gateway, sits between a private network and the Internet. It rewrites addresses in packets as they pass through, so many private hosts can share one or a few public addresses.

### Kinds of NAT

- **Static NAT**: a fixed one-to-one mapping. Private 10.0.0.5 always appears as public 198.51.100.5. Used to expose a server.
- **Dynamic NAT**: private hosts borrow a public address from a pool while they're active. Still one-to-one at any moment.
- **NAPT / PAT** (port address translation, often called "NAT overload" or masquerading): many private hosts share **one** public address, distinguished by **port**. NAPT is commonly used on home gateways; product configurations differ.

### How port translation works

When a laptop at `192.168.1.10:51000` opens a connection to a web server, the router:

1. Selects a public address/port mapping, for example port 40000. Allocation and possible reuse depend on protocol and mapping policy.
2. Records a mapping in its translation table.
3. Rewrites the source to `203.0.113.7:40000`, updates the IPv4 header checksum and the TCP checksum (or a nonzero UDP checksum), and forwards. An IPv4 UDP zero checksum means no checksum was supplied and remains zero.
4. When the reply arrives for `203.0.113.7:40000`, looks up the mapping, rewrites the destination back to `192.168.1.10:51000` and forwards it inside.

```
inside              NAT        outside
192.168.1.10:51000 --+
                     | 203.0.113.7:40000
192.168.1.11:51000 --+ 203.0.113.7:40001
                     |
        table: (priv ip, port) <-> pub port
```

A toy version for one transport protocol, one public address and endpoint-independent mapping. It omits timeouts, packet/checksum processing, remote-peer filtering, port reuse and high availability:

```python
import ipaddress

class NAPT:
    def __init__(self, public_ip):
        addr = ipaddress.IPv4Address
        self.ip = str(addr(public_ip))
        self.next_port = 40000
        self.out = {}   # (ip, port) -> pub
        self.back = {}  # pub -> (ip, port)

    def outbound(self, src, sport):
        addr = ipaddress.IPv4Address
        src = str(addr(src))
        if (type(sport) is not int
                or not 1 <= sport <= 65535):
            raise ValueError("invalid port")
        key = (src, sport)
        if key not in self.out:
            if self.next_port > 65535:
                raise ValueError(
                    "ports exhausted")
            p = self.next_port
            self.next_port += 1
            self.out[key] = p
            self.back[p] = key
        return self.ip, self.out[key]

    def inbound(self, dport):
        # None means: drop the packet
        return self.back.get(dport)

nat = NAPT("203.0.113.7")
print(nat.outbound("192.168.1.10", 51000))
print(nat.outbound("192.168.1.11", 51000))
print(nat.inbound(40001))
print(nat.inbound(8080))
# ('203.0.113.7', 40000)
# ('203.0.113.7', 40001)
# ('192.168.1.11', 51000)
# None
```

The toy drops inbound packets without a mapping. Real routers may also have static mappings, an explicitly configured fallback host or locally listening services. Translation lookup and firewall policy are distinct.

Real NATs expire state. RFC 4787 requires UDP mappings to last at least two idle minutes, with a specific exception for certain well-known destination ports; it recommends a default of at least five minutes. RFC 5382 specifies at least 2 hours 4 minutes for established TCP idle state when the NAT cannot determine whether endpoints remain active. These are protocol requirements, not measurements of every router. Keepalive choices must account for the application, state-refresh rules and actual network.

### Mapping and filtering behaviour

NATs differ in two ways that matter for peer-to-peer apps (RFC 4787 terms):

| Behaviour | Endpoint-independent | Address-and-port-dependent |
|---|---|---|
| Mapping | Reuses a mapping for the same internal endpoint across destinations | Mapping depends on the remote IP and port |
| Filtering | Anyone may send to the mapping | Only previously contacted remote IP:port pairs |

Older literature uses "full cone", "restricted cone", "port-restricted cone" and **symmetric** NAT. Those historical categories combine properties; describing mapping and filtering separately is clearer. Destination-dependent mapping can make a STUN-observed mapping unusable with another peer. It does not by itself prove that all direct connectivity checks will fail.

## Why NAT breaks end-to-end connectivity

IP was designed so any host could send a packet to any other. NAT breaks that:

- **Inbound reachability needs a usable mapping and permitted traffic.** Static forwarding, mapping-control protocols, traversal or relays can provide it; a previously unused private endpoint is not automatically reachable through dynamic NAPT. Running a server, a game host or a video call at home becomes awkward.
- **Addresses in payloads break.** Protocols that carry IP addresses inside the data (FTP's active mode, SIP for VoIP) send the private address, which is useless outside. Some devices provide **ALGs** (application-level gateways) that rewrite protocol fields. Application-aware traversal and relays are alternatives; encryption or protocol differences can prevent an ALG from doing the required rewrite.
- **State in the middle.** Losing an active dynamic mapping can interrupt a connection. Replicated or recoverable state and static mappings change failure behaviour; not every NAT deployment is a single unrecoverable point of failure.
- **Carrier-grade NAT** shares public IPv4 addresses among subscribers. It can add another translation layer beyond a home NAT, and RFC 6598 provides 100.64.0.0/10 for shared internal addressing. Sharing ratios vary. IP-based bans can affect unrelated subscribers; attribution needs sufficiently detailed mapping records, including protocol, ports and time. A subscriber mapping is not proof of an individual person's identity.

> [!note] NAT is not a firewall
> Translation does not define a complete security policy. Missing mappings can prevent delivery, while filtering determines which traffic may use existing mappings. IPv6 can apply stateful firewall rules without address translation.

## NAT traversal: STUN, TURN and ICE

Video calls, WebRTC, games and VPN meshes (Tailscale, for example) want direct peer-to-peer paths. Three protocols, used together, make that work:

**STUN** (RFC 8489): a client sends a request to a public STUN server, which replies "I saw you as 203.0.113.7:40000". The client now knows its **server-reflexive** address. Endpoint-independent mapping can make that address reusable with other peers, but filtering, mapping lifetime and path reachability still determine whether traffic works.

**UDP hole punching**: both peers learn their reflexive addresses via STUN, swap them through a signalling server, then send connectivity probes towards one another. This can create mappings and filtering state that permit replies. Exact simultaneity is unnecessary, and NAT/filter behaviour can still prevent success.

**TURN** (RFC 8656): when direct connectivity checks fail, a peer can allocate a reachable **relay** address; one or both peers may use relayed candidates. It can provide connectivity when direct paths fail, but the relay must be reachable and have capacity and valid credentials. Firewalls and network failures can still block it. Relaying costs bandwidth and can add latency.

**ICE** (RFC 8445) is the procedure that ties them together:

1. **Gather candidates**: host addresses (local interfaces), server-reflexive (from STUN) and relayed (from TURN).
2. **Exchange** candidates through signalling. WebRTC can include candidates in SDP descriptions and convey additional candidates later using Trickle ICE.
3. **Connectivity checks**: try candidate pairs in priority order with STUN requests.
4. **Nominate** a valid pair under ICE priorities and application policy. A direct pair is commonly preferred, but relays can be deliberately preferred and nomination does not benchmark every path for optimal performance.

```
         signalling server
          /             \
   Peer A ---- direct? ---- Peer B
     |   (hole punched)     |
     +------ TURN relay ----+
```

## IPv6

IPv6 (RFC 8200) is the long-term fix: **128-bit** addresses, about 3.4 × 10³⁸ of them. The base header is a fixed 40 bytes with no checksum and no router fragmentation; TTL is renamed **Hop Limit**, and extras go in optional extension headers.

### Writing addresses

Eight groups of four hex digits. Two rules shorten them (RFC 5952 gives the canonical form):

1. Drop leading zeros in each group.
2. Replace the **longest** run of at least two all-zero groups with `::`, once only (if runs tie, the first). RFC 5952 canonical output does not compress a single zero group.

```
2001:0db8:0000:0000:0000:ff00:0042:8329
2001:db8::ff00:42:8329

2001:db8:0:0:1:0:0:1
2001:db8::1:0:0:1
```

### Address types

| Prefix | Type |
|---|---|
| 2000::/3 | Main global-unicast allocation block, including special-use subranges |
| fe80::/10 | Link-local |
| fc00::/7 | Unique local (ULA) |
| ff00::/8 | Multicast |
| ::1/128 | Loopback |

There is no broadcast; multicast groups like `ff02::1` (all nodes on the link) replace it. IPv6 addressing specifies a **link-local** address on each interface, apart from exceptions such as the loopback interface. An interface need not have a global address; multiple addresses are supported. `2001:db8::/32` in these examples is documentation space, not a publicly routed allocation. ULA local generation uses `fd00::/8`; the `fc00::/8` half is not defined for that method.

### The /64 convention

A global address is typically split 64/64: a **prefix** (routing) and an **interface identifier** (the host). Ethernet SLAAC uses **/64** prefixes. Other uses include /127 point-to-point router links and /128 host routes, so IPv6 routing is not limited to /64. Delegation sizes vary; a /56 contains 256 /64s and a /48 contains 65,536.

### SLAAC: configuring without a server

**Stateless address autoconfiguration** (RFC 4862) lets a host configure itself:

1. Form a **link-local** address: `fe80::` + an interface identifier.
2. Run **duplicate address detection** (DAD): probe the tentative address with Neighbor Solicitation. A conflicting Advertisement or another host's DAD Solicitation can reveal a duplicate; absence of a reply is not an absolute uniqueness guarantee.
3. Send a **Router Solicitation** to `ff02::2` (all routers).
4. A **Router Advertisement** may carry prefix information and flags. A usable autonomous prefix must have its A flag set and suitable length/lifetimes. The RA source becomes a default-router candidate only with a nonzero router lifetime; an RA need not advertise a prefix or a default route.
5. The host can form an address from an eligible prefix and interface identifier, then perform DAD. Working routing, neighbour resolution and other configuration are still needed for external connectivity.

One historical interface-identifier method derives it from the MAC (**modified EUI-64**): split the MAC, insert `ff:fe`, and XOR the first byte with `0x02` (the U/L bit). `00:1a:2b:3c:4d:5e` becomes `021a:2bff:fe3c:4d5e`. That leaks a stable hardware ID everywhere you go, so alternatives include opaque, prefix-dependent **stable** identifiers (RFC 7217) and changing **temporary** addresses (RFC 8981). Which method is enabled depends on the system and configuration; stable identifiers are not freshly randomised for every connection.

RA flags say whether to also use **DHCPv6**: M (managed: get addresses from DHCPv6) and O (other: get options such as DNS from DHCPv6). DNS servers can also be sent in the RA itself (RDNSS). Support for DHCPv6 modes varies across client versions. M/O flags do not force a client to implement a mode, and SLAAC prefix processing is controlled separately by the prefix A flag.

### Dual stack and transition

The two protocols aren't wire-compatible: an IPv6-only host can't talk to an IPv4-only host directly. The migration uses:

- **Dual stack**: hosts and networks run both protocol families.
- **Happy Eyeballs** (RFC 8305): clients resolve and order addresses, then stagger connection attempts across candidates instead of waiting for a failed family's full timeout. The recommended default connection-attempt delay is 250 ms, but implementations can adapt it; DNS timing, address ordering and path RTT affect the result. It is not a universal 250 ms page-load guarantee.
- **NAT64 + DNS64** (RFC 6146/6147): a translator can connect IPv6-only clients to IPv4 servers. DNS64 can synthesise AAAA records using a configured translation prefix; `64:ff9b::/96` is the well-known prefix, not the only option. 464XLAT adds client-side translation for IPv4-dependent applications. Reachability and application compatibility still depend on the deployment.

- **Tunnels** (6in4 and others) carry IPv6 over IPv4 links where native IPv6 isn't available.

> [!note] Content omitted after review
> Current IPv6 adoption percentages, client-platform DHCPv6 support, app-store requirements and consumer NAT timeout surveys are omitted because they need versioned or dated evidence not established here. The linked standards define behaviour, not deployment prevalence.

> [!warning] Common IPv6 pitfalls
> - Review IPv6 firewall policy separately: IPv4-only rules do not establish what the IPv6 policy permits or blocks.
> - Blanket ICMPv6 filtering can break neighbour discovery, router advertisements and MTU feedback. Cached/static configuration or probing may mask some failures; ICMPv6 message types need deliberate treatment.
> - Code that stores IPs in 32-bit integers or splits on `:` for ports (`[2001:db8::1]:443` needs brackets).

## Key takeaways
- NAPT lets private hosts share a public address by translating ports. The toy model drops arrivals without mappings; real devices can also have local services and configured inbound rules.
- NAT breaks end-to-end reachability, payload addresses and IP-based identity; CGNAT makes it worse.
- STUN discovers your public mapping, hole punching can establish a direct path, TURN relays when that fails, and ICE orchestrates the lot.
- IPv6 uses 128-bit addresses and no broadcast. /64 is standard for Ethernet SLAAC, while other prefix lengths serve other purposes.
- SLAAC builds addresses from router advertisements; opaque and temporary identifiers can avoid exposing MAC-derived identifiers.
- Transition relies on dual stack with Happy Eyeballs, and NAT64/DNS64 for IPv6-only networks.

## Further reading
- [RFC 4787: NAT Behavioral Requirements for Unicast UDP](https://www.rfc-editor.org/rfc/rfc4787)
- [RFC 8445: Interactive Connectivity Establishment (ICE)](https://www.rfc-editor.org/rfc/rfc8445)
- [RFC 8200: IPv6 Specification](https://www.rfc-editor.org/rfc/rfc8200)
- [RFC 4862: IPv6 Stateless Address Autoconfiguration](https://www.rfc-editor.org/rfc/rfc4862)
- [RFC 8305: Happy Eyeballs Version 2](https://www.rfc-editor.org/rfc/rfc8305)
- [Network address translation — Wikipedia](https://en.wikipedia.org/wiki/Network_address_translation)
- [IPv6 adoption statistics — Google](https://www.google.com/intl/en/ipv6/statistics.html)
