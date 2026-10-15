---
id: secf-permission-matrix
title: Permission matrices, ACLs and capabilities
level: intermediate
minutes: 3
sourceLesson: secf-access-control
summary: An access decision concerns a subject, action and object.
---

Use an access decision to separate the caller, the operation and the resource. This unit introduces the representation; later units add owner-controlled permissions, mandatory labels and policy rules.


Once a system knows *who* you are, it must decide *what you may do*. That decision, made millions of times a day, is **access control** (authorisation). Broken access control is the number one category in the OWASP Top 10 (2021), ahead of injection.

Every access control decision has the same shape:

```
subject  + action + object  -> allow/deny
(alice)    (read)   (payslip-42)
```

The models differ in **who sets the rules** and **what the rules are based on**.

## The access control matrix

The theoretical starting point is a matrix: rows are subjects, columns are objects, cells are permitted actions.

| | payroll.xlsx | roadmap.doc | printer |
|---|---|---|---|
| alice | read, write | read | print |
| bob | none | read, write | print |
| carol | read | none | none |

A large matrix is often sparse, so systems commonly represent permissions through per-object lists or subject-held authority rather than a dense table:

- **Access control lists (ACLs)** store each **column** with its object: "payroll.xlsx: alice rw, carol r". File systems, S3 bucket policies and most databases work this way. Easy to answer "who can access this file?"; hard to answer "what can Alice access?".
- **Capabilities** (capability lists) store each **row** with the subject: Alice holds unforgeable tokens, each naming an object and rights. Can support delegation and narrow rights, but neither is automatic; revocation depends on the design. A Unix file descriptor, a signed pre-authorised URL and an OAuth access token are all capability-like.

## Key takeaways
- An access decision concerns a subject, action and object.
- ACLs organise permissions by object.
- Capability-like authority depends on token design and revocation rules.

## Further reading
- [Saltzer and Schroeder: protection principles](https://www.cs.virginia.edu/~evans/cs551/saltzer/)
- [RFC 4949: security terms and models](https://www.rfc-editor.org/rfc/rfc4949)
- [OWASP Top 10 2021: Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
