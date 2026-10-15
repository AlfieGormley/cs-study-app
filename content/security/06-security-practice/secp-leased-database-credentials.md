---
id: secp-leased-database-credentials
title: Short-lived and dynamic credentials
level: intermediate
minutes: 3
sourceLesson: secp-secrets
summary: Understand leases, revocation failures and the limits of attribution.
---

Short-lived credentials aim to reduce how long a stolen value can be reused. A database credential created on demand has a different lifecycle from a shared static password: creation, lease renewal and revocation all need to work with the target database.

## Short-lived and dynamic credentials

Reducing credential lifetime limits reuse only when expiry or revocation is enforced by the system accepting it. It does not undo access or data theft that happened before expiry.

**Dynamic secrets** are generated on demand. Vault's database secrets engine, for example, can create a unique database credential per request with a **lease** (say one hour). Expiry/revocation triggers the configured database revocation operation; successful removal depends on connectivity, permissions and database semantics. Leases may also be renewable.

```
 service ── auth (k8s SA) ──> Vault
    ^                          │
    │  user v-billing-8f2a     │ CREATE
    │  + password, TTL 1h      │ USER
    └──────────────────────────┤
              lease expiry ──> │ revoke*
```

*Revocation attempts the configured database operation; monitor failures.

Benefits:

- A properly enforced lease bounds use; failed revocation must be detected and repaired.
- If each instance obtains a distinct credential and database auditing is enabled, logs identify that credential; theft means they cannot prove which actor used it.
- Revoking a credential used only by one instance limits the operational scope; shared credentials or dependent sessions can complicate this.

The same idea applies everywhere: AWS AssumeRole sessions can request 15 minutes up to the role's configured maximum of 1–12 hours; role chaining has a one-hour limit. Other STS APIs have different duration rules; GCP and Azure have equivalents.

## Key takeaways
- On-demand credentials can separate requesters and narrow the scope of revocation.
- A lease requires effective expiry or revocation; monitor failed database operations.
- An audit record identifies a credential, not necessarily the person using a stolen credential.
- AWS session-duration limits vary by API and role-chaining context.

## Further reading
- [Vault database secrets](https://developer.hashicorp.com/vault/docs/secrets/databases)
- [Vault lease and revocation](https://developer.hashicorp.com/vault/docs/concepts/lease)
- [AWS AssumeRole duration](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html)
