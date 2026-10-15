---
id: ip-bgp-as-paths
title: Autonomous systems and AS paths
level: advanced
minutes: 3
sourceLesson: ip-bgp
summary: Identify an autonomous system and interpret the reachability and loop-checking role of AS_PATH.
---

OSPF computes paths within a routing domain using configured costs; that does not make its routers inherently trustworthy. Internet inter-domain routing must also accommodate independent networks, many of them competitors, with different policies. They need to exchange reachability without revealing their insides or giving up control.

That protocol is the **Border Gateway Protocol**, BGP-4 (RFC 4271). It's often called the glue of the Internet, and it runs on trust to a degree that surprises people.

## Autonomous systems

An **autonomous system** (AS) is a network under one administrative policy: an ISP, a cloud provider, a university, a large company. Public ASNs are allocated through Internet number registries; private ASNs can be used in appropriate private routing contexts.

- ASN fields expanded from 16 to 32 bits (RFC 6793). Not every encodable value is assignable: 65535 and 4294967295, for example, are reserved.
- Private ASN ranges exist for internal use: 64512–65534 and 4200000000–4294967294.
- AS numbers in the examples below illustrate routing policy; they are not instructions to announce those routes publicly.

Here is why 16 bits ran short, and where the reserved numbers originate:

```formula
N_16 = 2^16 = 65,536
N_32 = 2^32 = 4,294,967,296
where
N_16: the number of values a 16-bit ASN field can encode, from 0 to 65,535
N_32: the number of values a 32-bit ASN field can encode, from 0 to 4,294,967,295
2^16, 2^32: 16 or 32 copies of 2 multiplied together
In words: 16 bits allow only about 65 thousand AS numbers, too few for every network on the Internet; 32 bits allow about 4.3 billion. The reserved values 65535 and 4294967295 are the largest number each field size can hold.
```

An AS can use an IGP such as OSPF or IS-IS internally, alongside internal BGP. eBGP exchanges routes between ASes; designs can also use eBGP inside one organisation.

## A path-vector protocol

BGP is a **path-vector** protocol. Like distance vector, routers tell neighbours what they can reach. But instead of a distance, an ordinary **AS_PATH** sequence records advertised AS traversal, with repeated entries possible for prepending. It is not cryptographic proof of the actual forwarding path. For example:

```
203.0.113.0/24
  AS_PATH: 3356 1299 65010
            ^         ^
         neighbour   origin
```

That list does two jobs:

- **Loop prevention**: normal AS-loop checking excludes a received route containing the local ASN. Explicit configuration exceptions exist; this mechanism does not eliminate every possible forwarding loop or policy oscillation.
- **Policy**: operators can filter or rank the advertised path, subject to the limits of trusting that advertisement.

## Key takeaways
- ASNs have encoded values, private ASN ranges and other reserved values.
- An AS_PATH is an advertisement, not cryptographic proof of the forwarding path.
- Normal AS-loop checking excludes routes containing the local ASN.
- BGP exchanges policy-controlled reachability between independent networks.

## Further reading
- [RFC 4271: A Border Gateway Protocol 4 (BGP-4)](https://www.rfc-editor.org/rfc/rfc4271)
- [Border Gateway Protocol — Wikipedia](https://en.wikipedia.org/wiki/Border_Gateway_Protocol)
- [Understanding how Facebook disappeared from the Internet — Cloudflare blog](https://blog.cloudflare.com/october-2021-facebook-outage/)
- [How Verizon and a BGP Optimizer Knocked Large Parts of the Internet Offline — Cloudflare blog](https://blog.cloudflare.com/how-verizon-and-a-bgp-optimizer-knocked-large-parts-of-the-internet-offline-today/)
- [RFC 6811: BGP Prefix Origin Validation](https://www.rfc-editor.org/rfc/rfc6811)
- [BGP hijacking — Wikipedia](https://en.wikipedia.org/wiki/BGP_hijacking)
- [MANRS](https://www.manrs.org/)

- [RIPE NCC: YouTube hijacking presentation and timeline](https://ripe56.ripe.net/presentations/Refice-YouTube_Prefix_Hijacking.pdf)
- [Meta: October 2021 outage details](https://engineering.fb.com/2021/10/05/networking-traffic/outage-details/)
- [Cloudflare: BGP leaks and cryptocurrencies](https://blog.cloudflare.com/bgp-leaks-and-crypto-currencies/)
- [Cisco: BGP best-path algorithm](https://www.cisco.com/c/en/us/support/docs/ip/border-gateway-protocol-bgp/13753-25.html)
- [IETF: ASPA verification draft](https://datatracker.ietf.org/doc/draft-ietf-sidrops-aspa-verification/)
- [RFC 9319: RPKI maxLength](https://www.rfc-editor.org/rfc/rfc9319)
