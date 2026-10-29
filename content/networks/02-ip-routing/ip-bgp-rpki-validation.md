---
id: ip-bgp-rpki-validation
title: Validate route origins with RPKI
level: advanced
minutes: 4
sourceLesson: ip-bgp
summary: Predict route-origin validation states, choose precise ROAs and separate origin validation from path assurance.
---

BGP believes announcements unless someone filters them. RPKI gives routers signed evidence about which AS may originate which prefixes, so they can spot one common kind of hijack.

## RPKI: authorising route origins

The **Resource Public Key Infrastructure** adds cryptographic evidence about who may originate a prefix.

1. Resource certificates form a validation chain rooted in configured trust anchors. They attest who holds the address and AS resources within this system, rather than legal ownership.
2. A holder signs a **ROA** (route origin authorisation): a statement that one named AS may originate a prefix, announced at any length from the prefix's own length up to a stated maximum length (**maxLength**).
3. Validator software checks signed objects and supplies validated prefix/origin/max-length records to routers. For the simple AS_SEQUENCE paths here, the origin is the final ASN.

**Route origin validation** (ROV, RFC 6811) gives each route one of three states:

| State | Meaning |
|---|---|
| Valid | At least one covering validated record authorises both origin and length |
| Invalid | Covering validated records exist, but none authorises both origin and length |
| NotFound | No validated record covers it |

For a route covered by a ROA, two checks must both pass: the route's origin AS (the last ASN in its AS_PATH) must be the AS the ROA names, and its prefix length must be no longer than the ROA's max length. A covered route that fails either check against every covering ROA is Invalid.

> [!analogy] Real-world analogy: A signed collection authorisation
> A warehouse keeps letters signed by each property's owner: "Only Acme Removals may collect from this address, in loads no smaller than a full van." When a lorry arrives, the guard checks the company name on the final paperwork and the load size against the letter.
>
> **How it maps:** The signed letter is a ROA, the property is the prefix, the named company is the authorised origin AS, and the load-size limit is maxLength. The guard is a router doing route origin validation; turning lorries away is a local policy of dropping Invalid routes.
>
> **Where it stops:** The guard checks only the name of the final company. A forger who writes "Acme Removals" at the end of fake paperwork passes, just as a forged AS_PATH ending in the right ASN passes origin validation. And an address with no letter on file (NotFound) is not turned away.

Operators choose how to use validation states; **dropping Invalid** routes is a filtering policy, not an automatic effect of computing ROV. Had YouTube's /22 had a ROA with max length 22, Pakistan Telecom's /24 would have been Invalid twice over: the origin AS 17557 is not YouTube's, and 24 is more than 22.

> [!warning] Max length cuts both ways
> In a hypothetical prefix-arithmetic example, a ROA for 192.0.0.0/22 with max length 24 authorises your /24s, but if you only announce the /22, an attacker can announce a /24 with *your* ASN as origin and pass validation. RFC 9319 recommends ROAs that match exactly what you announce.

### What RPKI doesn't fix

ROV checks the **origin only**. An attacker who announces your prefix with a fake path ending in your ASN (`666 65010`) can be Valid when origin and prefix length are authorised. ROV does not validate the intervening path or detect a leak that retains an authorised origin.

- **BGPsec** (RFC 8205) signs the AS path hop by hop for participating BGPsec speakers. Its protection depends on cryptographic validation and deployment; it is not a claim that every forwarding router signs every packet.
- **ASPA** (autonomous system provider authorisation) publishes authorised provider relationships. The IETF verification draft retrieved for this review is an Internet-Draft dated August 2026; detection depends on relationship data, direction and validation rules, and is not guaranteed for every forged path.
- **Prefix filtering** remains the basic defence: providers should accept from customers only the prefixes they're registered to announce, and cap how many. The MANRS initiative publishes these practices as baseline norms.

> [!note] Content omitted after review
> Current AS/route counts, adoption percentages, router performance guarantees and the Route 53 incident's financial loss are omitted because this review did not establish reliable dated evidence for them. No live Internet routing changes were performed to validate the examples.

## Key takeaways
- A covering validated record must authorise both origin and length for a Valid result.
- Invalid and NotFound differ; rejection remains local policy.
- Unnecessarily broad maxLength can authorise forged-origin more-specifics.
- ROV does not prove the path or stop all leaks; BGPsec, ASPA and filtering address different evidence.

## Further reading
- [RFC 6811: BGP Prefix Origin Validation](https://www.rfc-editor.org/rfc/rfc6811)
- [RFC 9319: RPKI maxLength](https://www.rfc-editor.org/rfc/rfc9319)
- [MANRS](https://www.manrs.org/)
- [IETF: ASPA verification draft](https://datatracker.ietf.org/doc/draft-ietf-sidrops-aspa-verification/)
