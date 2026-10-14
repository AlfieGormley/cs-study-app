---
id: rel-transport-storage-security-limits
title: Transport and storage encryption limits
level: advanced
minutes: 3
summary: Place layered encryption controls and identify what a compromised application can still read.
sourceLesson: rel-security
---

Security failures can also interrupt service. This unit assumes the authentication and authorisation distinction from API Design: proving a caller’s identity does not prove permission to read a particular record.

Security is a reliability property: a breach, ransomware attack or DDoS can harm availability as well as confidentiality or integrity. In system design interviews and in real architecture reviews, security is judged on the same terms as everything else: what's the threat, what's the control, and what does it cost?

The following units place the security controls on the diagram and explain their limits.

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

Use **TLS** for supported application protocols across network boundaries (1.2 minimum, 1.3 preferred under current IETF guidance); use an appropriate encrypted transport for other traffic. TLS gives confidentiality, integrity, and server authentication via certificates.

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

## Key takeaways

- Layer controls from the edge to audit, using TLS on network hops and mTLS for service identities where configured.
- HSTS protects after policy is learned or preloaded; automate certificate renewal.
- At-rest encryption protects stored copies, while a compromised authorised application can still decrypt. Identity authentication does not replace object authorisation.

## Further reading

- [Secrets management cheat sheet (OWASP)](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [AWS Well-Architected Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
- [Recommendations for TLS and DTLS (RFC 9325)](https://www.rfc-editor.org/rfc/rfc9325)
