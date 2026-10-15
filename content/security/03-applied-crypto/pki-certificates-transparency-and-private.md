---
id: pki-certificates-transparency-and-private
title: Transparency, private PKI and operations
level: intermediate
minutes: 3
sourceLesson: pki-certificates
summary: CT logs and monitoring can reveal mis-issuance; an SCT promises inclusion rather than proving it.
---

Certificates bind names to public keys through trusted issuers. A valid signature is only one part of deciding whether an application should accept that binding.

## Keeping CAs honest

An unconstrained trusted CA can authorize names outside the domains it usually serves. The set of accepted roots and the constraints vary by platform and policy, so one compromised CA can affect many relying parties.

> [!example] DigiNotar, 2011
> Attackers broke into the Dutch CA DigiNotar and issued hundreds of fraudulent certificates, including one for `*.google.com`, which was used to intercept Gmail users in Iran. Chrome caught it because it pinned Google's keys. Mozilla removed trust following the incident. This example concerns the documented certificate compromise, not a verified account of the company's later legal or financial proceedings.

One major accountability mechanism is **Certificate Transparency** (CT, RFC 6962). For certificates subject to public-browser CT policies, issuance involves submitting certificates or precertificates to append-only Merkle-tree logs. This does not apply to every private or non-TLS certificate. The log returns a **signed certificate timestamp** (SCT), a promise to include the certificate, which can be delivered in a certificate extension or by other supported TLS/OCSP mechanisms. Chrome and Safari reject public certificates without enough SCTs from independent logs.

CT does not prevent mis-issuance; it makes it **visible**. You can watch the logs for your domains (crt.sh, or your CA's monitoring), and researchers routinely spot CAs breaking the rules. Chrome's 2018 Symantec changes eventually distrusted certificates chaining to its old infrastructure, not only newly issued ones. Its Entrust/AffirmTrust change used a November 2024 issuance cutoff. Exact browser policies and managed-environment exceptions differ.

Browsers also run their own root programmes. Mozilla, Apple, Microsoft and Google each decide which roots to ship, and audit them against the CA/Browser Forum's Baseline Requirements.

## Private PKI

Not every certificate comes from a public CA. Organisations run **private CAs** for internal services, VPNs, devices and **mutual TLS**, where clients present certificates too. Service meshes such as Istio issue each workload a certificate with a SPIFFE identity (`spiffe://cluster/ns/shop/sa/api`), valid for about a day by default, and rotate it automatically.

Private PKI gives you control and short lifetimes, but you inherit the CA's problems: protecting the root CA's key, distributing trust to every client, and handling revocation. Appropriate name constraints can limit what enforcing clients accept, but must cover the identity forms actually used. DNS constraints alone do not constrain arbitrary SPIFFE URI identities. A stolen issuing key can keep signing until its trust is removed or otherwise rejected.

## Pitfalls

- **Disabling verification.** `verify=False`, `CERT_NONE` or `InsecureSkipVerify: true` turn TLS into encryption with a stranger.
- **Missing intermediates.** Some clients recover missing intermediates through caches or AIA retrieval; others do not. Serve the needed intermediate chain rather than depending on client-specific recovery.
- **Expiry outages.** Certificates have known expiry dates, and still take down major services. Automate renewal and alert on days-to-expiry.
- **Pinning without a plan.** HTTP Public Key Pinning (HPKP) was removed from browsers because a wrong pin could lock users out for months. A pinning design needs an explicit update and recovery strategy; backup keys or a suitable CA pin may help, but each changes what compromises the client accepts.

## Key takeaways
- CT logs and monitoring can reveal mis-issuance; an SCT promises inclusion rather than proving it.
- Private CAs inherit key custody, trust distribution, renewal and compromise-recovery work.
- Apply constraints to the actual identity form and plan certificate renewal and pin recovery.

## Further reading
- [X.509 certificate profile — RFC 5280](https://www.rfc-editor.org/rfc/rfc5280)
- [ACME — RFC 8555](https://www.rfc-editor.org/rfc/rfc8555)
- [RFC 5280: Internet X.509 PKI Certificate and CRL Profile](https://www.rfc-editor.org/rfc/rfc5280)
- [RFC 8555: Automatic Certificate Management Environment (ACME)](https://www.rfc-editor.org/rfc/rfc8555)
- [How Certificate Transparency works](https://certificate.transparency.dev/howctworks/)
- [DST Root CA X3 expiration (September 2021) — Let's Encrypt](https://letsencrypt.org/docs/dst-root-ca-x3-expiration-september-2021/)
- [X.509 verification — pyca/cryptography docs](https://cryptography.io/en/latest/x509/verification/)
- [DigiNotar — Wikipedia](https://en.wikipedia.org/wiki/DigiNotar)
