---
id: api-offset-pagination-costs
title: Bounded lists and offset pagination
level: intermediate
minutes: 3
summary: Bound list responses and trace why deep offsets cost more and shift under writes.
sourceLesson: api-designing-good-apis
---

An API is a promise. Once a client depends on it, every quirk becomes load-bearing. Good API design is mostly about making the right promises up front, so you can change the implementation for years without breaking anyone.

This unit bounds list results and examines offset pagination. Later units develop cursor contracts, query validation and compatibility.

## Pagination

No list endpoint should return unbounded results. A customer with 2 million orders will eventually call `GET /orders` and take down your database. Always paginate, with a sensible default and a hard maximum (Stripe v1 list APIs: default 10, maximum 100).

## Offset pagination

```
GET /orders?limit=20&offset=40
```

```sql
-- Walk past 40 rows before returning 20.
SELECT * FROM orders
ORDER BY created_at DESC, id DESC
LIMIT 20 OFFSET 40;
```

It's simple and lets users jump to "page 37". But it has two serious problems.

**1. It gets slower the deeper you go.** The database can't jump to row 40,000. It has to walk the index and discard the first 40,000 rows, then return 20:

```formula
E_off ≈ offset + limit
E_off ≈ 40,000 + 20 = 40,020 entries
cost = O(offset + limit)
where
E_off: the number of index entries the database walks to serve one offset page
offset: how many rows the client asks to skip (the offset query parameter)
limit: how many rows the page returns (the limit query parameter)
entries: index entries, one per row in the index
cost: the work the database does for one page
O(...): Big O notation: how the cost grows as the quantities inside the brackets grow, ignoring constant factors
≈: approximately equal to
In words: every row before the page still has to be stepped over, so page 2,001 costs about 2,000 times as much as page 1.
```

This assumes the database walks an index in sort order. Without a suitable index it is worse: it may sort the whole table first.

**2. Results shift under concurrent writes.**

```
Page 1 (offset 0):  [A B C D E]
  -- new order Z inserted at top --
Page 2 (offset 5):  [E F G H I]
                     ^ E seen twice
```

A deletion causes the opposite: an item is skipped entirely.

## Key takeaways
- Every list needs a default and maximum page size.
- An indexed offset scan still walks and discards the earlier entries.
- Concurrent inserts duplicate previously seen rows; deletions can skip rows.

## Further reading
- [Use The Index, Luke: Paging through results (no offset)](https://use-the-index-luke.com/no-offset)
- [Stripe API: Pagination](https://docs.stripe.com/api/pagination)
