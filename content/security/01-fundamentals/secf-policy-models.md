---
id: secf-policy-models
title: Roles, attributes and relationships
level: intermediate
minutes: 3
sourceLesson: secf-access-control
summary: Roles group authority but still need appropriate object constraints.
---

## Role-based access control (RBAC)

In **RBAC**, permissions attach to **access-control roles**, and users are assigned roles.

```
users        roles          permissions
alice  --> [accountant] --> invoice:read
bob    --> [accountant] --> invoice:create
carol  --> [admin]     --> user:manage
                       --> invoice:read
```

Benefits: when someone changes job you change their role, not 40 individual permissions. Auditors can review "who has the admin role?". Roles can form hierarchies (a manager inherits everything an employee has), and the NIST RBAC standard adds **constraints** such as separation of duties: nobody may hold both "create supplier" and "approve payment".

Pitfalls:

- **Role explosion.** "Accountant, but only for the UK, but only for Q3" creates thousands of roles.
- **Coarse roles do not automatically enforce ownership.** A single customer role with invoice-read permission needs an object-level constraint. RBAC can include object-specific permissions and additional constraints; ABAC or ReBAC often expresses these relationships more conveniently.

## Attribute-based access control (ABAC)

**ABAC** evaluates rules over attributes of the subject, object, action and environment:

```python
def can_read(user, doc, ctx):
    # Every condition must hold together.
    return (
        doc.tenant_id == user.tenant_id
        and user.clearance >= doc.level
        # Ownership or the auditor role
        # suffices.
        and (doc.owner_id == user.id
             or "auditor" in user.roles)
        and 0 <= ctx.mfa_age_minutes < 60
    )
```

ABAC is expressive enough for ownership, tenancy, time and device posture. AWS IAM supports attribute-based conditions such as tags, source IP and MFA context alongside other policy mechanisms. The cost is that policies become code, and "who can access X?" gets hard to answer without evaluating every rule.

## Relationship-based access control (ReBAC)

Many products are really graphs: Alice is an editor of folder F, which contains document D, so Alice can edit D. **ReBAC** models permissions as relationships. Google's **Zanzibar** system (described in a 2019 paper) answers checks for Drive, YouTube and other services this way, storing relation tuples such as:

```
doc:D#parent@folder:F
folder:F#editor@user:alice
```

Rules then say "editors of a parent folder are editors of the document". Open-source systems such as OpenFGA and SpiceDB follow this design. ReBAC handles sharing and nested hierarchies naturally, while graph evaluation, consistency and policy maintenance add complexity. A dedicated service is one deployment choice, not a requirement of the model.

## Comparing the models

| Model | Who sets rules | Based on |
|---|---|---|
| DAC | Object owner | Identity, ownership |
| mandatory access control | Central policy | Labels, levels |
| RBAC | Administrators | Roles |
| ABAC | Policy authors | Attributes |
| ReBAC | Policy + users | Relationships |

Real systems mix them: RBAC for coarse capability ("is this a support agent?"), plus ABAC or ReBAC for the object-level check ("is this ticket in their region?").

## Key takeaways
- Roles group authority but still need appropriate object constraints.
- ABAC evaluates trusted attributes and context.
- ReBAC follows declared relationships and inheritance rules.

## Further reading
- [NIST Role Based Access Control project](https://csrc.nist.gov/projects/role-based-access-control)
- [NIST SP 800-162: ABAC](https://csrc.nist.gov/pubs/sp/800/162/upd2/final)
- [Zanzibar — Google Research](https://research.google/pubs/zanzibar-googles-consistent-global-authorization-system/)
