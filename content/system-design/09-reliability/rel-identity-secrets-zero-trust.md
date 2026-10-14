---
id: rel-identity-secrets-zero-trust
title: Workload identity, secrets and zero trust
level: advanced
minutes: 3
summary: Limit compromised identities and avoid implicit trust from internal network location.
sourceLesson: rel-security
---

TLS protects a network hop and KMS controls key use. An authorised identity can still cause damage if its permissions are excessive. This unit limits that blast radius and explains why a trusted-looking source IP cannot substitute for access control.

## Least privilege and identity

Every identity (human, service, CI job) should have **only the permissions it needs, for only as long as it needs them**.

- **Scoped roles**: the image-resizer service can read `uploads/*` and write `thumbnails/*`, nothing else. Not `s3:*` on `*`.
- **Short-lived credentials**: workloads assume roles and receive temporary tokens (AWS STS, GCP workload identity) instead of long-lived access keys in config files.
- **Just-in-time human access**: engineers request elevated production access for a ticket, time-boxed and logged, rather than holding standing admin rights.
- **Separate accounts/projects** for prod, staging and backups, so one compromised credential has a limited blast radius.

> [!warning] Over-permissioned roles turn small bugs into breaches
> The 2019 Capital One criminal complaint describes a misconfigured web application firewall that allowed theft of its WAF role credentials, then bucket listing and copying wherever that role had permission. Capital One reported about 100 million affected individuals in the US and six million in Canada. The SSRF/metadata scenario in this unit’s questions illustrates how such credential theft can occur; the complaint itself does not spell out that lower-level chain. Least privilege limits what a stolen role can read.

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

## Key takeaways

- Grant narrowly scoped, short-lived permissions and isolate environments and backups.
- Manage secrets through authenticated identities, rotate them and keep them out of history, images and logs.
- Zero trust checks identity and policy at resources; internal network placement does not grant access.

## Further reading

- [Secrets management cheat sheet (OWASP)](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [NIST SP 800-207: Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final)
- [AWS Well-Architected Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
