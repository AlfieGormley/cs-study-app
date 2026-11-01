---
id: sea-layer-responsibilities
sourceLesson: sea-layered
title: Layer responsibilities and tangled views
level: basic
minutes: 4
summary: Recognise separate presentation, application, domain and data concerns and diagnose an unsafe mixed view.
---

Open a small web app written in a hurry and you often find one function that parses the HTTP request, checks the user's permissions, applies a discount rule, writes SQL and formats the JSON response. It works. Then someone asks for the same discount rule in a nightly batch job, and there is no way to call it without faking an HTTP request.

**Layered architecture** is a common answer to this. You split the code by *kind of concern* into horizontal layers, and you only let each layer talk to the ones beneath it.

## The classic layers

Most descriptions use three or four layers. Martin Fowler's *presentation, domain, data* split is the core; many teams add an **application layer** (or service layer) between presentation and domain.

```
 +--------------------------------+
 | Presentation                   |
 | HTTP views, CLI, templates     |
 +--------------------------------+
 | Application / service          |
 | use cases, transactions, auth  |
 +--------------------------------+
 | Domain                         |
 | business rules and concepts    |
 +--------------------------------+
 | Data / infrastructure          |
 | SQL, ORM, files, external APIs |
 +--------------------------------+
   calls go downwards only
```

Here “auth” means authorization: checking whether the caller may perform the requested use case.

| Layer | Answers | Knows nothing about |
|---|---|---|
| Presentation | How do users talk to us? | SQL, tables |
| Application | What can users do? | HTTP, JSON |
| Domain | What are the rules? | HTTP, storage |
| Data | Where is it stored? | Who called |

The point of the split is that each layer changes for a different reason. A redesign of the JSON format touches presentation. A new VAT rule touches the domain. Moving from MySQL to Postgres touches data. Separating those concerns usually keeps such changes smaller, though not always: a new feature, or a database that behaves differently, can still reach across several layers.

> [!analogy] Real-world analogy: a newspaper's departments
> A newspaper has a layout desk that decides how pages look, editors who decide which stories run today, reporters' facts and the paper's style rules, and a printing plant. A front-page redesign doesn't change the facts, and switching to a new printer doesn't change editorial policy.
>
> **How it maps:** Layout is presentation, the editors' daily choices are the application layer, facts and house rules are the domain, and the printing plant is the data layer. The plant prints what it's given and never decides what goes on the front page, just as the data layer never decides how a discount works.
>
> **Where it stops:** People in a newsroom talk freely in every direction and adapt as they go. In code, layering is a rule about which module may import which, and it only holds if a check enforces it. Some changes, like a new section of the paper, still involve every department.

## The one rule: dependencies point down

A layer may depend on layers below it, never on one above. The version used here lets a layer skip downwards past its neighbour, which is called relaxed layering; a later unit compares it with strict layering, where each layer may use only the one directly below. Either way, the domain never imports a Flask request, and the data layer never decides how a discount works.

This intentionally broken Flask fragment assumes an existing app, request and database connection. It shows the problem before separating responsibilities:

```python
@app.post("/orders/<int:oid>/discount")
def apply_discount(oid):
    code = request.json["code"]
    row = db.execute(
        "SELECT total, status FROM orders"
        " WHERE id = ?", (oid,)).fetchone()
    # Closed orders must not be discounted.
    if row["status"] != "open":
        return {"error": "closed"}, 409
    if code == "SPRING10":
        # Unknown codes leave new
        # unassigned.
        new = row["total"] * 0.9
    db.execute(
        "UPDATE orders SET total = ?"
        " WHERE id = ?", (new, oid))
    return {"total": new}
```

There are several problems here. The discount rule lives in a view, so the batch job can't reuse it. Testing it needs a web client and a database. An unknown code even crashes with `UnboundLocalError`, because `new` is never assigned, and Flask turns that into a 500 error. And with a numeric total, `* 0.9` produces a float, an inexact type for money, which is then written back to the table.

## Key takeaways
- Layers group code by kind of concern so changes can stay local.
- A downward dependency rule forbids a lower layer importing a higher one.
- Mixing request handling, rules and SQL makes reuse and isolated tests harder.

## Further reading
- [Presentation Domain Data Layering — Martin Fowler](https://martinfowler.com/bliki/PresentationDomainDataLayering.html)
- [Service Layer — Martin Fowler](https://martinfowler.com/eaaCatalog/serviceLayer.html)
