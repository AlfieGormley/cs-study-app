---
id: app-dnssec-validation-chain
title: "DNSSEC trust chains and authenticated denial"
level: intermediate
minutes: 4
sourceLesson: app-dns-wire
summary: "DNSSEC authenticates covered RRsets through configured trust anchors without encrypting queries."
---

## DNSSEC: signed answers

DNSSEC adds **authenticity and integrity**, not confidentiality. A signed zone publishes signatures over covered RRsets, and a validating resolver checks the signatures up a chain to a key it already trusts.

New record types:

| Type | Holds |
|---|---|
| DNSKEY | The zone's public keys |
| RRSIG | A signature over an RRset |
| DS | Key tag, algorithm and digest fields binding a child owner name and DNSKEY, in the parent |
| NSEC / NSEC3 | RRsets used with signatures for authenticated denial of a name/type or delegation properties |

Signatures cover an **RRset** (records with the same owner name, class and type) and have an inception and expiry time, so signatures must be renewed before they expire; affected data becomes bogus for validating resolvers enforcing the chain if no valid signatures remain.

A split-key design uses a **KSK** to authenticate the DNSKEY RRset and a **ZSK** for other signed RRsets. These are operational roles, not mandatory two-key enforcement; a combined signing key is possible. A parent DS authenticates a selected child DNSKEY, which then authenticates the child DNSKEY set.

```
configured root trust anchor
  verifies root DNSKEY RRset
  root key verifies DS RRset for com.
  DS authenticates com. DNSKEY
  child key verifies its DNSKEY RRset
  com. key verifies example.com DS
  DS authenticates child DNSKEY set
  child key verifies A RRset RRSIG
```

A validating resolver walks this chain. AD can signal that the relevant answer/authority data was validated, subject to request flags and response rules. With checking enabled, bogus data normally produces SERVFAIL; an authenticated unsigned delegation is an **insecure delegation**, not automatically bogus. CD can request data without that rejection. A non-validating stub must trust the resolver and protected path for its AD assertion; a validating stub can check signatures itself.

### Proving non-existence

An attacker could also forge "this name does not exist". To sign a negative answer without signing every possible name, **NSEC** records chain the zone's existing names in sorted order: "the next name after `alpha` is `delta`" proves the exact covered name does not exist; a complete NXDOMAIN proof also needs appropriate wildcard/closest-encloser handling. The side effect is **zone walking**: following a conventional static NSEC chain can enumerate names represented in that chain. Delegations, empty nonterminals and online-signed denial techniques require care. **NSEC3** chains hashes of names instead, which slows walking but does not prevent offline dictionary attacks against the hashes.

### Costs and pitfalls

- **Bigger answers.** Signatures and keys make responses much larger, which means more truncation, TCP fallback and fragmentation, and makes signed zones more attractive for **amplification attacks** (a form of DDoS). ECDSA P-256 (algorithm 13) has far smaller signatures than RSA-2048 in the compared algorithms (64-byte ECDSA signatures versus 256-byte RSA-2048 signatures). No deployment-prevalence claim is made here.
- **Operational fragility.** Expired signatures or a key rollover with a stale DS record can make affected signed data fail validation once usable cached data and overlapping valid chains are exhausted.
- **Validator DoS.** The 2024 KeyTrap vulnerability showed that crafted key-tag collisions and many candidate signatures can force excessive validation work in vulnerable implementations. This refers to key-tag matching, not a break of signature cryptography; no universal CPU duration is asserted here.
- **Last mile.** DNSSEC authenticates signed data to whichever endpoint performs validation, through intervening caches or transports. It does nothing about who can *see* your queries.

## Key takeaways
- DNSSEC authenticates covered RRsets through configured trust anchors without encrypting queries.
- Signed denial has precise name/type and wildcard conditions; rollover mistakes and validation work have operational costs.

## Further reading
- [RFC 4034](https://www.rfc-editor.org/rfc/rfc4034)
- [RFC 4035](https://www.rfc-editor.org/rfc/rfc4035)
- [RFC 5155](https://www.rfc-editor.org/rfc/rfc5155)
- [RFC 6781](https://www.rfc-editor.org/rfc/rfc6781)
- [RFC 6840](https://www.rfc-editor.org/rfc/rfc6840)
