---
id: secf-principles
title: Security design principles
level: intermediate
minutes: 11
summary: Least privilege, defence in depth, fail-safe defaults, complete mediation and the other Saltzer and Schroeder principles, with the real failures that show why they matter.
---

Specific vulnerabilities change every year. The principles that prevent them have barely changed since 1975, when Jerome Saltzer and Michael Schroeder published *The Protection of Information in Computer Systems*. Their list of eight design principles is still the backbone of how security engineers review a design.

This lesson covers those principles plus defence in depth, with the question each one asks of your system.

## Least privilege

> Every program and every user should operate using the least set of privileges necessary to complete the job.

The intuition: you can't prevent every compromise, so limit what a compromise can do. This is often described as limiting the **blast radius**.

```
Web app has broad database authority
  SQLi may read/alter/drop accessible data;
  extra role powers depend on the DB

Web app credentials: SELECT/INSERT on
  orders, SELECT on products
  SQLi may read orders/products,
  insert orders (still serious)
```

In practice least privilege means:

- **Service accounts scoped to one job.** The thumbnail worker gets read access to one bucket, not `s3:*`.
- **No standing admin rights.** Engineers request elevated access for a time-limited window (just-in-time access), which is logged.
- **Avoid unnecessary elevated execution.** Use an unprivileged service with a narrowly scoped binding mechanism where supported. If start-up needs elevation, drop the unneeded identities, groups and capabilities afterwards. Non-root containers still need appropriate capability and access controls.
- **Short-lived credentials** rather than long-lived keys, so a leaked token expires.

The hard part isn't the principle; it is keeping permissions tight over time. Permissions accrete: someone adds a wildcard to fix an outage and nobody removes it. Tools such as AWS IAM Access Analyzer compare granted permissions with those actually used.

> [!example] Capital One, 2019
> Capital One reported unauthorised access affecting approximately 100 million individuals in the US and six million in Canada. The company identified a configuration vulnerability. The exact exploit chain and the counterfactual claim that a narrower role would have made the incident minor are not established by the disclosure used here, so those details are omitted.

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

The same idea applies to error handling. If the authorisation service times out, should the request be allowed? For a payments API, no: **fail closed**. Other systems may have a different safety or availability requirement. Physical exit and fire-containment design requires its own safety rules and is not specified here. Make the access-control failure policy explicit instead of letting an unhandled exception decide.

```python
def is_allowed(user, action):
    try:
        return policy.check(user, action)
    except Exception:
        log.exception("policy check failed")
        return False  # fail closed
```

## Complete mediation

> Every access to every object must be checked for authority.

Not just the first access, and not just the obvious path. Common violations:

- **Checking on the page, not the API.** The admin button is hidden in the UI, but `POST /api/admin/users` has no check.
- **Caching a permission decision** after the user's rights have been revoked.
- **Time-of-check to time-of-use (TOCTOU)**: a program checks that a file is safe, then opens it by name; an attacker swaps the file in between. Use appropriate credentials when opening the object and validate the opened object through its handle. A handle prevents that name-substitution race, but does not itself establish permission or make the object immutable.

Complete mediation is why a central authorisation layer (middleware or a policy service) beats scattered `if` statements: it is harder to forget one endpoint.

## Economy of mechanism

Keep the security-relevant parts **small and simple**, so they can be reviewed and tested. Every extra feature in a login flow, parser or crypto library is extra attack surface. This is why security teams favour small, well-reviewed libraries over home-grown code, and why removing an unused feature is a security improvement.

## Open design

Security should not depend on the attacker not knowing how the system works. This is **Kerckhoffs's principle** from 1883 cryptography: a cipher should be secure even if everything except the key is public.

Secrecy can still add a little friction (not publishing your internal network map is sensible), but "nobody knows the admin URL" is not a control. **Security through obscurity** fails the day the secret leaks, and it usually leaks.

## Separation of privilege

A protection mechanism can require **two independent conditions**, so compromise of one condition is insufficient. Benefits depend on independence and correct enforcement. Examples:

- Two-person approval for production database changes or large payments.
- Multi-factor authentication (two independent proofs).
- Code review required before merge, enforced by branch protection.

Closely related is **separation of duties**: the person who raises a payment shouldn't be the person who approves it.

## Least common mechanism

Minimise mechanisms **shared** between users, because each shared mechanism is a channel for one user to affect another. A shared `/tmp` directory, a shared cache keyed only by URL, or a multi-tenant database without tenant isolation are all examples. Cache poisoning and cross-tenant data leaks often come down to this.

## Psychological acceptability

If security is painful, people work around it. Password rules that force monthly changes produce `Summer2025!`, `Autumn2025!`. A VPN that drops every ten minutes produces shadow IT. Good security is the easy path: passkeys instead of complex passwords, single sign-on instead of twenty logins.

## The principles together

| Principle | Question to ask |
|---|---|
| Least privilege | What's the blast radius? |
| Defence in depth | What if this layer fails? |
| Fail-safe defaults | What happens by default? |
| Complete mediation | Is every access checked? |
| Economy of mechanism | Can we review it all? |
| Open design | Secure if attackers read the code? |
| Separation of privilege | Can one person do it alone? |
| Least common mechanism | What do users share? |
| Psychological acceptability | Will people bypass it? |

> [!tip] The confused deputy
> A classic failure combining several principles: a privileged program (the deputy) is tricked into using its authority on behalf of a less privileged caller. Server-side request forgery is a modern example: the server fetches a URL the user supplies, using the server's own network access. Restrict what authority the deputy may exercise for each caller. For URL fetching, validate destinations and redirects, constrain network access and avoid exposing unnecessary credentials.

## Trade-offs

Principles conflict with each other and with delivery:

- Least privilege costs engineering time and causes outages when a needed permission is missing.
- Defence in depth adds latency, cost and complexity, which fights economy of mechanism.
- Fail-closed protects confidentiality and integrity at the cost of availability.

The skill is applying them in proportion to the value of what you protect.

## Key takeaways
- Least privilege limits blast radius; permissions must be reviewed because they accrete.
- Defence in depth needs independent layers; shared failure modes collapse them into one.
- Default to deny and allowlists; choose fail-closed or fail-open deliberately.
- Complete mediation means checking every access, including APIs, cached decisions and TOCTOU windows.
- Open design: do not depend on hiding the mechanism. Protect keys, credentials and sensitive data independently.

> [!note] Example limits
> Python permission and failure branches were exercised with test objects. The privileged C race example is a source-reviewed fragment, not an executed setuid program. Cloud policy and cache examples require deployment-specific configuration; they were not tested against live services.

## Further reading
- [The Protection of Information in Computer Systems — Saltzer and Schroeder](https://www.cs.virginia.edu/~evans/cs551/saltzer/)
- [Principle of least privilege — Wikipedia](https://en.wikipedia.org/wiki/Principle_of_least_privilege)
- [Defense in depth (computing) — Wikipedia](https://en.wikipedia.org/wiki/Defense_in_depth_(computing))
- [Kerckhoffs's principle — Wikipedia](https://en.wikipedia.org/wiki/Kerckhoffs%27s_principle)
- [Confused deputy problem — Wikipedia](https://en.wikipedia.org/wiki/Confused_deputy_problem)
