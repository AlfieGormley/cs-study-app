---
id: logp-predicate-sql
title: Universal SQL queries and automation limits
level: basic
minutes: 3
sourceLesson: logp-predicate
summary: Double NOT EXISTS expresses the absence of a counterexample to a universal query.
---

## Quantifiers in SQL

SQL has existence tests through EXISTS and quantified comparisons through ALL. It has no standalone FOR ALL quantifier for arbitrary predicates, so universal queries use the negation law:

```formula
∀x P(x) ≡ ¬∃x ¬P(x)
where
x: a variable ranging over the domain (here, rows of a table)
P(x): a predicate, true or false for each x
∀: for all
∃: there exists at least one (SQL `EXISTS`)
¬: NOT (SQL `NOT`)
≡: is logically equivalent to
In words: "everything has P" means "there is nothing without P".
```

"Customers who have ordered **every** product" becomes a double `NOT EXISTS`:

```formula
∀p ∃o Ord(c, p, o)
  ≡ ¬∃p ¬∃o Ord(c, p, o)
where
c: the customer being tested
p: a variable ranging over products
o: a variable ranging over orders
Ord(c, p, o): the predicate "o is an order by customer c for product p"
∀: for all
∃: there exists at least one
¬: NOT
≡: is logically equivalent to
In words: "c ordered every product" means "there is no product that c has no order for".
```

```sql
SELECT c.id FROM customers c
WHERE NOT EXISTS (
  SELECT 1 FROM products p
  WHERE NOT EXISTS (
    SELECT 1 FROM orders o
    WHERE o.customer_id = c.id
      AND o.product_id = p.id));
```

This pattern is called **relational division**. If the products table is empty, every customer is returned: vacuous truth again.


## How far can you automate it?

For propositional logic, you can always decide whether a formula is valid by checking every row (slowly). First-order logic is different. Church and Turing proved in 1936 that no algorithm can decide validity for every first-order formula. Gödel's completeness theorem (1929) says every valid formula has a proof, so you can *search* for proofs, but the search may run forever on a formula that is not valid.

In practice, tools such as Z3 and the Dafny verifier handle large, useful parts of it automatically. The undecidability shows up as timeouts and "unknown" answers, especially around quantifiers.


## Key takeaways
- Double NOT EXISTS expresses the absence of a counterexample to a universal query.
- General first-order validity is undecidable even though valid formulas have finite proofs.

## Further reading
- [Open Logic Project](https://forallx.openlogicproject.org/)
