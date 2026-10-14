---
id: db-document-aggregate-bounds
title: Document aggregates and bounded growth
level: basic
minutes: 3
summary: Choose embedded or referenced data and keep growing arrays below document and workload limits.
sourceLesson: db-nosql-families
---

A document groups data that belongs together. The useful boundary is a bounded aggregate that can be read and updated as a unit, rather than an ever-growing container for all history.

## Document stores

A document store keeps self-contained, nested documents, usually JSON or BSON. Unlike a key-value store, the database understands the structure, so it can index and query fields inside the document.

```json
{
  "_id": "order-981",
  "customer": { "id": 42, "name": "Priya" },
  "lines": [
    { "sku": "KET-1", "qty": 1,
      "price_p": 2999 },
    { "sku": "MUG-4", "qty": 2,
      "price_p": 899 }
  ],
  "status": "paid"
}
```

- **Examples**: MongoDB, Couchbase, Firestore, and Postgres's own `jsonb` columns.
- **Cheap**: loading a whole aggregate (an order with its lines) in one read, without joins. Flexible schemas can ease evolution, but incompatible shape changes still need validation, migration or reader compatibility.
- **Expensive**: many-to-many relationships and cross-document joins. MongoDB has `$lookup`, but it's not what the engine is optimised for.

The modelling rule is *embed what you read together, reference what you share*. Order lines belong inside the order. A product shared by thousands of orders should be referenced by id, not copied everywhere.

Also keep embedded arrays *bounded*. A MongoDB document is capped at 16 MiB; an ever-growing array increases size and processing pressure, although updates and replication can use deltas rather than rewriting/transmitting the whole document. The **bucket pattern** fixes this: one document per device per hour, say, each holding that hour's readings.

> [!warning] Schemaless isn't schema-free
> The schema still exists; it has moved into your application code. Every reader must handle every historical shape of the document. MongoDB's JSON Schema validation can put some of it back in the database.

## Transactions and arbitrary relationships

MongoDB supports multi-document transactions, so "NoSQL" does not mean transactions are impossible. However, a new workload dominated by arbitrary joins and multi-entity updates can be simpler to model in a relational store. Compare the workload and complexity rather than assuming a missing product feature.

## Key takeaways
- Embed bounded data read with one aggregate; reference shared entities.
- Flexible documents still need schema compatibility and validation.
- Time buckets bound growing arrays; arbitrary joins and multi-entity updates can favour relational modelling.

## Further reading
- [MongoDB: Data modeling](https://www.mongodb.com/docs/manual/data-modeling/)
- [www.mongodb.com: unbounded arrays](https://www.mongodb.com/docs/manual/data-modeling/design-antipatterns/unbounded-arrays/)
- [www.mongodb.com: transactions](https://www.mongodb.com/docs/manual/core/transactions/)
