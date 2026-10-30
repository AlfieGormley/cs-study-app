---
id: rel-th-analytical-layouts
title: Star schemas and embedded records
level: advanced
minutes: 2
sourceLesson: rel-th-denormalisation
summary: Star schemas and document embedding: deliberate redundancy shaped around read patterns.
---

## Star and snowflake schemas

Analytical databases denormalise on purpose. A **star schema** has a central **fact table** (one row per sale, with numeric measures and foreign keys) surrounded by wide, denormalised **dimension tables**:

```
          dim_date
             |
dim_store - fact_sales - dim_product
             |
         dim_customer
```

`dim_product` holds product, category and department names in one row, even though that contains a transitive dependency: the product fixes its category, and the category fixes its department, so the department depends on the key only indirectly. A normalised design would move category and department into their own tables.

Storing it flat repeats each department name on every product row. The **snowflake schema** variant normalises dimensions back out. Stars suit analytics because queries join one big fact table to a few small, flat dimensions, which is simple for analysts and efficient for columnar engines. The redundancy has to be managed by a controlled loading pipeline that rewrites dimension rows consistently and checks them after each load; batch loading by itself does not prevent update anomalies.

## Embedding and access patterns

Document and key-value stores push this furthest. In MongoDB you might embed an order's lines inside the order document. In DynamoDB’s native query API, which has no relational join operation, a common pattern stores several entity types in one table, keyed so that one query fetches a customer and their recent orders together. AWS's own guidance is to design around your access patterns first, which is denormalisation as the default. The cost is the same as in SQL: duplicated data must be updated in every place, and changing an access pattern can require rewriting the data.

## Key takeaways

- Star dimensions deliberately repeat descriptive attributes for analytical access.
- Embedding and single-table designs trade simpler reads for maintenance and access-pattern constraints.

## Further reading

- [PostgreSQL 18: refresh materialised views](https://www.postgresql.org/docs/18/sql-refreshmaterializedview.html)
- [PostgreSQL 18: generated columns](https://www.postgresql.org/docs/18/ddl-generated-columns.html)
- [AWS: transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)
- [Kimball: Fact Tables and Dimension Tables](https://www.kimballgroup.com/2003/01/fact-tables-and-dimension-tables/)
- [AWS: DynamoDB modelling and access patterns](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-general-nosql-design.html)
- [MongoDB: embedding and references](https://www.mongodb.com/docs/manual/data-modeling/concepts/embedding-vs-references/)
