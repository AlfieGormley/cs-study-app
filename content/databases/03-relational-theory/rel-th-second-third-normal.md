---
id: rel-th-second-third-normal
title: Second normal form and partial dependence
level: intermediate
minutes: 3
sourceLesson: rel-th-normal-forms
summary: Second normal form and partial dependence, with complete worked examples and local definitions.
---

This unit continues the shop design: an order line stores order id `oid`, product id `pid`, date `odate`, customer id `cid`, customer name `cname`, product name `pname`, current product price `price`, and quantity `qty`. An order has one customer and date; a product has one current name and price. One line per order and product is the business rule.

## Second normal form (2NF)

A relation is in 2NF when it is in 1NF and **no non-prime attribute depends on part of a candidate key**. (A **prime** attribute is one that belongs to some candidate key.)

```formula
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

In the usual case with no constant non-prime attributes, a single-attribute candidate key has no non-empty proper part, so partial dependence needs a composite key. Formally the empty attribute set is also a proper subset; a non-prime attribute forced constant can therefore violate the fully general predicate even with a singleton key. The worked schemas have no such constant dependencies. OrderLine’s key is the order/product pair, and each half determines attributes on its own:

```formula
oid → odate, cid, cname
pid → pname, price
where
→: functionally determines
oid, pid: the order id and product id, each one half of the key {oid, pid}
odate, cid, cname: the order date, customer id and customer name (oid reaches cname through cid)
pname, price: the product's name and current price
In words: the order id alone fixes the date and customer; the product id alone fixes the product's name and price.
```

Both are **partial dependencies**. Fix them by moving each one into its own relation:

```formula
Order(oid, odate, cid, cname)
Product(pid, pname, price)
Line(oid, pid, qty)
where
Order: the relation of orders, with the attributes shown
Customer: the relation of customers
Product: the relation of products
Line: the relation of order lines
OrderLine: the original combined order-line relation
oid: order identifier
odate: order date
cid: customer identifier
cname: customer name
pid: product identifier
pname: product name
price: current product price, in pounds per item
qty: number of items ordered
In words: these are the headings after moving dependent customer and product facts into their own relations.
```

## Key takeaways

- 2NF forbids a non-prime attribute depending on a proper part of any candidate key.
- Separate order and product facts from order-line facts to remove partial dependencies.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [Fagin: multivalued dependencies and fourth normal form](https://research.ibm.com/publications/multivalued-dependencies-and-a-new-normal-form-for-relational-databases)
