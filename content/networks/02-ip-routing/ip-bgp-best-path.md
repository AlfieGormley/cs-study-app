---
id: ip-bgp-best-path
title: Choose a BGP path by policy
level: advanced
minutes: 3
sourceLesson: ip-bgp
summary: Predict which BGP route wins using local preference and a common selection order, while recognising vendor-specific rules.
---

When a router hears several routes to the same prefix, BGP does not simply pick the shortest. It walks an ordered list of tie-breakers, and the first difference decides.

## Path attributes and best-path selection

Each route carries **path attributes**:

- **AS_PATH**: the advertised AS traversal, possibly including prepending.
- **NEXT_HOP**: where to send the traffic.
- **LOCAL_PREF**: a preference set *inside* your AS and shared over iBGP. Higher wins.
- **MED** (multi-exit discriminator): a hint from a neighbour about which of several links into it you should use. Lower wins.
- **BGP communities**: tags like `65010:100` that carry meaning by agreement, such as "don't announce this to peers" or "prepend twice towards Europe".

Among eligible routes for the same prefix, a common Cisco-style sequence is below. Reachability checks, vendor-specific steps (including Cisco weight before LOCAL_PREF), configuration and multipath settings matter; this is not a universal BGP ordering:

1. Highest **LOCAL_PREF**.
2. Prefer routes originated locally.
3. Shortest **AS_PATH**.
4. Lowest **origin attribute** (IGP, then EGP, then incomplete). These are attribute codes, not proof that the route was learned through an IGP.
5. Lowest **MED** (normally only between routes from the same neighbouring AS).
6. **eBGP** over iBGP.
7. Lowest IGP cost to the NEXT_HOP ("hot potato").
8. Further implementation-dependent tie-breakers, including route age in some eBGP cases and router IDs.

The key habit is to walk the list in order and stop at the first step where the routes differ. A later step, however lopsided, is never consulted.

> [!example] A worked choice
> Your AS hears 203.0.113.0/24 three ways:
> - From a transit provider: LOCAL_PREF 100, path `64500 3356 65010` (3 ASes).
> - From a peer: LOCAL_PREF 200, path `64600 64700 65010` (3 ASes).
> - From customer 65010 directly: LOCAL_PREF 300, path `65010 65010 65010` (prepended to 3).
>
> With all eligibility checks passed and earlier vendor-specific preferences equal, LOCAL_PREF decides: the customer route wins at 300. The customer's prepending was meant to push traffic away, but it only affects step 3, which is never reached.

> [!analogy] Real-world analogy: Preferred suppliers
> A buyer's company policy says "use our preferred suppliers first; only if two are equally preferred, pick the one with fewer middlemen". A supplier who pads its quote with extra middlemen to discourage orders is still chosen if it is the preferred one.
>
> **How it maps:** The preferred-supplier ranking is LOCAL_PREF, set inside your own AS; the number of middlemen is AS_PATH length; padding the quote is AS_PATH prepending. Because policy is checked first, the padding only matters between equally preferred options.
>
> **Where it stops:** Real buyers might also weigh price or delivery time on the spot. Base BGP does not measure performance at all, and each router applies a fixed, vendor-defined order rather than judgement.

Note what's missing: bandwidth, latency, congestion. BGP picks paths by **policy** and AS count, not performance. The shortest AS_PATH may cross an ocean twice.

## Key takeaways
- Higher LOCAL_PREF can decide before AS_PATH length.
- Origin and MED have specific meanings and comparison conditions.
- Walk the selection order and stop at the first difference; later steps never override earlier ones.
- BGP path policy does not optimise measured latency, bandwidth or congestion.

## Further reading
- [RFC 4271: A Border Gateway Protocol 4 (BGP-4)](https://www.rfc-editor.org/rfc/rfc4271)
- [Cisco: BGP best-path algorithm](https://www.cisco.com/c/en/us/support/docs/ip/border-gateway-protocol-bgp/13753-25.html)
