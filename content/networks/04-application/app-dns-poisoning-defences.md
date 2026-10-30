---
id: app-dns-poisoning-defences
title: DNS poisoning defences and their assumptions
level: intermediate
minutes: 3
sourceLesson: app-dns-wire
summary: Randomness and response validation raise distinct barriers to off-path poisoning.
---

A forged UDP DNS answer must match an outstanding query and arrive in time to be accepted. A uniformly random sixteen-bit DNS transaction ID offers 65,536 possibilities. This unit examines additional barriers and the assumptions behind their combined guessing space.

## Defences

- **Source port randomisation.** The emergency fix after Kaminsky: pick a random UDP source port per query. The attacker must now guess the port *and* the ID, so the possibilities multiply. A pool of about 28,000 ports turns 65,536 possibilities into roughly 1.8 billion. Actual resolver pools, NAT behaviour and predictability determine the real gain; RFC 5452 warns that a NAT which assigns outgoing ports sequentially, or from a small range, can dramatically reduce it.
- **Bailiwick checking.** Restrict which supplied records can update cache entries under the responding server’s authority and the resolver’s delegation context. A response about `x71.bank.example` must not set records for `google.com`.
- **0x20 encoding.** Randomise the letter case of the query (`wWw.ExAmPlE.cOm`) and require the reply's question to echo it exactly. Each letter whose case is chosen at random doubles the possibilities, so `www.example.com`, with 13 letters, multiplies them by 8,192. It only works with servers that preserve the question's case, and resolvers need a fallback policy for those that do not.
- **DNS cookies** (RFC 7873) and TCP make some off-path spoofing harder, but do not provide DNSSEC’s signed-data chain or protect against every on-path attacker.
- **DNSSEC** cryptographically authenticates covered RRsets through a configured trust chain. Other authenticated transports protect their own endpoints and hops; these guarantees are different.

The random ID, the random port and random letter case combine because independent random choices multiply:

```formula reference
S = 2^16 × P × 2^ℓ
where
S: the number of equally likely combinations an off-path attacker must cover with forged replies
2^16: the 65,536 possible DNS transaction IDs
P: the number of source ports the resolver chooses from, independently and uniformly
ℓ: the number of letters in the query name whose case is randomised and checked
^: "to the power of"; 2^ℓ doubles once for every letter
In words: every independent random choice the attacker must match multiplies the guessing space, so ID, port and letter case together make a blind match far less likely than the ID alone.
```

Port randomisation is not the end of the story. The 2020 **SAD DNS** attack used a side channel (the global rate limit on ICMP "port unreachable" replies in Linux) to discover which port a resolver was using, bringing back the guessing game on the 16-bit ID alone.

## Key takeaways
- Independent port and case randomness can enlarge an off-path guessing space.
- Cache-admission rules, DNS cookies, signed data and authenticated transports have distinct guarantees.

## Further reading
- [RFC 5452](https://www.rfc-editor.org/rfc/rfc5452)
- [RFC 7873](https://www.rfc-editor.org/rfc/rfc7873)
- [SAD DNS original paper](https://www.cs.ucr.edu/~zhiyunq/pub/ccs20_dns_poisoning.pdf)
