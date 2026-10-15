---
id: secf-shared-authority-usability
title: Shared authority, separation and usable controls
level: intermediate
minutes: 3
sourceLesson: secf-principles
summary: Independent conditions and separate approvers limit unilateral misuse.
---

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

> [!note] Example limits
> Python permission and failure branches were exercised with test objects. The privileged C race example is a source-reviewed fragment, not an executed setuid program. Cloud policy and cache examples require deployment-specific configuration; they were not tested against live services.

## Key takeaways
- Independent conditions and separate approvers limit unilateral misuse.
- Shared caches and privileged deputies need caller-specific authority.
- Usability and engineering costs affect whether controls work in practice.

## Further reading
- [Saltzer and Schroeder: protection principles](https://www.cs.virginia.edu/~evans/cs551/saltzer/)
- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [NIST SP 800-63B-4: authentication](https://pages.nist.gov/800-63-4/sp800-63b.html)
