---
id: secf-layers-defaults
title: Independent layers and safe defaults
level: intermediate
minutes: 3
sourceLesson: secf-principles
summary: Independent controls reduce shared failure paths.
---

## Defence in depth

No single control is perfect, so layer independent controls so an attacker has to beat several. A layered design should account for gaps and shared failure modes instead of assuming that several controls guarantee protection.

```
 attack --> | o | -> |  o| -> |o  | -X
            |   |    |   |    |   |
           WAF    authz   least
                  check   privilege
```

A typical web stack might layer:

1. Network: only ports 80 and 443 exposed; database in a private subnet.
2. Application: input validation, parameterised queries, ownership checks.
3. Identity: MFA, short-lived tokens.
4. Data: encryption at rest, with keys in a separate service.
5. Detection: alerting on unusual queries or data volumes.

The layers must be **independent**. Controls sharing a failure mode (a library, credential or administration path) can fail together for that threat, even if they provide different protections elsewhere. A WAF and the app both relying on the same regex for "safe input" fail together.

> [!warning] Depth is not an excuse for weak layers
> "It's behind the VPN" is not a reason to skip authentication on an internal tool. Treating the network perimeter as the only real layer is exactly what the **zero trust** model rejects: network location alone does not confer trust, and access decisions use the relevant identity, device and resource policy. This does not require a fresh interactive login for every request.

## Fail-safe defaults

> Base access decisions on permission rather than exclusion.

Start from **deny**, and grant explicitly. An allowlist ("these three roles may do this") fails safe when someone forgets to add an entry: the new role simply can't act. A denylist ("everyone except guests") fails dangerously when a new role is added and nobody updates the list.

```python
# Fails dangerously: new roles get access
def can_delete(user):
    return user.role not in {"guest"}

# Fails safe: new roles get no access
ALLOWED = {"admin", "owner"}
def can_delete(user):
    return user.role in ALLOWED
```

The same idea applies to error handling. If the call to the authorisation service times out, should the request be allowed? For a payments API, no: **fail closed**. Other systems may have a different safety or availability requirement. Physical exit and fire-containment design requires its own safety rules and is not specified here. Make the access-control failure policy explicit instead of letting an unhandled exception decide.

```python
def is_allowed(user, action):
    try:
        # Ask the policy at this decision
        # point.
        return policy.check(user, action)
    # Failure takes the denial branch.
    except Exception:
        log.exception("policy check failed")
        return False  # fail closed
```

## Key takeaways
- Independent controls reduce shared failure paths.
- Allow explicit actions and deny new roles by default.
- Choose failure behaviour deliberately, including the availability trade-off.

## Further reading
- [Saltzer and Schroeder: protection principles](https://www.cs.virginia.edu/~evans/cs551/saltzer/)
- [NIST SP 800-207: zero trust architecture](https://csrc.nist.gov/pubs/sp/800/207/final)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
