---
id: api-object-access-models
title: Object access with roles, attributes and relationships
level: advanced
minutes: 2
summary: Choose RBAC, ABAC or ReBAC while enforcing permission on every requested object.
sourceLesson: api-auth
---

## Authorisation models

Once you know who the caller is, decide what they can do.

## RBAC: role-based

Users get **access-control roles**; each role has **API permissions**.

```
alice -> [editor]
editor -> posts:read, posts:write
viewer -> posts:read
```

Simple, auditable and good enough for most internal tools. It strains when permissions depend on context: "editors can edit posts *in their own department*, *during business hours*". Teams end up with role explosion: `editor-uk`, `editor-uk-weekend`...

## ABAC: attribute-based

Decisions are policies over **access-control attributes** of the user, the resource, the action and the environment:

```pseudocode
# Check context and object attributes.
allow if
  user.dept == resource.dept
  and action == "edit"
  and resource.status != "locked"
```

More expressive, but harder to audit ("who can see this document?" requires evaluating policies). Tools such as Open Policy Agent (Rego) and AWS IAM policies are ABAC-style.

## ReBAC: relationship-based

Permissions follow relationships in a graph: "you can view this doc because you're in a group that has access to the folder that contains it". Google's **Zanzibar** (behind Drive, YouTube, Calendar) is the canonical example; OpenFGA and SpiceDB are open-source implementations.

| Model | Best for |
|---|---|
| RBAC | Simple apps, admin tools |
| ABAC | Context-dependent rules |
| ReBAC | Sharing, hierarchies |

Whatever the model, **enforce authorisation on the server for every object**, not just at login, and not just by hiding buttons in the UI.

## Key takeaways
- RBAC groups permissions into roles but can multiply roles for contextual rules.
- ABAC evaluates attributes and environment; ReBAC follows sharing and hierarchy relationships.
- Check object access on the server on every request; a valid token and hidden buttons are insufficient.

## Further reading
- [OWASP API Security Top 10: Broken object level authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/)
- [Google Research: Zanzibar](https://research.google/pubs/zanzibar-googles-consistent-global-authorization-system/)
- [NIST: Attribute based access control](https://csrc.nist.gov/projects/attribute-based-access-control)
