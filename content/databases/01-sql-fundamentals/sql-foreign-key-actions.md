---
id: sql-foreign-key-actions
title: Protect references and choose delete actions
level: intermediate
minutes: 3
sourceLesson: sql-dml-constraints
summary: Foreign keys protect references in both insertion and deletion directions.
---

The shop's orders.customer_id references customers.id, and order_items.order_id references orders.id. Original order 105 is cancelled and has one Toaster line. Each independent write example starts from fresh original data.

### Foreign keys

`orders.customer_id REFERENCES customers(id)` says every order's customer must exist (or be NULL, like the guest order). The database checks both directions:

- Inserting an order for customer 99 fails: there is no such customer.
- Deleting customer 1 fails while orders 101 and 102 still point at her.

What happens on delete is your choice:

| `ON DELETE` | deleting the parent |
|---|---|
| `NO ACTION` (default) | fails if children exist |
| `RESTRICT` | fails, checked at once |
| `CASCADE` | deletes the children |
| `SET NULL` | sets children's FK to NULL |

`NO ACTION` and `RESTRICT` differ only in timing: `NO ACTION` can be deferred to the end of the transaction, `RESTRICT` cannot. `CASCADE` suits rows that have no meaning without their parent, such as reviews of a product or the items of an order. Be wary of using it widely: one `DELETE` of a customer could silently remove years of order history. For records you must keep, `RESTRICT` plus a soft-delete flag is safer. `SET NULL` fits optional links, such as `referred_by`: if the referrer is deleted, the customer remains, unreferred.

> [!warning] SQLite doesn't enforce foreign keys by default
> For backwards compatibility, SQLite's usual default leaves foreign key enforcement off, though a build can choose a different default. Explicitly run `PRAGMA foreign_keys = ON;` for each connection, before starting a transaction, and check its setting; changing it inside an active transaction has no effect. With enforcement off, the order for customer 99 is accepted, and deleting Asha leaves orders 101 and 102 pointing at nobody. PostgreSQL enforces declared foreign keys on ordinary writes.

### Deferred constraints

Sometimes rows that refer to each other must be inserted in an awkward order. A constraint declared `DEFERRABLE INITIALLY DEFERRED` is checked at `COMMIT` instead of after each statement. Both PostgreSQL and SQLite support this for foreign keys, and PostgreSQL also for UNIQUE. If the reference is still broken at commit time, the commit fails.

## Key takeaways
- Foreign keys protect references in both insertion and deletion directions.
- Choose CASCADE, RESTRICT or SET NULL to fit the relationship.
- Enable SQLite foreign keys per connection and distinguish deferred checks.

## Further reading
- [Constraints — PostgreSQL documentation](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [SQLite foreign key support](https://www.sqlite.org/foreignkeys.html)
