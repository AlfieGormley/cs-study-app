---
id: rel-th-anomalies-and-1nf
title: Anomalies and first normal form
level: intermediate
minutes: 4
sourceLesson: rel-th-normal-forms
summary: Anomalies and first normal form, with explicit examples and the conditions that make the reasoning valid.
---

Normalisation is the process of splitting a badly structured relation into smaller ones so that **each fact is stored once**. When a fact is stored in many rows, the copies can disagree unless additional constraints or coordinated writes keep them consistent.

Each normal form forbids one kind of redundancy, defined precisely with the functional dependencies (FDs) from the previous lesson. Kent’s informal summary says that non-key facts should depend on the key, its whole value, and no unrelated determinant. It is a mnemonic; the precise prime-attribute conditions in the following units handle cases the mnemonic misses.

The formula below states the business rules. Every card defines its notation locally; an arrow expresses a rule across all legal states, rather than a coincidence in these three rows.

## The problem: anomalies

A shop imports its order spreadsheet as a single table:

```
OrderLine
oid pid odate  cid cname pname  price qty
 10 P1  03-01  C7  Ann   Bolt   0.20  50
 10 P2  03-01  C7  Ann   Nut    0.10  50
 11 P1  03-02  C9  Raj   Bolt   0.20  10
```

The business rules, as FDs:

```formula
oid → odate, cid
cid → cname
pid → pname, price
{oid, pid} → qty
where
→: functionally determines: rows that agree on the left side must agree on the right side
oid: the order id
odate: the order date
cid: the customer id
cname: the customer's name
pid: the product id
pname: the product's name
price: the product's current price (this shop sets one current price per product)
qty: the quantity of that product on that order
, (on the right of →): both attributes are determined, so oid → odate, cid means oid → {odate, cid}
{ }: a set of attributes; {oid, pid} means "order and product together"
In words: an order has one date and one customer; a customer has one name; a product has one name and price; and the quantity belongs to an order and product together.
```

The only candidate key is the pair of order id and product id. Three kinds of trouble follow.

1. **Update anomaly.** Ann changes her name. It is stored on every line of every order she has placed, and an update that misses one leaves the data contradicting itself.
2. **Insertion anomaly.** You cannot record a new product until someone orders it, because `oid` is part of the key and cannot be NULL.
3. **Deletion anomaly.** Delete order 11, Raj's only order, and you lose the fact that customer C9 is called Raj.

All three come from FDs whose left side is not a key: the table is storing facts about customers and products inside rows about order lines.

## First normal form (1NF)

A relation is in 1NF when every attribute value is an **atomic relational value**: a single value from its domain, with no repeating groups.

```
Not 1NF
oid  products
 10  "P1:50, P2:50"
```

Ordinary column constraints and joins do not directly represent the individual items; string-splitting expressions or custom constraints are more complex than storing a row per item. The fix is one row per product per order, as in OrderLine above.

> [!note] What counts as atomic?
> Atomicity is relative to the chosen domains and relational presentation. Decomposability by a function does not alone violate 1NF: dates and text have inspectable parts. Under the classical flat-relation convention used here, a repeating collection of phone numbers or order lines is represented by separate relational tuples. SQL arrays and JSON are valid SQL values with useful operators, but calling them automatically in or out of 1NF merely because an application searches inside them is too broad. For this design, separate rows let each phone or line have ordinary keys, foreign keys and indexes.

## Key takeaways

- Mixing order, customer and product facts creates update, insertion and deletion anomalies.
- Use separate relational tuples for repeating phone or item facts under the flat relational convention.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [Fagin: multivalued dependencies and fourth normal form](https://research.ibm.com/publications/multivalued-dependencies-and-a-new-normal-form-for-relational-databases)
