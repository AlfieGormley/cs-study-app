---
id: pki-certificates-path-validation
title: Building and validating certificate paths
level: intermediate
minutes: 4
sourceLesson: pki-certificates
summary: Path building chooses an issuer chain; validation checks signatures, dates, constraints and application identity policy.
---

A client receiving a certificate must decide two separate things: is this certificate genuinely issued under a root I trust, and is it a certificate for the server I meant to reach? Skipping either check defeats TLS.

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

For a root, intermediate and leaf, this prints `CN=shop.test <- CN=Toy Issuing CA` then `CN=Toy Issuing CA <- CN=Toy Root`. `verify_directly_issued_by` checks issuer/subject name agreement and signature validity; this loop does not check dates, hostname, CA constraints, trust, revocation or CT. Use a maintained validator and configure the required policy. `cryptography.x509.verification.PolicyBuilder` can build a server certificate verifier with hostname/path checks, but has no input for live revocation data or browser CT enforcement.

## The hostname check is half of authentication

A valid chain only proves that *some* trusted CA issued the certificate to *somebody*. Anyone can obtain a perfectly valid certificate for a domain they control, such as `attacker.example`. If the client never compares the certificate's names with the name it set out to reach, an attacker on the network can present that genuine certificate and the handshake succeeds.

RFC 9525 describes the check. The client builds its **reference identifier** from what the user or configuration asked for (the hostname in the URL, not a name supplied by the server) and compares it with the DNS names in the certificate's SAN. The Common Name must not be used, a wildcard matches exactly one leftmost label, and an automated client should abort on a mismatch rather than ask anyone.

This failure is easy to create by accident, because many TLS APIs separate the two checks:

- In Python's `ssl` module, `CERT_REQUIRED` validates the chain but *does not* match hostnames; `check_hostname` must also be on. `ssl.create_default_context()` enables both. Code that sets `check_hostname = False` "to fix a test" removes server authentication while still showing an encrypted connection.
- Disabling verification entirely (`verify=False`, `CERT_NONE`, `InsecureSkipVerify: true`) removes both checks at once.

> [!analogy] Real-world analogy: A genuine passport for the wrong person
> You are meeting a solicitor called Priya Patel. Someone hands you a real, government-issued passport and you check every security feature carefully, but you never read the name on it. It belongs to a stranger.
>
> **How it maps:** Checking the passport's security features is chain validation: the certificate really was issued under a trusted root. Reading the name and comparing it with "Priya Patel" is the hostname check: comparing the certificate's SAN with the name you intended to reach. Skipping it accepts any genuine certificate, including one the attacker obtained for their own domain.
>
> **Where it stops:** A person can be questioned further, and a passport has one name. A certificate may list many names, and must also be backed by proof that the server holds the matching private key during the handshake; the comparison is an exact rule set (RFC 9525), not a judgement call.

## Key takeaways
- Path building chooses an issuer chain; validation checks signatures, dates, constraints and application identity policy.
- A trusted chain without a hostname match authenticates nobody in particular; keep hostname checking on.
- Serve required intermediates and allow valid alternative paths when cross-signed roots expire.

## Further reading
- [X.509 certificate profile — RFC 5280](https://www.rfc-editor.org/rfc/rfc5280)
- [Service identity in TLS — RFC 9525](https://www.rfc-editor.org/rfc/rfc9525)
- [ssl — TLS/SSL wrapper — Python docs](https://docs.python.org/3/library/ssl.html)
- [X.509 verification — pyca/cryptography docs](https://cryptography.io/en/latest/x509/verification/)
- [DST Root CA X3 expiration (September 2021) — Let's Encrypt](https://letsencrypt.org/docs/dst-root-ca-x3-expiration-september-2021/)
