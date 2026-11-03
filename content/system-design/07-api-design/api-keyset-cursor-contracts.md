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
- **An index** on `(created_at, id)`. The `WHERE` clause becomes an index seek, so each page costs a few steps down the tree plus the rows it returns (the reference below describes the growth of work), without an offset-dependent walk.
- **Fetch limit + 1**. If you get 21 rows, `has_more` is true and you return 20.

The cost of a keyset page comes from the seek down the B-tree plus the rows it returns:

```formula reference
cost = O(log n + limit)
where
cost: the growth of work for an indexed keyset page
n: the number of indexed rows
limit: the requested page size in rows
log: logarithm; its base does not affect this growth classification
O(...): Big O notation, which ignores constant factors
In words: an indexed seek finds the cursor position, then reads the page; a deeper cursor does not require walking all preceding rows.
```

The tree height depends on page size, fill and implementation. The important distinction is that the seek does not grow with the number of rows before the cursor.

| | Offset | Cursor |
|---|---|---|
| Deep page work | Walk skipped rows, then page | Seek, then read page |
| Resists offset shifts | No | Yes, with stable sort keys |
| Jump to page N | Yes | No |

Neither style makes a **total count** cheap. "Page 3 of 107,000" may require scanning matching rows or index entries for an exact `COUNT(*)`; its cost depends on the database, filters and query plan. Many APIs return only `has_more`, or a capped or approximate count ("10,000+").

> [!tip] Make cursors opaque
> Base64-encode the cursor and document it as opaque, so clients don't parse or construct it. You can evolve the format while continuing to accept previously issued cursors until their documented expiry. Base64 hides nothing from a curious client, though, so some APIs use an HMAC or authenticated encryption to reject tampering. Stripe uses `starting_after=<object id>`; Slack and Facebook's Graph API use opaque cursors.

In a simplified indexed scan over 2 million rows at 20 per page, the last offset page walks about 2 million entries. Keyset seeks into the index and reads the remaining 20 entries; it requests up to 21 to detect another page.

> [!note] Content gap: measured pagination latency
> A reproducible workload and benchmark are not available here, so no seconds-versus-milliseconds claim is included. Index-entry estimates explain the scaling difference, not a universal response time.

> [!analogy] Real-world analogy: A bookmark
> **How it maps:** A bookmark identifies where to continue. Counting pages from the front each time resembles offset navigation; continuing after a known ordered item resembles keyset navigation.
>
> **Where it stops:** Rows can move or disappear, unlike fixed printed pages. Stable sort keys, unique ties and sometimes a snapshot are still needed.

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
