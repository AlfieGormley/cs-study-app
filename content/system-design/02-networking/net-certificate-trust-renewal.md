---
id: net-certificate-trust-renewal
title: "Certificate chains and renewal"
level: intermediate
minutes: 3
summary: "Validate names and chains, automate shorter certificate lifetimes and avoid oversized handshake flights."
sourceLesson: net-tls
---
A certificate is the server’s name-to-key evidence. Correct hostname coverage, a complete chain and timely renewal matter separately from the key-exchange protocol.

## Certificates and the chain of trust

A certificate binds a public key to one or more names, signed by a **certificate authority (CA)**.

```
Root CA  (in OS/browser trust store)
   |
   | signs
   v
Intermediate CA
   |
   | signs
   v
Leaf: shop.example.com
```

The client verifies:

1. The leaf certificate's names (in the **Subject Alternative Name** field) include the hostname. A wildcard `*.example.com` covers `shop.example.com` but not `a.b.example.com` or `example.com`.
2. Each certificate in the chain is signed by the next, ending at a **root** in its trust store.
3. The applicable validity periods and certificate constraints pass validation. Revocation handling depends on client policy; a successful connection does not prove that every certificate was checked online.

The server must send the leaf **and intermediates**. A missing intermediate is a classic bug: it works in desktop browsers (which may cache or fetch intermediates) but fails in mobile apps and `curl`.

### Issuance and automation

**Let's Encrypt** offers free certificates and automated issuance through ACME. As checked on 14 October 2026, its classic profile is scheduled to move from 90 to 64 days on 10 February 2027, then to 45 days on 16 February 2028; its tlsserver profile moved to 45 days in May 2026. The CA/Browser Forum maximum for newly issued publicly trusted TLS certificates became 200 days on 15 March 2026 and is scheduled to become 100 days on 15 March 2027 and 47 days on 15 March 2029. Automate renewal and monitor expiry to make these shorter cycles manageable. These public-trust requirements do not automatically govern a private PKI.

> [!note] Evidence gap
> No comparative outage dataset or reproducible TLS performance benchmark accompanies this lesson. Claims that certificate expiry is a leading outage cause, and universal throughput or signature-speed estimates, are omitted; measure your deployment.

### Revocation and transparency

- **Revocation** (CRLs, OCSP) is unreliable in practice; many clients don't check it strictly, and browsers instead push compressed revocation lists to themselves (Chrome's CRLSets, Firefox's CRLite). **OCSP stapling** lets the server attach a fresh signed status to the handshake, saving the client a lookup, but OCSP is in decline: the CA/Browser Forum made it optional, and Let's Encrypt shut its OCSP service down in 2025 in favour of CRLs. Shorter lifetimes complement revocation by limiting how long an unrevoked certificate can remain valid.
- **Certificate Transparency (CT)** uses public append-only logs; browser CT policies require qualifying publicly trusted certificates to have evidence of logging. Private certificates are not universally subject to CT. You can monitor them for certificates issued for your domains that you didn't request.
- **CAA DNS records** restrict which CAs may issue for your domain.

### Chain size also affects latency

Keep certificate chains small. For comparable certificate fields, ECDSA P-256 uses smaller keys and signatures than RSA-2048; actual certificate size and signing time depend on the chain and implementation. As the earlier TCP lesson showed, a first flight larger than the initial congestion window must wait for acknowledgements before the rest can be sent. Send necessary intermediates, omit an unnecessary root, and consider negotiated certificate compression. This is a size-dependent transport cost, not an extra round trip inherent in RSA key exchange.

## Key takeaways

- Validate the leaf hostname and a chain to a trusted root; send the required intermediates.
- A wildcard covers one label, and successful validation does not prove universal online revocation checking.
- Automate public-certificate renewal and keep the served chain lean enough for the intended transport.

## Further reading

- [How Let’s Encrypt works](https://letsencrypt.org/how-it-works/)
- [Public certificate lifetime schedule (CA/Browser Forum)](https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/)
- [Certificate lifetime changes (Let’s Encrypt)](https://letsencrypt.org/2025/12/02/from-90-to-45)
- [TLS certificate compression (RFC 8879)](https://www.rfc-editor.org/rfc/rfc8879)
