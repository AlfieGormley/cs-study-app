---
id: rel-security
title: Security in system design
level: advanced
minutes: 15
summary: Encrypt in transit and at rest, manage keys with KMS and envelope encryption, enforce least privilege and zero trust, handle secrets properly, and design for OWASP risks and DDoS.
---

Security is a reliability property: a breach, ransomware attack or DDoS can harm availability as well as confidentiality or integrity. In system design interviews and in real architecture reviews, security is judged on the same terms as everything else: what's the threat, what's the control, and what does it cost?

This lesson covers the building blocks you're expected to place on the diagram.

## Defence in depth

No single control is perfect, so layer them. An attacker who gets past one layer should meet another.

```
[Edge]    DDoS protection, WAF, TLS
  ▼
[Gateway] authN, rate limits
  ▼
[Service] authZ, input validation
  ▼
[Data]    encryption, least privilege
  ▼
[Audit]   logs, alerts, detection
```

## Encryption in transit

Everything crossing a network should use **TLS** (1.2 minimum, 1.3 preferred). TLS gives confidentiality, integrity, and server authentication via certificates.

- **At the edge**: HTTPS everywhere, with HSTS so browsers upgrade requests to HTTPS once a policy is learned (or preloaded); the initial visit is otherwise not protected by HSTS alone.
- **Inside the network**: historically teams terminated TLS at the load balancer and sent plain HTTP inside the "trusted" network. Zero trust (below) rejects this; internal hops should be encrypted too.
- **Mutual TLS (mTLS)**: both sides present certificates, so the server also authenticates the *client service*. Service meshes like Istio and Linkerd issue short-lived certificates to every workload and do mTLS transparently, typically using SPIFFE identities.

> [!tip] Automate certificates
> Expired certificates are a classic outage cause. Use automated issuance and renewal (ACME/Let's Encrypt, cloud certificate managers, mesh-issued certs with hours-long lifetimes), and alert well before expiry.

## Encryption at rest

Encrypting stored data protects against stolen disks, mis-disposed hardware, leaked snapshots and some classes of storage-layer access.

Layers, from coarse to fine:

| Layer | Protects against |
|---|---|
| Disk / volume | stolen hardware |
| Database / object store | encrypted copies without usable keys; not admins authorized to decrypt |
| Application-level fields | DB admins, SQL injection dumps |

Be honest about the limits: if an attacker compromises the application, which can decrypt, disk encryption doesn't help. **Field-level** encryption of the most sensitive data (card numbers, national IDs), with keys the database never sees, raises the bar further.

## Key management and envelope encryption

Encryption moves the problem to **key management**. A plaintext key accessible to the same attacker as its ciphertext provides little protection; an encrypted DEK can safely accompany the ciphertext when its wrapping key remains protected.

A **Key Management Service** controls key use through an authenticated API. AWS KMS provides HSM-backed key protection; Google Cloud KMS and Azure Key Vault also offer software-backed options. Select the required protection level explicitly and configure audit logging. The following envelope example uses AWS KMS-style data-key APIs.

But you can't send terabytes to KMS. **Envelope encryption** solves this:

```
1. Ask KMS for a data key (DEK)
   ← plaintext DEK + DEK encrypted
     under the master key (KEK)
2. Encrypt data locally with DEK
   (AES-256-GCM, fast)
3. Store ciphertext + encrypted DEK
   + GCM nonce and authentication tag
4. Discard plaintext DEK from memory

Decrypt: send encrypted DEK to KMS
  → plaintext DEK → decrypt locally
```

For AES-GCM, never reuse a nonce with the same key and respect the implementation's per-key/message limits. Prefer a vetted encryption SDK and framed format for large objects.

Benefits:

- Bulk encryption happens locally and fast; KMS only handles tiny keys.
- The master key never leaves the HSM.
- Each KMS unwrap call is subject to access controls and audit logging. A cached plaintext DEK can decrypt many records locally without another KMS call, so KMS logs alone do not audit every data read.
- **Key rotation** need not rewrite bulk data. AWS KMS automatic rotation retains old key material for decrypting existing DEKs; moving to a different KEK may instead require re-wrapping DEKs.
- **Crypto-shredding**: destroy the relevant key material and every remaining plaintext or alternate-wrapped DEK, and ciphertext with no other recovery path becomes unreadable, which is useful for erasure requests and per-tenant keys.

AWS services including S3, EBS, RDS and DynamoDB offer KMS integrations; exact key handling and defaults depend on the service and selected encryption mode.

## Least privilege and identity

Every identity (human, service, CI job) should have **only the permissions it needs, for only as long as it needs them**.

- **Scoped roles**: the image-resizer service can read `uploads/*` and write `thumbnails/*`, nothing else. Not `s3:*` on `*`.
- **Short-lived credentials**: workloads assume roles and receive temporary tokens (AWS STS, GCP workload identity) instead of long-lived access keys in config files.
- **Just-in-time human access**: engineers request elevated production access for a ticket, time-boxed and logged, rather than holding standing admin rights.
- **Separate accounts/projects** for prod, staging and backups, so one compromised credential has a limited blast radius.

> [!warning] Over-permissioned roles turn small bugs into breaches
> In the 2019 Capital One breach, a server-side request forgery (SSRF) flaw in a misconfigured web application firewall let an attacker obtain the temporary credentials of the firewall's IAM role from the instance metadata service. That role could list and read a large number of S3 buckets, so one bug exposed data on over 100 million people. Least privilege would have limited it to what the WAF actually needed.

## Secrets management

Secrets are database passwords, API keys, signing keys and tokens. Rules:

- **Never in source control**, container images, or plain environment files committed to the repo. Scan for leaks in CI (tools like gitleaks or GitHub secret scanning).
- **Store in a secrets manager**: HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager. Access is authenticated by workload identity, authorised per secret, and audited.
- **Rotate** automatically; better still, use **dynamic secrets** (Vault can mint a database user with a 1-hour lease per service instance).
- **Never log them**; redact in structured logging.
- Prefer identity-based auth (IAM roles, mTLS) to avoid long-lived shared passwords; temporary credentials and certificate private keys still require protection.

## Zero trust

The traditional model was a castle and moat: a hard perimeter (VPN, firewall) and a soft, trusted interior. Once an attacker got in, by phishing a laptop for example, they could move laterally.

**Zero trust** (Google's BeyondCorp, NIST SP 800-207) assumes the network is hostile everywhere:

- **No implicit trust from network location.** Being inside the VPC or office network grants nothing.
- **Authenticate and authorise every request**, user and device, based on identity and context (device health, location, risk).
- **Encrypt all traffic**, including service-to-service (mTLS).
- **Least privilege per request**, enforced by policy engines (e.g. Open Policy Agent) close to each resource.
- **Continuous verification** and logging rather than a one-time login.

```
Castle-and-moat    Zero trust
┌──────────────┐   [svc A]─mTLS─▶[svc B]
│ trusted LAN  │     ▲ identity + policy
│ A ──▶ B ──▶ C│     │ on every call
└──────────────┘   [user+device]─▶[proxy]
```

## OWASP Top 10 at a high level

The OWASP Top 10:2025 ranks the most critical web application risks. The categories, in order, with the design-level response for each:

| Risk | Design response |
|---|---|
| A01 Broken Access Control | server-side authZ on every object |
| A02 Security Misconfiguration | hardened defaults, IaC, config scanning |
| A03 Software Supply Chain Failures | pinned, scanned, signed dependencies |
| A04 Cryptographic Failures | TLS everywhere, KMS, strong algorithms |
| A05 Injection | parameterised queries, output encoding |
| A06 Insecure Design | threat modelling at design time |
| A07 Authentication Failures | MFA, rate-limited login, managed IdP |
| A08 Software or Data Integrity Failures | signed artefacts, verified updates |
| A09 Security Logging and Alerting Failures | audit logs, detections that page |
| A10 Mishandling of Exceptional Conditions | fail closed, safe error handling |

What changed from the 2021 list:

- **SSRF** is no longer its own category; it's folded into A01 Broken Access Control.
- **A03** broadens 2021's "Vulnerable and Outdated Components" to the whole software supply chain: build systems, distribution and dependencies.
- **A10** is new: failing open, swallowing errors and leaking detail in error messages.
- A07 and A09 were renamed ("Identification and" dropped; "Monitoring" became "Alerting").

Broken access control is number one: insecure direct object references like `GET /invoices/1234` that don't check the invoice belongs to the caller. The fix is architectural: authorisation enforced in a consistent layer, never just hidden in the UI.

> [!note] Fail closed
> A10 is a reliability lesson as much as a security one. If the authorisation service times out, the safe default is to *deny*, not allow. Decide the failure behaviour of every security check explicitly, because a check that fails open under load is a vulnerability that only appears during incidents.

## DDoS mitigation

A **distributed denial-of-service** attack floods you with traffic from many sources. Types:

- **Volumetric (L3/L4)**: UDP floods, reflection/amplification (DNS, NTP, memcached). Measured in Tbps.
- **Protocol**: SYN floods exhausting connection tables.
- **Application (L7)**: HTTP floods of expensive requests (search, login), which look like real users.

Defences, layered:

1. **Absorb at the edge**: anycast CDN or DDoS service (AWS Shield, Cloudflare, Google Cloud Armor) with huge distributed capacity. Anycast can distribute traffic across an operator's sites, depending on routing and source geography; it does not guarantee even distribution or unlimited capacity.
2. **Hide the origin**: restrict origin ingress and authenticate your own edge (for example with mTLS or provider-supported origin authentication). An allow-list of shared CDN ranges alone may still admit another customer's traffic.
3. **Rate limit** per IP, per API key and per user, at the edge and the gateway.
4. **WAF rules and bot detection** for L7 patterns; challenges (CAPTCHA, proof-of-work) for suspicious clients.
5. **Make expensive endpoints cheap**: cache safe responses, require appropriate auth and use bounded admission queues. Authentication alone does not make a costly request cheap. Combine with the load shedding and autoscaling from earlier lessons.
6. **Reduce attack surface**: close unused ports, don't expose databases or admin panels publicly.

> [!example] Amplification maths
> A memcached reflection attack sends a ~15-byte request with a spoofed source address; the server replies with up to hundreds of kilobytes to the victim. Amplification factors above 10,000× were observed in 2018, which is how attacks passed 1 Tbps. Never expose UDP services like memcached to the internet.

## Key takeaways

- Layer controls (defence in depth) from edge to data, and treat security incidents as availability incidents too.
- Encrypt in transit everywhere (TLS, mTLS internally) and at rest, with field-level encryption for the most sensitive data.
- Use KMS with envelope encryption: data keys encrypt data locally; select the required key-protection level, and audit both KMS operations and application reads (cached data keys bypass KMS calls).
- Least privilege with short-lived, scoped credentials limits blast radius; over-permissioned roles turn small bugs into breaches.
- Keep secrets in a secrets manager, rotate them, never commit or log them; prefer identity over shared secrets.
- Zero trust means no implicit trust from network location: authenticate, authorise and encrypt every request.
- DDoS defence is layered: anycast edge absorption, origin hiding, rate limits, WAF, and cheap expensive endpoints.

## Further reading

- [OWASP Top 10:2025](https://top10.owasp.org/2025/)
- [A01:2025 Broken Access Control (OWASP)](https://top10.owasp.org/2025/A01_2025-Broken_Access_Control/)
- [Secrets management cheat sheet (OWASP)](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [AWS KMS concepts](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html)
- [AWS Encryption SDK concepts: envelope encryption](https://docs.aws.amazon.com/encryption-sdk/latest/developer-guide/concepts.html)
- [NIST SP 800-207: Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final)
- [AWS Well-Architected Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
- [AWS best practices for DDoS resiliency](https://docs.aws.amazon.com/whitepapers/latest/aws-best-practices-ddos-resiliency/welcome.html)
- [Denial-of-service attack (Wikipedia)](https://en.wikipedia.org/wiki/Denial-of-service_attack)
