---
id: ip-bgp-best-path
title: Choose a BGP path by policy
level: advanced
minutes: 3
sourceLesson: ip-bgp
summary: Use local preference and the stated teaching ranking while recognising vendor-specific selection rules.
---

Use local preference and the stated teaching ranking while recognising vendor-specific selection rules.

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

This executable teaching model ranks already eligible routes, assumes equal weight/local-origination status, counts AS_SEQUENCE entries, compares MED across all candidates, and uses input order for complete ties. It deliberately omits the rest of real BGP selection:

```python
def rank(r):
    # min() should prefer higher preference.
    return (-r["lp"],
            len(r["path"]),
            r["origin"],
            r["med"],
            0 if r["ebgp"] else 1,
            r["igp"])

routes = [
    dict(name="transit", lp=100,
         path=[64500, 3356, 65010],
         origin=0, med=0,
         ebgp=True, igp=10),
    dict(name="peer", lp=200,
         path=[64600, 64700, 65010],
         origin=0, med=0,
         ebgp=True, igp=10),
    dict(name="customer", lp=300,
         path=[65010, 65010, 65010],
         origin=0, med=0,
         ebgp=True, igp=10),
]
best = min(routes, key=rank)
print(best["name"])  # customer
```

> [!example] A worked choice
> Your AS hears 203.0.113.0/24 three ways:
> - From a transit provider: LOCAL_PREF 100, path `64500 3356 65010` (3 ASes).
> - From a peer: LOCAL_PREF 200, path `64600 64700 65010` (3 ASes).
> - From customer 65010 directly: LOCAL_PREF 300, path `65010 65010 65010` (prepended to 3).
>
> With all eligibility checks passed and earlier vendor-specific preferences equal, LOCAL_PREF decides: the customer route wins at 300. The customer's prepending was meant to push traffic away, but it only affects step 3, which is never reached.

Note what's missing: bandwidth, latency, congestion. BGP picks paths by **policy** and AS count, not performance. The shortest AS_PATH may cross an ocean twice.

## Key takeaways
- Higher LOCAL_PREF can decide before AS_PATH length.
- Origin and MED have specific meanings and comparison conditions.
- The executable tuple rank omits real selection steps and deliberately compares MED across candidates.
- BGP path policy does not optimise measured latency, bandwidth or congestion.

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
