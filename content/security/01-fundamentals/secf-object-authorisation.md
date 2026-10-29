---
id: secf-object-authorisation
title: Enforce authorisation on each object
level: intermediate
minutes: 3
sourceLesson: secf-access-control
summary: Authentication and unpredictable IDs do not replace ownership checks.
---

An authenticated caller still needs permission for the exact resource requested. Object authorisation is where the earlier permission models become an enforceable application decision.


## Broken access control in practice

A missing object-level check is an important failure mode. In an **insecure direct object reference (IDOR)**, an endpoint fetches an object using an ID taken from the request without checking that the caller may access that object. Any logged-in user can then change the ID and read someone else's data.

The two handlers below are alternative sketches of one route, not two routes to register together. Framework, database, response serialisation and login setup are omitted.

```python
# Vulnerable: authenticated, not authorised
@app.get("/invoices/<int:inv_id>")
@login_required
def get_invoice(inv_id):
    # Login alone leaves ownership
    # unchecked.
    return db.invoices.get(inv_id)

# Fixed: object-level check
@app.get("/invoices/<int:inv_id>")
@login_required
def get_invoice(inv_id):
    # Fetch once, then check this exact
    # object.
    inv = db.invoices.get(inv_id)
    if inv is None or \
       inv.customer_id != current_user.id:
        # Hide the missing/forbidden
        # distinction.
        abort(404)
    return inv
```

Returning the same 404 for missing and inaccessible invoices avoids disclosing existence through that status distinction alone. Timing, response bodies and other endpoints may still reveal it. Note that random, unguessable IDs (UUIDs) make IDOR harder to *find* but don't fix it; that would be relying on obscurity.

> [!analogy] Real-world analogy: a cloakroom attendant
> At a theatre cloakroom, being in the audience does not entitle you to any coat. A careful attendant checks that the coat you ask for is the one you handed in.
>
> **How it maps:** Being inside the theatre is authentication. Checking that the coat is yours is the object-level authorisation check. An IDOR is an attendant who hands over whichever peg number you call out to anyone with a ticket for the show.
>
> **Where it stops:** Peg numbers are like invoice IDs: making them hard to guess does not fix an attendant who never checks ownership. Software also has no memory of faces; the server must look up the object's owner and compare it with the authenticated account on every request.

> [!tip] Enforce centrally, deny by default
> Put authorisation in one layer (middleware, a policy engine, or row-level security in the database) and verify that every applicable path actually uses it. Write tests that log in as user A and request user B's objects, for every endpoint.

Other common failures:

- **Vertical escalation**: a normal user calls an admin endpoint.
- **Mass assignment**: the API binds a request body straight onto the model, so `{"role": "admin"}` in a profile update works.
- **Multi-tenant leaks**: a query missing `WHERE tenant_id = ?`.
- **Stale permissions**: a user removed from a project keeps access through a cached token.

### Tenant isolation and database policy

Application checks must use a trustworthy tenant context, not a tenant ID chosen freely in the request. A data-access layer can require that context before constructing queries. Restrict direct database calls through review and tooling so endpoints cannot casually bypass it.

PostgreSQL row-level security can apply policy to rows even when an application query forgets its tenant filter. That requires appropriate roles, enabled policies and trustworthy context. Superusers and roles with BYPASSRLS bypass those policies; table owners normally do unless row security is forced. Whole-table operations such as TRUNCATE are outside row filtering. A connection pool must not leak one request's tenant setting into another request.

Cross-tenant integration tests then exercise the complete path: authenticate as tenant A, request tenant B's objects and check that reads and writes are rejected. Tests reveal regressions in the cases exercised; they do not enforce production isolation themselves. Wiki reminders and unpredictable IDs cannot repair a missing permission check.

## Key takeaways
- Authentication and unpredictable IDs do not replace ownership checks.
- An indistinguishable 404 hides one existence signal, not all signals.
- Test tenant isolation, mass assignment and revoked access.

## Further reading
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [PostgreSQL row security policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [OWASP Top 10:2025: Broken Access Control](https://owasp.org/Top10/2025/A01_2025-Broken_Access_Control/)
