---
id: ip-nat-port-mappings
title: Translate ports and expire mappings
level: intermediate
minutes: 4
sourceLesson: ip-nat-ipv6
summary: Trace a NAPT translation table and distinguish mapping reuse, filtering and idle expiry.
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

The heart of NAPT is its translation table. After the two laptops above open connections, a simplified table for one protocol and one public address looks like this:

| Inside endpoint | Public endpoint |
|---|---|
| 192.168.1.10:51000 | 203.0.113.7:40000 |
| 192.168.1.11:51000 | 203.0.113.7:40001 |

Both laptops happen to use source port 51000, so the router gives them different public ports to tell their replies apart. A reply to 203.0.113.7:40001 matches the second row and goes to 192.168.1.11. An unsolicited packet to 203.0.113.7:8080 matches no row, so in this simple model it is dropped: there is nobody inside to send it to.

Real routers can add rows deliberately, with static mappings (port forwarding), a configured fallback host or services listening on the router itself. Translation lookup and firewall policy are distinct functions.

> [!analogy] Real-world analogy: An office switchboard
> An office has one public phone number. When a member of staff makes an outside call, the receptionist notes "line 40000 is extension 10's call" so that when the other party rings back on that line, the call is put through to the right desk. An unexpected call on a line nobody has used gets no answer.
>
> **How it maps:** The public number is the shared public IP address, the lines are public ports, the extensions are private addresses and ports, and the receptionist's notebook is the translation table. Entries made by outgoing calls are dynamic mappings; a standing instruction to put all calls on one line through to the sales desk is a static port forward.
>
> **Where it stops:** A receptionist does not rewrite anything, whereas a NAT changes addresses, ports and checksums in every packet. NAT entries also expire after idle periods, and some NATs accept a return call only from the exact party that was called, which is a filtering rule rather than part of the mapping.

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
- An inbound packet with no matching mapping has no inside destination unless a static rule exists.
- Mapping reuse and inbound filtering describe different properties.
- Idle-state requirements differ by protocol; application keepalives need the actual refresh rules.

## Further reading
- [RFC 4787: NAT Behavioral Requirements for Unicast UDP](https://www.rfc-editor.org/rfc/rfc4787)
- [RFC 5382: NAT Behavioral Requirements for TCP](https://www.rfc-editor.org/rfc/rfc5382)
- [Network address translation — Wikipedia](https://en.wikipedia.org/wiki/Network_address_translation)
