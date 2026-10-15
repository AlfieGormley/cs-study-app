---
id: ip-bgp-routing-incidents
title: Distinguish hijacks, leaks and withdrawals
level: advanced
minutes: 3
sourceLesson: ip-bgp
summary: Compare documented routing incidents and distinguish unauthorised origins, export mistakes and local withdrawal.
---

Compare documented routing incidents and distinguish unauthorised origins, export mistakes and local withdrawal.

## When BGP goes wrong

BGP believes what neighbours tell it unless operators filter. Mistakes and attacks spread as fast as legitimate updates.

### Hijacks

A **BGP hijack** is an unauthorised route announcement for address space. A more-specific announcement is especially effective, because longest-prefix match prefers it where it is accepted and installed alongside the covering route.

- **Pakistan Telecom and YouTube, February 2008.** Ordered to block YouTube domestically, Pakistan Telecom (AS17557) announced 208.65.153.0/24, a more specific part of YouTube's 208.65.152.0/22. Its upstream, PCCW, passed it on without filtering, and much of the world's YouTube traffic was drawn to Pakistan and dropped, during the interval documented by RIPE RIS from 18:47 to 21:01 UTC on 24 February. YouTube first counter-announced the /24, then two /25s; acceptance varied by network.
- **Amazon Route 53, April 2018.** Attackers announced more-specific routes for some of Amazon's DNS address space via a small ISP (eNet, AS10297). For about two hours, DNS queries for the cryptocurrency site MyEtherWallet were answered by an attacker's server, which sent users to a phishing copy. Cloudflare documented the redirection and certificate-warning risk; this lesson does not establish a reliable total financial loss.

### Leaks

A **route leak** breaks the export rules: a network re-announces routes it should have kept to itself, usually from one provider to another.

- **Verizon and DQE, June 2019.** DQE Communications used a "BGP optimiser" that generated more-specific routes internally. These leaked to a customer, Allegheny Technologies, which announced them to its other provider, Verizon (AS701). Verizon accepted and propagated them, and traffic for parts of Cloudflare, Amazon and others was drawn through a small network that couldn't carry it.

### Self-inflicted: the Facebook outage, October 2021

On 4 October 2021 a maintenance command accidentally disconnected Facebook's backbone. Facebook's DNS servers are built to **withdraw** their BGP announcements (a **route withdrawal**) if they can't reach the data centres, so they did. The prefixes holding Facebook's authoritative DNS vanished from the Internet, `facebook.com` stopped resolving, and the backbone disconnection disrupted Facebook services. Cached DNS answers could still exist; DNS failure was a consequence that compounded the underlying network outage. Internal tools depended on the same network, which slowed the recovery.

## Key takeaways
- A hijack can attract traffic through a more-specific installed route.
- A leak exports otherwise learned routes beyond the intended policy.
- The YouTube and 2019 DQE incidents propagated through upstream filtering failures.
- Meta’s DNS-route withdrawal compounded its 2021 backbone outage.

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
