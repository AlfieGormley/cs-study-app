---
id: sql-model-price-snapshots
title: Model relationships and preserve sale prices
level: advanced
minutes: 3
sourceLesson: sql-schema-ddl
summary: Use a foreign key for one-to-many and a junction table for many-to-many.
---

The examples continue the shop database introduced in the first unit. The original products are Kettle £30, Toaster £25, Lamp £40, Rug £90 and Mug £8. 

Queries come and go, but a schema lasts for years. A badly chosen type or key turns into thousands of lines of defensive code and a data-cleaning project. This lesson is about writing **DDL** (data definition language): `CREATE`, `ALTER` and `DROP`. It also covers the decisions behind those statements.

We'll redesign the module's shop schema from its requirements, then look at how to change it once it's live. Normalisation theory gets its own module (Relational Theory). How tables and indexes are stored on disk is covered in System Design.

## From requirements to tables

The shop's requirements, stated plainly:

- A customer has a name, an optional city, and may have been referred by another customer.
- A product has a name, a price and an optional category.
- A customer places many orders. A guest can also order with no account.
- An order contains many products, each with a quantity, and a product appears in many orders.

Each noun that has its own facts becomes a table. Each relationship becomes a foreign key:

```
customers 1 ──< orders 1 ──< order_items
  ^    │                          >──┐
  └────┘ referred_by                 │
              products 1 ────────────┘
```

| relationship | how it's stored |
|---|---|
| one-to-many | FK on the "many" side |
| many-to-many | a junction table |
| self-reference | FK to the same table |
| optional link | nullable FK |

`orders.customer_id` is the one-to-many link, and it is nullable for guests. `order_items` is the **junction table** that resolves orders-to-products many-to-many. Its primary key is the pair `(order_id, product_id)`: a **composite key**. It also enforces a business rule, because adding a second Kettle to order 101 fails with `UNIQUE constraint failed`. You increase `qty` instead.

### A flaw in our schema

The module's `order_items` stores only a quantity, so an order's total is computed from `products.price` **today**. Raise the Kettle's price and every historical order containing a Kettle changes value. That's wrong for invoices, refunds and accounting.

The fix is to copy the price at the moment of sale into the line item (`unit_pence`). This looks like duplication, but it's a different fact: "what this customer paid" rather than "what the product costs now". Many apparent duplicates in a well-designed schema are really **snapshots** like this.

> [!analogy] Real-world analogy: the receipt and the shelf label
> The shelf label shows today's price. Your receipt shows what you paid last month. When the shop changes the label, your receipt stays the same.
>
> **How it maps:** `products.price` is the shelf label: one current fact, updated in place. `order_items.unit_pence` is the receipt line: a copy taken at the moment of sale, which later price changes must not touch.
>
> **Where it stops:** A receipt is printed once and never edited. In a database the snapshot is ordinary data, so it stays correct only if the application fills it at checkout and nothing later overwrites it; the schema cannot tell which copy is meant to be historical.

## Key takeaways
- Use a foreign key for one-to-many and a junction table for many-to-many.
- A composite line key makes each order/product pair unique.
- The sale price is a historical fact distinct from the current product price.

## Further reading
- [Data definition — PostgreSQL documentation](https://www.postgresql.org/docs/current/ddl.html)
