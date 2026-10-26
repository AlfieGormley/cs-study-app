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

A universal claim can be checked by searching for a counterexample: it holds exactly when no counterexample exists.

"Customers who have ordered **every** product" becomes a double `NOT EXISTS`:

For each customer, look for a product with no matching order. Keep the customer only when that search finds nothing.

```sql
SELECT c.id FROM customers c
WHERE NOT EXISTS (
  SELECT 1 FROM products p
  WHERE NOT EXISTS (
    SELECT 1 FROM orders o
    WHERE o.customer_id = c.id
      AND o.product_id = p.id));
```

This pattern is called **relational division**. Assume customer and product IDs are non-null keys and matching order IDs identify those keys. If the products table is empty, every customer is returned: vacuous truth again.

Ordinary SQL comparisons involving `NULL` produce UNKNOWN, and `WHERE` keeps only TRUE rows. Use `IS NULL` to test directly for the missing-value marker. `EXISTS` itself returns TRUE or FALSE according to whether its subquery returns any rows. De Morgan's laws still hold for SQL's three truth values; the difference from classical logic is that a condition and its negation can both be UNKNOWN.


## How far can you automate it?

For propositional logic, you can always decide whether a formula is valid by checking every row (slowly). First-order logic is different. Church and Turing proved in 1936 that no algorithm can decide validity for every first-order formula. Gödel's completeness theorem says every valid formula has a proof, so you can *search* for proofs, but the search may run forever on a formula that is not valid.

In practice, tools such as Z3 and the Dafny verifier handle large, useful parts of it automatically. The undecidability shows up as timeouts and "unknown" answers, especially around quantifiers.


## Key takeaways
- Double NOT EXISTS expresses the absence of a counterexample to a universal query.
- General first-order validity is undecidable even though valid formulas have finite proofs.

## Further reading
- [Open Logic Project](https://forallx.openlogicproject.org/)
- [PostgreSQL subquery expressions](https://www.postgresql.org/docs/current/functions-subquery.html)
- [PostgreSQL comparisons and NULL](https://www.postgresql.org/docs/current/functions-comparison.html)
- [PostgreSQL logical operators](https://www.postgresql.org/docs/current/functions-logical.html)
