---
id: ip-nat-port-mappings
title: Translate ports and expire mappings
level: intermediate
minutes: 5
sourceLesson: ip-nat-ipv6
summary: Trace a NAPT mapping in Python and distinguish mapping reuse, filtering and idle expiry.
---

IPv4 has 2³² possible address values (32 copies of 2 multiplied together), about 4.3 billion, with some reserved for special purposes. **NAT** shares or translates address space; **IPv6** provides a much larger address space. They address different aspects of connectivity and coexist in deployed networks.

## Network address translation

A **NAT** device, usually your home router or a cloud NAT gateway, sits between a private network and the Internet. It rewrites addresses in packets as they pass through, so many private hosts can share one or a few public addresses.

### Kinds of NAT

- **Static NAT**: a fixed one-to-one mapping. Private 10.0.0.5 always appears as public 198.51.100.5. Used to expose a server.
- **Dynamic NAT**: private hosts borrow a public address from a pool while they're active. Still one private address per public address at any moment.
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
        # Reuse this endpoint's mapping.
        if key not in self.out:
            if self.next_port > 65535:
                raise ValueError(
                    "ports exhausted")
            p = self.next_port
            self.next_port += 1
            self.out[key] = p
            # Save the reverse mapping.
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

Real NATs expire state. RFC 4787 requires UDP mappings to last at least two idle minutes, with a specific exception for certain well-known destination ports; it recommends a default of at least five minutes. RFC 5382 specifies at least 2 hours 4 minutes for idle established TCP connections when the NAT cannot determine whether endpoints remain active. These are protocol requirements, not measurements of every router. Keepalive choices must account for the application, state-refresh rules and actual network.

### Separate mapping reuse from inbound filtering

NATs differ in two ways that matter for peer-to-peer apps (RFC 4787 terms):

| Behaviour | Endpoint-independent | Address-and-port-dependent |
|---|---|---|
| Mapping | Reuses a mapping for the same internal endpoint across destinations | Mapping depends on the remote IP and port |
| Filtering | Anyone may send to the mapping | Only previously contacted remote IP:port pairs |

Older literature uses "full cone", "restricted cone", "port-restricted cone" and **symmetric NAT**. Those historical categories combine properties; describing mapping reuse and inbound filtering separately is clearer. Destination-dependent mapping can make a STUN-observed mapping unusable with another peer. It does not by itself prove that all direct connectivity checks will fail.

## Key takeaways
- NAPT can share a public address by translating transport ports.
- The toy translation table omits packet checksums, filtering and expiry.
- Mapping reuse and inbound filtering describe different properties.
- Idle-state requirements differ by protocol; application keepalives need the actual refresh rules.

## Further reading
- [RFC 4787: NAT Behavioral Requirements for Unicast UDP](https://www.rfc-editor.org/rfc/rfc4787)
- [RFC 8445: Interactive Connectivity Establishment (ICE)](https://www.rfc-editor.org/rfc/rfc8445)
- [RFC 8200: IPv6 Specification](https://www.rfc-editor.org/rfc/rfc8200)
- [RFC 4862: IPv6 Stateless Address Autoconfiguration](https://www.rfc-editor.org/rfc/rfc4862)
- [RFC 8305: Happy Eyeballs Version 2](https://www.rfc-editor.org/rfc/rfc8305)
- [Network address translation — Wikipedia](https://en.wikipedia.org/wiki/Network_address_translation)
- [IPv6 adoption statistics — Google](https://www.google.com/intl/en/ipv6/statistics.html)
