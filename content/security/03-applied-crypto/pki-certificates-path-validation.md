---
id: pki-certificates-path-validation
title: Building and validating certificate paths
level: intermediate
minutes: 2
sourceLesson: pki-certificates
summary: Path building chooses an issuer chain; validation checks signatures, dates, constraints and application identity policy.
---

Certificates bind names to public keys through trusted issuers. A valid signature is only one part of deciding whether an application should accept that binding.

## How a client validates a chain

A client given a leaf and some intermediates must **build a path** to a trusted root, then check every link:

1. Each certificate's signature verifies with the next one's public key.
2. The certificates in the path are within their validity windows. A trust anchor is an input to validation, not necessarily processed as another path certificate; root-certificate expiry handling varies.
3. Intermediate issuers are authorized CAs; Basic Constraints, applicable Key Usage, path-length constraints, name constraints and unrecognized critical extensions are checked.
4. The leaf's SAN matches the hostname, and its EKU allows `serverAuth`.
5. Apply the client's revocation and browser CT policies. Coverage, freshness and failure handling vary; certificate-path validation alone does not establish either.

Path building is harder than it looks, because a CA can have several certificates with the same key: a self-signed root plus **cross-signed** versions issued by older roots, so new CAs work on old devices. On 30 September 2021 the old root that cross-signed Let's Encrypt, DST Root CA X3, expired. Clients with the appropriate trust anchor and usable path building could validate through ISRG Root X1. Other client families handled the cross-sign and trust-anchor expiry according to their own policy; compatibility was not one universal path switch. Some older OpenSSL 1.0.2 configurations selected the expired path and failed, affecting API integrations.

Here is step 1 alone, using the `cryptography` library:

```python
from cryptography import x509

def check_links(chain):
    # chain[0] = leaf, chain[-1] = root
    # Pair each child with its next issuer.
    for c, iss in zip(chain, chain[1:]):
        # raises if the signature is bad
        c.verify_directly_issued_by(iss)
        print(c.subject.rfc4514_string(),
              "<-",
              iss.subject.rfc4514_string())
```

For a root, intermediate and leaf, this prints `CN=shop.test <- CN=Toy Issuing CA` then `CN=Toy Issuing CA <- CN=Toy Root`. `verify_directly_issued_by` checks issuer/subject name agreement and signature validity; this loop does not check dates, hostname, CA constraints, trust, revocation or CT. Use a maintained validator and configure the required policy. `cryptography.x509.verification.PolicyBuilder` can build a server certificate verifier with hostname/path checks, but does **not** automatically perform live revocation or browser CT enforcement.

## Key takeaways
- Path building chooses an issuer chain; validation checks signatures, dates, constraints and application identity policy.
- A direct issuer-signature loop does not establish hostname validity, trusted roots, revocation or CT.
- Serve required intermediates and allow valid alternative paths when cross-signed roots expire.

## Further reading
- [X.509 certificate profile — RFC 5280](https://www.rfc-editor.org/rfc/rfc5280)
- [ACME — RFC 8555](https://www.rfc-editor.org/rfc/rfc8555)
