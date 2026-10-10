---
id: secf-access-control
title: Access control models
level: intermediate
minutes: 13
summary: DAC, MAC (Bell–LaPadula and Biba), RBAC, ABAC and relationship-based access control, ACLs versus capabilities, and why broken access control tops the OWASP list.
---

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

## Discretionary access control (DAC)

In **DAC** the **owner** of an object decides who can access it. Unix file permissions are the classic example:

```
$ ls -l report.txt
-rw-r----- 1 alice finance report.txt
 |  |  |
 |  |  other: ---  (no access)
 |  group finance: r--
 owner alice: rw-
```

The permission bits are often written in **octal** (base 8), one digit per class. Each class has three on/off bits, and three bits can count from 0 to 7, which is exactly one octal digit. Read is worth 4, write 2 and execute 1:

```formula
d = 4 × r + 2 × w + 1 × x
d_owner = 4 × 1 + 2 × 1 + 1 × 0 = 6
d_group = 4 × 1 + 2 × 0 + 1 × 0 = 4
d_other = 4 × 0 + 2 × 0 + 1 × 0 = 0
where
d: one octal digit of the mode, from 0 to 7, for one class (owner, group or other)
r: 1 if the class may read (an r in the string), 0 if not (a -)
w: 1 if the class may write (a w), 0 if not
x: 1 if the class may execute (an x), 0 if not
d_owner: the owner's digit for rw-
d_group: the group's digit for r--
d_other: the digit for everyone else, for ---
4: the place value of the read bit; 2 and 1 are the place values of the write and execute bits, the base-2 place values of the bit patterns 100, 010 and 001
In words: add 4 for read, 2 for write and 1 for execute in each class, so rw-r----- becomes the digits 6, 4 and 0.
```

So `rw-r-----` is set with `chmod 640`. Going the other way, 7 is `rwx`, 5 is `r-x` and 0 is no access.

For ordinary users and these mode bits alone, without extended ACLs or overriding privileges, Unix checks the classes **in order and stops at the first class that matches**: if you're the owner, only the owner bits apply; else if you're in the group, the group bits; else other. So with `chmod 604`, the owner can read and write, any *other* user can read, but members of the group cannot read, because they match the group class first and stop there.

DAC is flexible and intuitive. Its weakness: any program you run acts with your authority, so malware (or a confused user) can share your files with anyone. The owner's discretion is the attacker's discretion.

## Mandatory access control (MAC)

In **MAC** a central policy, not the owner, decides. Users can't override it even for their own files. MAC came from military systems with classification levels (Unclassified < Confidential < Secret < Top Secret).

### Bell–LaPadula: confidentiality

The Bell–LaPadula model constrains confidentiality-related information flows. In this simplified level-only explanation, assume subjects operate at the named level and have no trusted declassification exception:

- **Simple security property: no read up.** A Secret-cleared subject can't read Top Secret.
- **Star property: no write down.** A Secret subject can't write to a Confidential object.

The second rule is the clever one. Without it, a Trojan horse running with Secret clearance could copy Secret data into an Unclassified file.

### Biba: integrity

The **strict integrity** form associated with Biba reverses these directional rules to protect integrity:

- **No read down**: a high-integrity process mustn't consume low-integrity data, which could corrupt it.
- **No write up**: a low-integrity subject mustn't modify high-integrity objects.

```
          Bell-LaPadula    Biba
          (secrecy)        (integrity)
read      no read UP       no read DOWN
write     no write DOWN    no write UP
```

Windows Mandatory Integrity Control normally enforces **no write up** through integrity labels and policy; it is not an implementation of all strict Biba rules. SELinux and AppArmor can confine processes, including root processes, under enforced policies. Actual access also depends on policy configuration and trusted administrative powers.

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
    return (
        doc.tenant_id == user.tenant_id
        and user.clearance >= doc.level
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
| MAC | Central policy | Labels, levels |
| RBAC | Administrators | Roles |
| ABAC | Policy authors | Attributes |
| ReBAC | Policy + users | Relationships |

Real systems mix them: RBAC for coarse capability ("is this a support agent?"), plus ABAC or ReBAC for the object-level check ("is this ticket in their region?").

## Broken access control in practice

A missing object-level check is an important failure mode. **Insecure direct object reference (IDOR)**:

These are alternative handler sketches, not two routes to register together. Framework, database, response serialisation and login setup are omitted.

```python
# Vulnerable: authenticated, not authorised
@app.get("/invoices/<int:inv_id>")
@login_required
def get_invoice(inv_id):
    return db.invoices.get(inv_id)

# Fixed: object-level check
@app.get("/invoices/<int:inv_id>")
@login_required
def get_invoice(inv_id):
    inv = db.invoices.get(inv_id)
    if inv is None or \
       inv.customer_id != current_user.id:
        abort(404)
    return inv
```

Returning the same 404 for missing and inaccessible invoices avoids disclosing existence through that status distinction alone. Timing, response bodies and other endpoints may still reveal it. Note that random, unguessable IDs (UUIDs) make IDOR harder to *find* but don't fix it; that would be relying on obscurity.

> [!tip] Enforce centrally, deny by default
> Put authorisation in one layer (middleware, a policy engine, or row-level security in the database) and verify that every applicable path actually uses it. Write tests that log in as user A and request user B's objects, for every endpoint.

Other common failures:

- **Vertical escalation**: a normal user calls an admin endpoint.
- **Mass assignment**: the API binds a request body straight onto the model, so `{"role": "admin"}` in a profile update works.
- **Multi-tenant leaks**: a query missing `WHERE tenant_id = ?`.
- **Stale permissions**: a user removed from a project keeps access through a cached token.

## Key takeaways
- Access control decides subject + action + object; ACLs store it per object, capabilities per subject.
- DAC lets owners decide (Unix permissions); MAC enforces central labels that owners can't override.
- Bell–LaPadula protects secrecy (no read up, no write down); Biba protects integrity (no read down, no write up).
- Coarse roles need object-level constraints; RBAC can include such constraints, while ABAC and ReBAC provide useful modelling approaches.
- Missing object-level checks cause IDOR; enforce policy consistently and test cross-user access.

> [!note] Scope and execution
> The directional models omit compartments, trusted exceptions and formal proofs. Python access checks are illustrative and assume trustworthy context; the web handlers omit a full application. No live AWS, Windows MIC, database RLS or ReBAC service was deployed for this lesson review.

## Further reading
- [Authorization Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [A01:2021 Broken Access Control — OWASP Top 10](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
- [Bell–LaPadula model — Wikipedia](https://en.wikipedia.org/wiki/Bell%E2%80%93LaPadula_model)
- [Role-based access control — Wikipedia](https://en.wikipedia.org/wiki/Role-based_access_control)
- [Zanzibar: Google's Consistent, Global Authorization System](https://research.google/pubs/zanzibar-googles-consistent-global-authorization-system/)
- [Capability-based security — Wikipedia](https://en.wikipedia.org/wiki/Capability-based_security)
