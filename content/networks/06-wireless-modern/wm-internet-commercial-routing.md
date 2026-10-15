---
id: wm-internet-commercial-routing
title: Autonomous systems and commercial routing policy
level: advanced
minutes: 4
summary: BGP carries policy-controlled reachability; AS-path length is not latency.
sourceLesson: wm-internet-structure
---

"The Internet" is not one network. It comprises independently administered networks exchanging traffic under their routing policies, connected by physical cables under streets and oceans, by switches in shared buildings, and increasingly by satellites.

To reason about latency, outages, costs and why your packets take the route they do, you need the physical and the commercial picture together: who connects to whom, why, over what, and how fast light can get there.

## Autonomous systems and BGP

The unit of the Internet is the **autonomous system** (AS): a network under one administration with its own routing policy, identified by an AS number. An organisation may operate one AS, several ASes, or use another organisation’s routing. Observed AS/prefix counts depend on date, collector and filtering; no undated count is used here.

ASes exchange reachability with **BGP** (Border Gateway Protocol). BGP announcements carry reachability attributes, including **AS_PATH** information. They can be incorrect or manipulated, and AS-path prepending means the attribute is not a simple record of physical routers. BGP chooses routes by **policy** first (business relationships, configured preferences) and only then by things like AS path length. It does not measure latency or bandwidth.

## Transit, peering and the tiers

Two kinds of business relationship connect ASes:

- **Transit**: a customer pays a provider to provide broad Internet reachability according to the service agreement. A full table or default route may be supplied; policy, filtering, partial-transit products and outages qualify “every destination”.
- **Peering**: two networks exchange traffic *between their own networks and customers only*, under agreed policy. **Settlement-free** peering has no traffic-exchange payment between the peers, while ports, circuits and colocation still cost money. Paid peering also exists; equal benefit is not guaranteed.

This creates a loose hierarchy:

```
   [Tier 1] ==peer== [Tier 1]
      |                  |
   transit            transit
      |                  |
   [Tier 2] ==peer== [Tier 2]
      |                  |
   [access ISP]     [content]
```

- **Tier 1** networks can reach every destination without paying anyone for transit: they peer with all other Tier 1s and have their own customers. This is a commercial/topological classification, not an IETF-certified membership list or proof of uninterrupted reachability.
- **Tier 2** networks peer widely but still buy some transit.
- **Tier 3** or stub networks buy transit and do little peering.

## Routing follows the money

A common economic routing model prefers customer routes over peer/provider routes and restricts export. Some operators further prefer peers over providers, but this is policy rather than a BGP requirement. In the simplified export model:

| Learned from | Exported to |
|---|---|
| Customer | everyone |
| Peer | customers only |
| Provider | customers only |

Under these model assumptions, networks do not offer transit between peers/providers. This produces **valley-free** paths: up through providers, at most one peering link across, then down through customers. Real agreements and traffic engineering can deviate from the model. Policy-selected paths need not minimise distance or latency.

> [!warning] Route leaks and hijacks
> BGP trusts announcements by default. In 2008 Pakistan Telecom announced a more specific prefix for YouTube, intended for local blocking; it leaked to its upstream and took YouTube offline for much of the world for hours. In 2019 a small network leaked routes it had learned from one provider to its other provider, Verizon, which accepted them, and significant traffic for Cloudflare and others was drawn through a tiny network. **RPKI route origin validation** checks prefix/origin authorisation against validated ROA information; it does not authenticate the whole AS path or detect every route leak. Local rejection policy, customer prefix filters, relationship-aware controls and monitoring provide complementary defences.

## Forwarding chooses the longest installed prefix

BGP route selection and destination lookup are separate steps. After routes have been accepted and installed, ordinary IP forwarding chooses the most specific matching destination prefix. For example, an installed route for `192.0.2.0/24` is preferred for a destination in that range over a covering `192.0.0.0/22`, even if the larger block has a shorter AS-path attribute. Prefix and origin filtering determine whether the advertisement is accepted in the first place.

The addresses here are a hypothetical routing example, not an instruction to announce address space.

## Key takeaways
- BGP carries policy-controlled reachability; AS-path length is not latency.
- Commercial export models produce valley-free paths under their assumptions.
- Origin validation checks authorised origins, not the whole AS path.

## Further reading
- [Autonomous system (Internet) — Wikipedia](https://en.wikipedia.org/wiki/Autonomous_system_(Internet))
- [Tier 1 network — Wikipedia](https://en.wikipedia.org/wiki/Tier_1_network)
- [Peering — Wikipedia](https://en.wikipedia.org/wiki/Peering)
- [Gao and Rexford: Stable Internet Routing Without Global Coordination](https://www.cs.princeton.edu/courses/archive/fall14/cos561/papers/StableBGP01.pdf)
- [RFC 4271: BGP](https://www.rfc-editor.org/rfc/rfc4271)
