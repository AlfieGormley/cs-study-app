---
id: pki-certificates-issuance
title: Issuing certificates with ACME
level: intermediate
minutes: 3
sourceLesson: pki-certificates
summary: A CSR demonstrates possession of the requested public key’s private half; domain control needs its own validation.
---

A certificate is only as trustworthy as the checks the CA made before signing it. For ordinary web certificates, those checks are automated checks of control over a domain name.

## Getting a certificate

1. You generate a key pair. Protect the private key; where it is generated, backed up or used depends on the deployment and key-management service.
2. You create a **certificate signing request** (CSR, PKCS#10): your public key and requested names, *signed with your private key*. That signature proves you hold the key.
3. The CA validates that you control the names.
4. The CA signs a certificate and you install it with the intermediate chain.

For the web, step 3 is **domain validation** (DV), and **ACME** (RFC 8555) is one widely used automation protocol. It was developed through the IETF, with Let's Encrypt as an early deployment. The CA gives you a random token and checks you can publish it:

| Challenge | Proof of control |
|---|---|
| HTTP-01 | Serve key authorization under `/.well-known/acme-challenge/<token>` |
| DNS-01 | Publish a digest of key authorization under `_acme-challenge.<name>` |
| TLS-ALPN-01 | Present a special cert on port 443 |

For Let's Encrypt wildcard requests, use DNS-01. Control of the delegated challenge record can satisfy this validation; it need not give control of every record in the entire zone. Organisation Validation (OV) and Extended Validation (EV) add legal-entity validation requirements. They do not inherently provide stronger encryption than DV; actual cryptographic strength depends on the chosen keys, algorithms and protocol.

Domain validation has a weak spot: it trusts DNS and routing *from the CA's point of view*. An attacker who hijacks a BGP route to your server for a few minutes could pass HTTP-01. CAs now validate from several network vantage points (**multi-perspective validation**): as of October 2026 the Baseline Requirements demand at least four remote perspectives, rising to five from 15 December 2026, with a limited number allowed to disagree. You can also publish a **CAA** DNS record listing which CAs may issue for your domain at all.

> [!analogy] Real-world analogy: A bank posting a code to your address
> To prove you live at an address, a bank posts a one-time code there and asks you to read it back. Anyone who can read the post at that address passes, whoever owns the house.
>
> **How it maps:** HTTP-01 and DNS-01 are the posted code: the CA hands out a token and checks that it appears on your web server or in your DNS. Passing proves control of the name at that moment, not legal ownership. A BGP hijack is like an attacker briefly redirecting the post, which is why CAs now check from several places at once.
>
> **Where it stops:** A letter takes days and is hard to divert; network routes can be changed in seconds and from far away. The CA's check is also bound to your ACME account key, so the response cannot simply be replayed for a different applicant.

## Key takeaways
- A CSR demonstrates possession of the requested public key’s private half; domain control needs its own validation.
- Let’s Encrypt wildcard validation uses DNS-01, including suitable delegated challenge records.
- CAA and multi-perspective validation constrain compliant issuance and localized routing attacks.

## Further reading
- [ACME — RFC 8555](https://www.rfc-editor.org/rfc/rfc8555)
- [Challenge types — Let's Encrypt](https://letsencrypt.org/docs/challenge-types/)
- [Baseline Requirements — CA/Browser Forum](https://cabforum.org/working-groups/server/baseline-requirements/requirements/)
