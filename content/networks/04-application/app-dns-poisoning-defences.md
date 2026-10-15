---
id: app-dns-poisoning-defences
title: DNS poisoning defences and their assumptions
level: intermediate
minutes: 3
sourceLesson: app-dns-wire
summary: Randomness and response validation raise distinct barriers to off-path poisoning.
---

A forged UDP DNS answer must match an outstanding query and arrive in time to be accepted. A uniformly random sixteen-bit transaction ID offers 65,536 possibilities. This unit examines additional barriers and the assumptions behind their combined guessing space.

## Defences

- **Source port randomisation.** The emergency fix: pick a random UDP source port per query. Because the attacker must now guess the port *and* the ID, the possibilities multiply:

```formula
S = 2^16 P
S = 28,000 × 65,536 = 1,835,008,000
where
S: the number of equally likely (port, ID) combinations
P: the number of source ports the resolver picks from, independently and uniformly; here a hypothetical 28,000
^: "to the power of"; 2^16 = 65,536 possible IDs
In words: 28,000 ports times 65,536 IDs gives about 1.8 billion combinations, so each guess is 28,000 times less likely to hit.
```

Actual resolver pools, NAT behaviour and predictability determine effective entropy; they need not equal the OS ephemeral range.
- **Bailiwick checking.** Restrict which supplied records can update cache entries under the responding server’s authority and the resolver’s delegation context. A response about `x71.bank.example` must not set records for `google.com`.
- **0x20 encoding.** Randomise the letter case of the query (`wWw.ExAmPlE.cOm`). With compatible servers that preserve question case and a resolver that checks it, randomising each independently chosen ASCII letter adds one bit to the guessing model:

```formula
S_case = 2^ℓ S
where
S_case: the guessing space with case randomisation
S: the guessing space from the ID and source port alone
ℓ: the number of ASCII letters in the query name whose case is randomised; www.example.com has 13
^: "to the power of": each letter doubles the space
In words: every letter whose case is chosen at random doubles the number of possibilities an off-path attacker must cover.
```

Not every server preserves case, and fallback policies matter.
- **DNS cookies** (RFC 7873) and TCP make some off-path spoofing harder, but do not provide DNSSEC’s signed-data chain or protect against every on-path attacker.
- **DNSSEC** cryptographically authenticates covered RRsets through a configured trust chain. Other authenticated transports protect their own endpoints and hops; these guarantees are different.

Port randomisation is not the end of the story. The 2020 **SAD DNS** attack used a side channel (the global rate limit on ICMP "port unreachable" replies in Linux) to discover which port a resolver was using, bringing back the guessing game on the 16-bit ID alone.

## Key takeaways
- Independent port and case randomness can enlarge an off-path guessing space.
- Cache-admission rules, DNS cookies, signed data and authenticated transports have distinct guarantees.

## Further reading
- [RFC 5452](https://www.rfc-editor.org/rfc/rfc5452)
- [RFC 7873](https://www.rfc-editor.org/rfc/rfc7873)
- [SAD DNS original paper](https://www.cs.ucr.edu/~zhiyunq/pub/ccs20_dns_poisoning.pdf)
