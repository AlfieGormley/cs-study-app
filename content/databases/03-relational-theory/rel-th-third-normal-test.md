---
id: rel-th-third-normal-test
title: Third normal form and indirect facts
level: intermediate
minutes: 3
sourceLesson: rel-th-normal-forms
summary: Third normal form and indirect facts, with complete worked examples and local definitions.
---

The shop has already separated order lines from product facts. Its remaining Order relation stores order identifier `oid`, order date `odate`, customer identifier `cid` and customer name `cname`. An order fixes its date and customer; a customer fixes one current name. The only candidate key of Order is its order identifier.

## Third normal form (3NF)

A relation is in 3NF when, for every non-trivial FD whose right side is a single attribute A, **either the left side X is a superkey or A is prime**:

```formula
for every X → A in F⁺ with A ∉ X:
  X⁺ = R  or  A ∈ P
where
F⁺: every FD that holds on the relation (all FDs implied by the given set F)
X: the left side, a set of attributes
A: the right side, a single attribute
→: functionally determines
∉: is not a member of; A ∉ X makes the FD non-trivial
X⁺: the attribute closure of X; X⁺ = R means X is a superkey
R: the set of all attributes of the relation
∈: is a member of
P: the set of prime attributes (those in some candidate key)
In words: every real dependency either comes from a superkey or points at a key attribute.
```

The Order relation containing order id, date, customer id and customer name is in 2NF under these rules (its only candidate key is the single order id) but still repeats Ann's name on every order. The cause is a **transitive dependency**:

```formula
oid → cid and cid → cname
cid⁺ = {cid, cname}
where
→: functionally determines
oid: the order id, the key of Order
cid: the customer id
cname: the customer's name
cid⁺: the attribute closure of cid within Order
{ }: a set of attributes
In words: the order fixes the customer, and the customer fixes the name, so the name hangs off the key only indirectly. cid reaches just cid and cname, not all of Order, so it is not a superkey.
```

`cid` is not a superkey of Order and `cname` is not prime, so 3NF is violated. Split again:

```formula
Order(oid, odate, cid)
Customer(cid, cname)
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

Now every FD's left side is a key of its relation. Ann's name lives in one row, products can exist before anyone orders them, and deleting an order loses nothing else.

> [!warning] Price is a different fact
> The current price of a product (one per product) can hold in every database state even when prices change over time. It does not imply that the price *paid* on every historical order line equals today's price. In a real shop, the price charged on an order is a separate fact from the current list price, and it belongs to the order and product together: the order id and product id together determine `price_paid`. Store it on `Line`. That is not denormalisation; it is modelling a time-dependent fact correctly. Normalising away the price paid is a classic bug that silently alters old invoices.

## Key takeaways

- 3NF checks every non-trivial singleton-right-side FD for a superkey determinant or prime result attribute.
- Customer name and historical price paid belong to different facts and require different determinants.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [Fagin: multivalued dependencies and fourth normal form](https://research.ibm.com/publications/multivalued-dependencies-and-a-new-normal-form-for-relational-databases)
