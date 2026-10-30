---
id: rel-th-second-third-normal
title: Second normal form and partial dependence
level: intermediate
minutes: 3
sourceLesson: rel-th-normal-forms
summary: Second normal form: diagnosing attributes that depend on only part of a composite key.
---

This unit continues the shop design: an order line stores order id `oid`, product id `pid`, date `odate`, customer id `cid`, customer name `cname`, product name `pname`, current product price `price`, and quantity `qty`. An order has one customer and date; a product has one current name and price. One line per order and product is the business rule.

## Second normal form (2NF)

A relation is in 2NF when it is in 1NF and **no non-prime attribute depends on part of a candidate key**. (A **prime** attribute is one that belongs to some candidate key.)

```formula reference
X ↛ A
  for every X ⊂ K and every A ∉ P
where
K: any candidate key of the relation
X: a set of attributes that is part of K but not all of it
⊂: is a proper subset of: inside K, and smaller than K
A: a single attribute
P: the set of prime attributes: those that belong to at least one candidate key
∉: is not a member of; A ∉ P means A is non-prime
↛: does not functionally determine
In words: no non-prime attribute may be determined by only part of a candidate key.
```

In practice, a **partial dependency** needs a composite key: a single-attribute key has no smaller non-empty part. (The one technical exception is a non-prime column forced to hold a single constant value, which the empty set of attributes "determines"; the schemas here have none.) So the 2NF question to ask of a table is: *does any non-key fact depend on only some of the key's columns?*

OrderLine's key is the order/product pair, and each half determines attributes on its own:

```formula reference
oid → odate, cid, cname
pid → pname, price
where
→: functionally determines
oid, pid: the order id and product id, each one half of the key {oid, pid}
odate, cid, cname: the order date, customer id and customer name (oid reaches cname through cid)
pname, price: the product's name and current price
, (on the right of →): every listed attribute is determined, so oid → odate, cid, cname means oid determines all three
In words: the order id alone fixes the date and customer (and, through the customer, the customer's name); the product id alone fixes the product's name and price.
```

Both are partial dependencies. Fix them by moving each one into its own relation:

```
Order(oid, odate, cid, cname)
Product(pid, pname, price)
Line(oid, pid, qty)
```

Each order's date and customer are now stored once per order, and each product's name and price once per product. The line keeps only what genuinely needs both halves of the key: the quantity. Order still repeats a customer's name on every order they place; that is a different problem, which third normal form addresses next.

## Key takeaways

- 2NF forbids a non-prime attribute depending on a proper part of any candidate key.
- Separate order and product facts from order-line facts to remove partial dependencies.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [Fagin: multivalued dependencies and fourth normal form](https://research.ibm.com/publications/multivalued-dependencies-and-a-new-normal-form-for-relational-databases)
