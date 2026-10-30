---
id: pki-certificates-revocation
title: Revocation and certificate lifetimes
level: intermediate
minutes: 3
sourceLesson: pki-certificates
summary: Revocation changes acceptance policy without changing the original signature mathematics.
---

A certificate's signature stays mathematically valid until it expires, even if its private key is stolen the day after issue. Revocation is the attempt to withdraw trust early.

## Revocation: the unsolved part

A server private-key leak does not change its certificate’s mathematically valid signature. Expiry and revocation separately change whether clients should accept it. **Revocation** tries to cut that short:

- **CRLs**: the CA publishes a signed list of revoked serial numbers. Simple, but lists can grow to megabytes.
- **OCSP**: the client asks the CA's responder about one certificate. Small, but slow, and it tells the CA which sites you visit.
- **OCSP stapling**: the server fetches a signed OCSP response itself and attaches it to the handshake, avoiding that client’s separate status lookup and its associated privacy/latency costs. Coverage and freshness still matter.

All three hit the same problem: what should a client do if the answer does not arrive? Hard-failing breaks sites whenever a responder has an outage. A **soft-fail** policy accepts when status cannot be obtained, which an attacker may exploit by blocking retrieval. Other clients use hard-fail, cached or pushed status. No single behavior applies to every browser, platform and private PKI.

> [!analogy] Real-world analogy: A shop checking a stolen-card list
> A stolen bank card still looks valid: the chip, name and expiry date are all genuine. A shop catches it only by asking the bank, and if the phone line to the bank is down, the shop must choose between refusing every card and accepting some stolen ones.
>
> **How it maps:** The card's genuine features are the certificate's valid signature. Phoning the bank is an OCSP request, a printed hot-list of stolen card numbers is a CRL, and a customer arriving with a recent letter from the bank is OCSP stapling. Accepting cards when the line is down is soft-fail; refusing them is hard-fail.
>
> **Where it stops:** A shopkeeper might notice a nervous customer. A TLS client has only the data it receives, and an attacker who controls the network can deliberately block the revocation lookup to trigger soft-fail.

Browser approaches differ. Chrome distributes **CRLSets** with selected revocations rather than complete coverage. Mozilla's **CRLite** pushes compressed revocation data for covered WebPKI certificates to Firefox. Mozilla enabled it for desktop Firefox from version 137 and announced in August 2025 that Firefox 142 would stop OCSP checks for domain-validated certificates, relying on CRLite instead. Coverage and fallback policy still matter. Let's Encrypt turned off its OCSP service in August 2025 and publishes CRLs instead.

Shorter validity reduces the exposure window for a particular certificate, but does not eliminate the need for revocation, key replacement or preventing fraudulent renewal. The CA/Browser Forum's Baseline Requirements cut maximum public TLS certificate lifetimes from 398 days to 200 days for certificates issued from 15 March 2026, then to 100 days from 15 March 2027 and 47 days from 15 March 2029 (as published in October 2026; check the current requirements). Automation becomes operationally valuable; the policy does not mandate ACME specifically.

## Key takeaways
- Revocation changes acceptance policy without changing the original signature mathematics.
- CRLs, OCSP and stapling have different distribution, latency and privacy properties.
- Soft-fail and browser-pushed coverage vary; shorter lifetimes reduce an exposure window without eliminating renewal abuse.

## Further reading
- [X.509 certificate profile — RFC 5280](https://www.rfc-editor.org/rfc/rfc5280)
- [Certificate revocation — Wikipedia](https://en.wikipedia.org/wiki/Certificate_revocation)
- [Baseline Requirements — CA/Browser Forum](https://cabforum.org/working-groups/server/baseline-requirements/requirements/)
