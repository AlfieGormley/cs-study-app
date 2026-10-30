---
id: app-dns-poisoning-models
title: "DNS spoofing races and guessing-space models"
level: intermediate
minutes: 4
sourceLesson: app-dns-wire
summary: "Forged UDP responses must match the outstanding query and race the legitimate answer."
---

## Cache poisoning

A recursive resolver caches answers for their TTL. If an attacker gets a forged answer accepted, later matching lookups may receive poisoned cached data until expiry or replacement. Other caches, record types, validation and application authentication affect the result. That is **cache poisoning**.

For ordinary outstanding UDP queries, necessary response-matching checks include:

- the question (name, type, class),
- the transaction **ID**,
- the source IP and port it sent to, arriving at the **source port** it sent from.

An off-path attacker cannot see the query, so they must guess. With a fixed, known source port, the only unknown is the 16-bit ID: 65,536 possible values. One blind forged reply therefore matches once in 65,536 tries, and an attacker who races 100 forged replies in before the real answer covers about 1 in 650 of the possibilities. It must also beat the legitimate answer, which ends the race the moment it arrives.

> [!analogy] Real-world analogy: Forging a reply to someone else's letter
> You write to your bank quoting a five-digit reference number and accept the first reply that quotes it back. A fraudster who cannot read your post wants to slip in a fake reply first. They must guess the reference, and each fake letter has only a tiny chance of carrying the right one.
>
> **How it maps:** The reference number is the DNS transaction ID (and, later, the source port). The genuine bank reply is the legitimate DNS answer: once it arrives, the race is over. A fake that matches is accepted and remembered, like a poisoned cache entry.
>
> **Where it stops:** A fraudster might wait weeks for your next letter. Kaminsky's method, below, lets an attacker trigger a fresh "letter" whenever they like, so they can make hundreds of attempts in quick succession.

### The Kaminsky attack (2008)

A simple vulnerable-resolver model offers a race only when a target name's cached answer expires. Dan Kaminsky's 2008 technique avoids that wait by causing fresh lookups and attempting to replace delegation data:

1. Make the resolver look up a fresh random name unlikely to have a cached answer: `x71.bank.example`.
2. Race the real answer with a flood of forged responses with guessed IDs.
3. Each forged response says "I don't know `x71`, but the name server for **bank.example** is `ns.bank.example` at **192.0.2.66**" (attacker-controlled), in the authority and additional sections.
4. If a forged response wins and its delegation records are admitted, the vulnerable resolver caches the attacker's server for the target zone.
5. If none wins, try `x72.bank.example` immediately. There is no TTL to wait for.

The odds per attempt have not changed; what changed is the number of attempts. If each attempt independently has about a 1-in-650 chance, roughly 450 attempts give an even chance that at least one succeeds, and a resolver that answers quickly lets an attacker make those attempts in a short time. This is a simplified probability model, not a measured attack duration: real caching rules, response checks and DNSSEC change whether forged data is admitted. The defences in the next unit enlarge what the attacker must guess and restrict which records a reply can install.

## Key takeaways
- Forged replies must match outstanding-query fields and beat the legitimate answer.
- The independent ID-guess model estimates attempts, not real attack duration.

## Further reading
- [RFC 5452](https://www.rfc-editor.org/rfc/rfc5452)
