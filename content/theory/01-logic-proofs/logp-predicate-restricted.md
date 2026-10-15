---
id: logp-predicate-restricted
title: Translating every and some correctly
level: basic
minutes: 3
sourceLesson: logp-predicate
summary: Restricted universal claims use an implication so non-members do not violate the rule.
---

## Translating English

Most real statements quantify over *some* of the domain: "every admin", "some order". These **restricted quantifiers** have a fixed shape, and getting it wrong is the most common error in the whole subject. Over a domain of users:

```formula
∀u (Admin(u) → Verified(u))
∃u (Admin(u) ∧ Verified(u))
where
u: a variable ranging over all users
Admin(u): the predicate "u is an admin"
Verified(u): the predicate "u is verified"
∀: for all users
∃: there exists at least one user
→: implies: "if ... then ...", false only when the left side is true and the right side false
∧: AND: true only when both sides are true
In words: "every user, if an admin, is verified" (every admin is verified) and "some user is both an admin and verified" (some admin is verified).
```

The four common patterns (not is NOT):

| English | Formula |
|---|---|
| Every admin is verified | for every u (Admin(u) implies Verified(u)) |
| Some admin is verified | there exists u (Admin(u) and Verified(u)) |
| No admin is verified | for every u (Admin(u) implies not Verified(u)) |
| Not every admin is verified | there exists u (Admin(u) and not Verified(u)) |

For these restricted-domain translations, use implication under ∀ and conjunction under ∃. This is not a restriction on which connectives may appear in quantified formulas.

> [!warning] The two classic mistranslations
> - for every u (Admin(u) and Verified(u)) says *everyone* is an admin and verified. Far too strong.
> - there exists u (Admin(u) implies Verified(u)) is true as soon as there is a single non-admin, because the implication is then vacuously true. Far too weak.

In code the same shapes appear naturally. These are expressions to use with a finite iterable `users`; each account object must have Boolean `admin` and `verified` attributes. They produce Boolean results and do not print them:

```python
# Filtering ignores non-admin accounts.
all(u.verified for u in users
    if u.admin)

# One verified admin supplies a witness.
any(u.admin and u.verified
    for u in users)
```

The `if` filter in a comprehension plays the role of the →.


## Key takeaways
- Restricted universal claims use an implication so non-members do not violate the rule.
- Restricted existential claims require membership and the desired property together.

## Further reading
- [Open Logic Project](https://forallx.openlogicproject.org/)
- [Quantifier (logic) — Wikipedia](https://en.wikipedia.org/wiki/Quantifier_(logic))
