---
id: rel-th-subtype-mappings
title: Mapping subtypes to tables
level: advanced
minutes: 3
sourceLesson: rel-th-er-modelling
summary: Mapping subtypes to tables, with explicit examples and the conditions that make the reasoning valid.
---

## Inheritance: specialisation and generalisation

Sometimes entities share most attributes but differ in some: a `Payment` is either a `CardPayment` (card token, last four digits) or a `BankTransfer` (sort code, reference). The ER model calls this specialisation. Subtypes can be **disjoint subtypes** (at most one subtype; exactly one only when also total) or **overlapping subtypes**, and specialisation can be **total** (every payment is some subtype) or **partial**.

For portable relational schemas, choose one of three mappings. PostgreSQL also has native table inheritance, with different semantics and limitations; the mappings here do not rely on it. They are named in Martin Fowler's *Patterns of Enterprise Application Architecture*:

| Mapping | Tables | Main cost |
|---|---|---|
| Single table | one, with type column | many NULLs |
| Class table | parent + one per subtype | joins |
| Concrete table | one per subtype | no key common to all subtypes |

**Single-table inheritance** puts every column in one table with a `kind` discriminator. It is fast and simple, but subtype columns must be nullable, so declare kind NOT NULL and use CHECK constraints to keep them coherent:

```sql
CHECK (
  (kind = 'card'
   AND card_last4 IS NOT NULL
   AND sort_code IS NULL)
  OR
  (kind = 'bank'
   AND sort_code IS NOT NULL
   AND card_last4 IS NULL))
```

**Class-table inheritance** has `payment(payment_id, amount, ...)` plus `card_payment(payment_id PRIMARY KEY REFERENCES payment, ...)`. No NULL columns and clean constraints, at the cost of a join to load a whole payment.

**Concrete-table inheritance** has a full table per subtype. Queries over "all payments" need `UNION ALL`, and nothing enforces unique ids across the tables.

## Enforcing subtype membership

A subtype primary key that is also a foreign key ensures each subtype row has a parent and appears at most once in that subtype table. It does not ensure that each parent has a subtype, or that the same parent cannot appear in both card and bank tables. For disjoint membership, a parent discriminator plus matching composite foreign keys can prevent the wrong subtype; total participation still needs a suitable creation/deletion protocol or deferred constraint trigger. Choose the constraint strategy along with the table mapping. Avoid presenting class tables alone as an automatic enforcement of “exactly one subtype”.

## Key takeaways

- Single, class and concrete tables make different nullability and query trade-offs.
- Parent/subtype foreign keys alone do not ensure total, disjoint membership.

## Further reading

- [Chen: The Entity-Relationship Model (1976)](https://openlib.org/home/krichel/courses/lis512/readings/chen76theentity-relationship.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
- [Fowler: Class Table Inheritance](https://martinfowler.com/eaaCatalog/classTableInheritance.html)
- [Fowler: Single Table Inheritance](https://martinfowler.com/eaaCatalog/singleTableInheritance.html)
- [Fowler: Concrete Table Inheritance](https://martinfowler.com/eaaCatalog/concreteTableInheritance.html)
