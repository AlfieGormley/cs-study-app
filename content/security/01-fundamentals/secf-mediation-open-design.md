---
id: secf-mediation-open-design
title: Check every access with a simple, open design
level: intermediate
minutes: 3
sourceLesson: secf-principles
summary: A hidden button does not protect its API.
---

A good permission rule has little effect when one route bypasses it. Complete mediation concerns where and when checks happen; economy of mechanism and open design make the checks easier to assess.


## Complete mediation

> Every access to every object must be checked for authority.

Not just the first access, and not just the obvious path. Common violations:

- **Checking on the page, not the API.** The admin button is hidden in the UI, but `POST /api/admin/users` has no check.
- **Caching a permission decision** after the user's rights have been revoked.
- **Time-of-check to time-of-use (TOCTOU)**: a program checks that a file is safe, then opens it by name; an attacker swaps the file in between. Use appropriate credentials when opening the object and validate the opened object through its handle. A handle prevents that name-substitution race, but does not itself establish permission or make the object immutable.

Complete mediation is why a central authorisation layer (middleware or a policy service) beats scattered `if` statements: it is harder to forget one endpoint.

> [!analogy] Real-world analogy: the unmarked stage door
> A theatre checks tickets at the front entrance, but the stage door round the back is unmarked and unlocked. The managers assume nobody knows it is there.
>
> **How it maps:** The front-of-house check is the UI hiding an admin button; the stage door is an API endpoint with no check of its own. Complete mediation means checking at every door. Open design means the theatre should stay safe even when everyone knows where the stage door is.
>
> **Where it stops:** A theatre can post a guard at a door. Software needs the check in code on every path, including paths created by a cached permission or by a file changing between check and use, which have no simple physical equivalent.

## Economy of mechanism

Keep the security-relevant parts **small and simple**, so they can be reviewed and tested. Every extra feature in a login flow, parser or crypto library is extra attack surface. This is why security teams favour small, well-reviewed libraries over home-grown code, and why removing an unused feature is a security improvement.

## Open design

Security shouldn't depend on the attacker not knowing how the system works. This is **Kerckhoffs's principle** from 1883 cryptography: a cipher should be secure even if everything except the key is public.

Secrecy can still add a little friction (not publishing your internal network map is sensible), but "nobody knows the admin URL" is not a control. **Security through obscurity** fails the day the secret leaks, and it usually leaks.

## Key takeaways
- A hidden button does not protect its API.
- A checked path can change before it is used; reason about the opened object.
- Keep protection mechanisms small and secure when their design is public.

## Further reading
- [Saltzer and Schroeder: protection principles](https://www.cs.virginia.edu/~evans/cs551/saltzer/)
- [Linux access: real credentials and pathname races](https://man7.org/linux/man-pages/man2/access.2.html)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
