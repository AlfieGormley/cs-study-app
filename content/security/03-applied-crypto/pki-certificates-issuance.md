---
id: pki-certificates-issuance
title: Issuing certificates with ACME
level: intermediate
minutes: 2
sourceLesson: pki-certificates
summary: A CSR demonstrates possession of the requested public key’s private half; domain control needs its own validation.
---

Certificates bind names to public keys through trusted issuers. A valid signature is only one part of deciding whether an application should accept that binding.

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

For Let's Encrypt wildcard requests, use DNS-01. Control of the delegated challenge record can satisfy this validation; it need not give control of every record in the entire zone. Organisation Validation (OV) and Extended Validation (EV) add legal-entity validation requirements. They do not inherently provide stronger encryption than DV; actual cryptographic strength depends on the chosen keys, algorithms and protocol. Historical UI-effectiveness claims are omitted here because their research evidence was not reviewed.

Domain validation has a weak spot: it trusts DNS and routing *from the CA's point of view*. An attacker who hijacks a BGP route to your server for a few minutes could pass HTTP-01. CAs now validate from several network vantage points (**multi-perspective validation**), and you can publish a **CAA** DNS record listing which CAs may issue for your domain at all.

## Key takeaways
- A CSR demonstrates possession of the requested public key’s private half; domain control needs its own validation.
- Let’s Encrypt wildcard validation uses DNS-01, including suitable delegated challenge records.
- CAA and multi-perspective validation constrain compliant issuance and localized routing attacks.

## Further reading
- [X.509 certificate profile — RFC 5280](https://www.rfc-editor.org/rfc/rfc5280)
- [ACME — RFC 8555](https://www.rfc-editor.org/rfc/rfc8555)
