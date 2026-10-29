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

Why the expansion? A 16-bit field can encode only 65,536 values, too few for every network that needed one; 32 bits allow about 4.3 billion. The reserved values 65535 and 4294967295 are the largest number each field size can hold.

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

> [!analogy] Real-world analogy: A parcel's chain of handlers
> Imagine each courier company that handles a parcel writes its name on a handling slip before passing it on. If a company receives a parcel whose slip already shows its own name, it knows the parcel has gone round in a circle and refuses it. A shipper can also choose between offers by how many handlers each would involve.
>
> **How it maps:** Each company is an AS, the slip is the AS_PATH, refusing a parcel with your own name on it is AS-loop checking, and choosing by number of handlers is the shortest-AS_PATH preference.
>
> **Where it stops:** Nothing stops a company writing a misleading slip: an AS_PATH is an unsigned claim, and networks can deliberately repeat their own name (prepending) to look longer. The slip describes the route announcement, not proof of where packets actually travel.

## Key takeaways
- ASNs have encoded values, private ASN ranges and other reserved values.
- An AS_PATH is an advertisement, not cryptographic proof of the forwarding path.
- Normal AS-loop checking excludes routes containing the local ASN.
- BGP exchanges policy-controlled reachability between independent networks.

## Further reading
- [RFC 4271: A Border Gateway Protocol 4 (BGP-4)](https://www.rfc-editor.org/rfc/rfc4271)
- [Border Gateway Protocol — Wikipedia](https://en.wikipedia.org/wiki/Border_Gateway_Protocol)
