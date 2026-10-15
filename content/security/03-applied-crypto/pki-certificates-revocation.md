---
id: pki-certificates-revocation
title: Revocation and certificate lifetimes
level: intermediate
minutes: 2
sourceLesson: pki-certificates
summary: Revocation changes acceptance policy without changing the original signature mathematics.
---

Certificates bind names to public keys through trusted issuers. A valid signature is only one part of deciding whether an application should accept that binding.

## Revocation: the unsolved part

A server private-key leak does not change its certificate’s mathematically valid signature. Expiry and revocation separately change whether clients should accept it. **Revocation** tries to cut that short:

- **CRLs**: the CA publishes a signed list of revoked serial numbers. Simple, but lists can grow to megabytes.
- **OCSP**: the client asks the CA's responder about one certificate. Small, but slow, and it tells the CA which sites you visit.
- **OCSP stapling**: the server fetches a signed OCSP response itself and attaches it to the handshake, avoiding that client’s separate status lookup and its associated privacy/latency costs. Coverage and freshness still matter.

All three hit the same problem: what should a client do if the answer does not arrive? Hard-failing breaks sites whenever a responder has an outage. A **soft-fail** policy accepts when status cannot be obtained, which an attacker may exploit by blocking retrieval. Other clients use hard-fail, cached or pushed status. No single behavior applies to every browser, platform and private PKI.

Browser approaches differ. Chrome distributes **CRLSets** with selected revocations rather than complete coverage. Mozilla began production **CRLite** use in Firefox 142, using compressed revocation data for covered WebPKI certificates; coverage and fallback policy matter. Let's Encrypt ended its OCSP service in 2025 and publishes CRLs instead.

Shorter validity reduces the exposure window for a particular certificate, but does not eliminate the need for revocation, key replacement or preventing fraudulent renewal. The CA/Browser Forum has voted to cut maximum public certificate lifetimes from 398 days to 200 days from March 2026, then 100 days in 2027 and 47 days in 2029. The issuance-date cutoffs are 15 March 2026, 2027 and 2029 respectively. Automation becomes operationally valuable; the policy does not mandate ACME specifically.

## Key takeaways
- Revocation changes acceptance policy without changing the original signature mathematics.
- CRLs, OCSP and stapling have different distribution, latency and privacy properties.
- Soft-fail and browser-pushed coverage vary; shorter lifetimes reduce an exposure window without eliminating renewal abuse.

## Further reading
- [X.509 certificate profile — RFC 5280](https://www.rfc-editor.org/rfc/rfc5280)
- [ACME — RFC 8555](https://www.rfc-editor.org/rfc/rfc8555)
