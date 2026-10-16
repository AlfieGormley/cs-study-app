---
id: rel-th-legal-keys
title: Choosing keys from legal states
level: basic
minutes: 2
sourceLesson: rel-th-relational-model
summary: Choosing keys from legal states, with explicit examples and the conditions that make the reasoning valid.
---

## Keys

A relation has no duplicate relational tuples, so the full set of attributes always identifies a relational tuple uniquely. Usually a smaller set does too.

- A **superkey** is any set of attributes whose values are unique across every relational tuple the relation could legally contain.
- A **candidate key** is a *minimal* superkey: remove any attribute and it stops being unique.
- The **primary key** is the candidate key you choose as the main way to identify relational tuples. The others are **alternate keys**, normally enforced in SQL with UNIQUE plus NOT NULL on their attributes.

Consider employees described by identifier `emp_id`, email address `email`, personal `name` and department `dept`. The domain guarantees that each identifier and each email belongs to only one employee:

| Attribute set | Superkey? | Candidate key? |
|---|---|---|
| identifier alone | Yes | Yes |
| email alone | Yes | Yes |
| identifier and name together | Yes | No, not minimal |
| name and department together | No | No |

> [!tip] Keys are about rules, not current data
> A key is a claim about *every legal state* of the relation, not the rows you happen to have. If today no two employees share a name, the name alone is still not a key, because the business allows two people called Sam. Keys come from the domain, and you find them by asking "can this ever repeat?"

## Key takeaways

- A candidate key is a superkey minimal under inclusion.
- Choose keys from rules for every legal state, not uniqueness in a sample.

## Further reading

- [Codd: A Relational Model of Data (1970)](https://www.seas.upenn.edu/~zives/03f/cis550/codd.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
