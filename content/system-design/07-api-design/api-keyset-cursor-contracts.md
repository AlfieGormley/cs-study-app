---
id: api-keyset-cursor-contracts
title: Keyset pagination and opaque cursors
level: intermediate
minutes: 5
summary: Build stable indexed cursor pages, handle ties and separate page navigation from total counts.
sourceLesson: api-designing-good-apis
---

A cursor asks for rows after a known position rather than skipping every row before it. The position and its public contract must stay meaningful as the database changes.

## Cursor (keyset) pagination

Instead of "skip N rows", say "give me rows after this one". The cursor encodes the sort key of the last item seen.

```
GET /orders?limit=20
```

```
HTTP/1.1 200 OK

{
  "data": [ ... 20 orders ... ],
  "has_more": true,
  "next_cursor": "eyJ0IjoiMjAy..."
}
```

The cursor is an opaque, base64-encoded `(created_at, id)` pair. The next page:

```sql
-- Seek after the last timestamp/id pair.
SELECT * FROM orders
WHERE (created_at, id) < ($1, $2)
ORDER BY created_at DESC, id DESC
-- The extra row tells us has_more.
LIMIT 21;
```

Three details make this work:

- **A unique tiebreaker**. Two orders can share a `created_at`. Adding `id` makes the order total. With immutable sort keys, inserts ahead of the cursor no longer shift later pages; changes to sort keys or filters can still move items across the cursor. Use a stable snapshot if the entire traversal must represent one instant.
- **An index** on `(created_at, id)`. The `WHERE` clause becomes an index seek, so each page costs a few steps down the tree plus the rows it returns (the formula below makes this precise), without an offset-dependent walk.
- **Fetch limit + 1**. If you get 21 rows, `has_more` is true and you return 20.

The cost of a keyset page comes from the seek down the B-tree plus the rows it returns:

```formula
E_key ≈ log_b(n) + limit
cost = O(log n + limit)
where
E_key: the work for one keyset page: index pages read during the seek, plus entries returned
cost: the work the database does for one page
n: the number of rows in the index
b: the fan-out of the B-tree: how many child pointers one index page holds, often a few hundred
log_b: the logarithm to base b: how many times you can divide n by b before reaching 1, which is the number of tree levels the seek walks down
log: a logarithm; inside Big O its base doesn't matter
limit: how many rows the page returns
O(...): Big O notation: how the cost grows as the quantities inside grow, ignoring constant factors
≈: approximately equal to
In words: finding the starting point takes only a few steps down the tree, however big the table, and then the page reads just its own rows.
```

For an illustrative 2-million-row index with fan-out about 300:

```formula
h = log_{300}(2,000,000) ≈ 2.5
p ≈ 3
where
h: the illustrative logarithmic tree-height estimate
log_{300}: logarithm to base 300, the assumed number of child pointers per index page
p: the approximate index pages read during the seek, followed by the requested 20 entries
≈: approximately equal to; actual height depends on page size, fill and implementation
In words: the seek traverses roughly three index pages, independently of how deep the cursor lies in the ordered result.
```

| | Offset | Cursor |
|---|---|---|
| Deep page cost | O(offset + limit) | O(log n + limit) |
| Resists offset shifts | No | Yes, with stable sort keys |
| Jump to page N | Yes | No |

Neither style makes a **total count** cheap. "Page 3 of 107,000" may require scanning matching rows or index entries for an exact `COUNT(*)`; its cost depends on the database, filters and query plan. Many APIs return only `has_more`, or a capped or approximate count ("10,000+").

> [!tip] Make cursors opaque
> Base64-encode the cursor and document it as opaque, so clients don't parse or construct it. You can evolve the format while continuing to accept previously issued cursors until their documented expiry. Base64 hides nothing from a curious client, though, so some APIs use an HMAC or authenticated encryption to reject tampering. Stripe uses `starting_after=<object id>`; Slack and Facebook's Graph API use opaque cursors.

In a simplified indexed scan over 2 million rows at 20 per page, the last offset page walks about 2 million entries. Keyset seeks into the index and reads the remaining 20 entries; it requests up to 21 to detect another page.

> [!note] Content gap: measured pagination latency
> A reproducible workload and benchmark are not available here, so no seconds-versus-milliseconds claim is included. Index-entry estimates explain the scaling difference, not a universal response time.

## Key takeaways
- Use a total order such as created_at plus a unique id, with a matching index.
- Fetch one extra row to determine has_more.
- Stable sort keys resist offset shifts; a consistent whole traversal may still need a snapshot.
- Document cursors as opaque, preserve issued cursors until expiry and authenticate them when tampering matters.
- Exact totals are separate work; has_more, caps or estimates may fit the interface better.

## Further reading
- [Use The Index, Luke: Paging through results (no offset)](https://use-the-index-luke.com/no-offset)
- [Stripe API: Pagination](https://docs.stripe.com/api/pagination)
- [Google AIP-158: Pagination](https://google.aip.dev/158)
