---
id: secp-safe-secret-rotation
title: Rotating secrets without an outage
level: intermediate
minutes: 3
sourceLesson: secp-secrets
summary: Coordinate consumers and credential validity through a controlled changeover.
---

Rotation changes both a stored value and the system that accepts it. Updating a secret-store label alone cannot make a database accept two passwords. Begin with the target's overlap capabilities and a plan for consumers that cache credentials or read them only at startup.

## Rotation

Successful rotation limits reuse of the retired value and exercises the changeover before an emergency. Merely scheduling rotation does not prove that consumers or target revocation work. The hard part is doing it without downtime. The standard pattern keeps two credentials valid during a changeover:

1. **Create** a new credential alongside the old one.
2. **Deploy/propagate** it so all consumers start using it.
3. **Verify** nothing still uses the old one (check audit logs).
4. **Revoke** the old one.

AWS Secrets Manager uses version labels (`AWSPENDING`, `AWSCURRENT`, `AWSPREVIOUS`) and supports rotation workflows. Labels alone do not make two database passwords valid: the target must support overlap, for example through alternating users or dual-password support; single-user rotation has different transition behavior. Applications that fetch the secret at runtime (with a short cache) pick up the new value without a redeploy. Applications that read a secret once at boot need a restart, which is a reason to prefer runtime fetching.

## Planned rotation versus emergency revocation

The overlap pattern suits *planned* rotation, when nothing suggests the current value is in the wrong hands. Once exposure is likely, the order changes, because the old credential may already be in an attacker's hands:

- **Exposed or probably exposed** (pushed to a repository, printed in a CI log, pasted in chat, held by a breached supplier, or found during an incident): revoke or disable it promptly, even if some consumers fail until they receive a replacement, then review logs for misuse.
- **Holder no longer trusted** (a departing administrator, an offboarded contractor or a decommissioned service): revoke that holder's credentials; rotate any shared passwords or keys that person could read.
- **During an intrusion**: rotating one stolen password early can alert an attacker who holds other footholds, so incident responders may time credential changes as part of a coordinated eviction, unless ongoing harm demands immediate action.
- **Routine schedule**: rotate on a regular cycle, mainly to prove the changeover works and to limit the life of copies nobody knows about.

Where possible, replace a static secret with a short-lived or federated credential, so less rotation is needed at all.

## Key takeaways
- Where overlap is supported, create, propagate, verify and then revoke.
- For an exposed credential, revoke first and accept some disruption; overlap is for planned changes.
- Secret-store version labels coordinate values; target database semantics determine what is accepted.
- Runtime fetching with a bounded cache and startup-only loading have different rollout requirements.

## Further reading
- [AWS rotation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html)
- [OWASP secrets management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
