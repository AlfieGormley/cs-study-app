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

## Key takeaways
- Where overlap is supported, create, propagate, verify and then revoke.
- Secret-store version labels coordinate values; target database semantics determine what is accepted.
- Runtime fetching with a bounded cache and startup-only loading have different rollout requirements.

## Further reading
- [AWS rotation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html)
- [OWASP secrets management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
