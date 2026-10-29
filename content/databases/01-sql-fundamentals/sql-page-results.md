---
id: sql-page-results
title: Page through a stable ordered result
level: basic
minutes: 3
sourceLesson: sql-select-basics
summary: Use a unique final sort key when page boundaries can cut through ties.
---

The examples continue the shop database introduced in the first unit. The original products are Kettle £30, Toaster £25, Lamp £40, Rug £90 and Mug £8. 

## LIMIT and OFFSET

`LIMIT` caps the number of rows and `OFFSET` skips some first:

```sql
-- Skip Rug, then return Lamp and Kettle.
SELECT name, price FROM products
ORDER BY price DESC
LIMIT 2 OFFSET 1;
```

| name | price |
|---|---|
| Lamp | 40 |
| Kettle | 30 |

Pages of a fixed size are the usual reason to use `OFFSET`. To show a given page, you skip every row on the earlier pages, and the database still has to produce the skipped rows before it can throw them away:

```formula reference
offset = (p − 1)s
rows_read = offset + s
where
offset: how many rows to skip, the number written after OFFSET
p: the requested page number, a positive integer counting from 1
s: the page size, a positive whole number of rows (the LIMIT value)
rows_read: result rows produced up to this full page, assuming enough matching rows exist; a plan may inspect additional underlying rows
In words: a page starts after all the rows of the earlier pages, and the database must produce every one of those skipped rows as well as the page itself.
```

With 20 rows per page, page 3 is `LIMIT 20 OFFSET 40`: skip two earlier pages, then return the next 20 rows. That means producing 60 result rows to return 20. Page 1 needs 20 result rows, but page 5,000 needs 100,000 if enough rows exist. The skipped-result work grows with the page number; sorting and filtering can inspect additional data. This assumes nothing is inserted or deleted between page requests; otherwise the pages shift.

Two rules:

1. `LIMIT` without a deterministic `ORDER BY` returns an arbitrary set of rows. If two rows tie on the sort key, add a tiebreaker such as `id`, or a page boundary can show one row twice and another never.
2. Large offsets are slow. `OFFSET 100000` still reads and discards 100,000 rows. For deep paging, use **keyset pagination**: remember the last key you showed and ask for `WHERE price < :last_price` (plus an id tiebreaker). The database can then seek straight to the right place using an index.

> [!analogy] Real-world analogy: counting pages versus using a bookmark
> Imagine a long book with no page numbers. To reach where you stopped, you could count pages from the front every time, or keep a bookmark and open the book straight at it.
>
> **How it maps:** `OFFSET` is counting from the front: every earlier row must be produced and skipped again for each new page. Keyset pagination is the bookmark: the last key you showed tells an index where to resume.
>
> **Where it stops:** The bookmark only works because the rows are kept in a fixed, indexed order with a unique tiebreaker. Unlike a book, you cannot jump straight to "page 500" with a keyset cursor; you can only continue from a key you already have.

PostgreSQL also supports the SQL-standard spelling `FETCH FIRST 2 ROWS ONLY`. SQLite does not, but both understand `LIMIT`.

## Key takeaways
- Use a unique final sort key when page boundaries can cut through ties.
- OFFSET still makes the database produce skipped result rows.
- Keyset pagination uses a remembered key to seek into an index.

## Further reading
- [SELECT — PostgreSQL documentation](https://www.postgresql.org/docs/current/sql-select.html)
- [Sorting rows (ORDER BY) — PostgreSQL documentation](https://www.postgresql.org/docs/current/queries-order.html)
- [Paging through results without OFFSET — Use The Index, Luke](https://use-the-index-luke.com/no-offset)
