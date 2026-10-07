---
id: api-designing-good-apis
title: Designing good APIs
level: intermediate
minutes: 13
summary: Pagination (offset vs cursor), filtering and sorting, versioning, consistent error formats, and how to evolve an API without breaking clients.
---

An API is a promise. Once a client depends on it, every quirk becomes load-bearing. Good API design is mostly about making the right promises up front, so you can change the implementation for years without breaking anyone.

This lesson covers the decisions that come up in every list endpoint and every release: pagination, filtering, sorting, errors, versioning and compatibility.

## Pagination

No list endpoint should return unbounded results. A customer with 2 million orders will eventually call `GET /orders` and take down your database. Always paginate, with a sensible default and a hard maximum (Stripe v1 list APIs: default 10, maximum 100).

### Offset pagination

```
GET /orders?limit=20&offset=40
```

```
SELECT * FROM orders
ORDER BY created_at DESC, id DESC
LIMIT 20 OFFSET 40;
```

It's simple and lets users jump to "page 37". But it has two serious problems.

**1. It gets slower the deeper you go.** The database can't jump to row 40,000. It has to walk the index and discard the first 40,000 rows, then return 20. Cost is O(offset + limit).

**2. Results shift under concurrent writes.**

```
Page 1 (offset 0):  [A B C D E]
  -- new order Z inserted at top --
Page 2 (offset 5):  [E F G H I]
                     ^ E seen twice
```

A deletion causes the opposite: an item is skipped entirely.

### Cursor (keyset) pagination

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

```
SELECT * FROM orders
WHERE (created_at, id) < ($1, $2)
ORDER BY created_at DESC, id DESC
LIMIT 21;
```

Three details make this work:

- **A unique tiebreaker**. Two orders can share a `created_at`. Adding `id` makes the order total. With immutable sort keys, inserts ahead of the cursor no longer shift later pages; changes to sort keys or filters can still move items across the cursor. Use a stable snapshot if the entire traversal must represent one instant.
- **An index** on `(created_at, id)`. The `WHERE` clause becomes an index seek, so each page costs roughly O(log n + limit) for the index seek and scan, without an offset-dependent walk.
- **Fetch limit + 1**. If you get 21 rows, `has_more` is true and you return 20.

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

## Filtering and sorting

Use query parameters, keep names consistent, and allow-list what can be filtered and sorted.

```
GET /orders?status=open
  &created_after=2026-01-01
  &sort=-created_at,id
  &limit=50
```

A common convention is `sort=-field` for descending. Other good habits:

- **Allow sorts with an acceptable query plan and cost.** A suitable index often helps, but a single-field index does not guarantee efficient combined filtering and ordering. Letting a client sort 50 million rows by an unindexed `notes` column is a denial-of-service vector.
- **Cursors must encode the sort.** If the client changes `sort` between pages, reject the old cursor with `400`.
- **Validate strictly.** Unknown filter names should return `400`, not be silently ignored. Otherwise a typo like `stauts=open` returns *all* orders, and the client never notices.

## Error formats

Clients need to handle errors programmatically. Free-text messages force them to string-match, which breaks when you fix a typo. Pick one structured format and use it everywhere.

RFC 9457, **Problem Details for HTTP APIs**, defines a standard JSON shape:

```
HTTP/1.1 422 Unprocessable Content
Content-Type: application/problem+json

{
  "type": "https://example.com/probs/funds",
  "title": "Insufficient funds",
  "status": 422,
  "detail": "Balance is 30, cost is 50.",
  "instance": "/payments/abc123",
  "balance": 30
}
```

- `type` is a stable URI identifying the error class. It's what clients branch on. RFC 9457 allows relative URIs but recommends absolute ones, and ideally the URI resolves to human-readable documentation.
- `title` is a human summary; `detail` is specific to this occurrence.
- Extension fields (`balance`) carry machine-readable context.

Also include a **request id** (often as an `X-Request-Id` header) so support can find the exact log line. And never leak stack traces or SQL errors to clients.

## Versioning

Sooner or later you'll need a breaking change. Common strategies:

| Strategy | Example |
|---|---|
| URL path | `/v2/orders` |
| Header | `Accept: ...;version=2` |
| Date-based | `Stripe-Version: 2024-06-20` |
| None (evolve only) | GraphQL style |

**URL versioning** makes versions visible in logs and straightforward to route at a gateway. Its weakness is that `v2` tends to be a big-bang rewrite, and you end up running `v1` for years.

**Stripe's versioning architecture**, described in its engineering article, uses small **version change modules** to adapt current representations for older API versions. This is a useful compatibility pattern, rather than a guarantee that every business operation has one identical code path. Consult the current Stripe versioning policy for account defaults and upgrade requirements. The diagram below is illustrative, not a list of actual releases.

```
latest response
   | transform 2026-03 -> 2025-09
   | transform 2025-09 -> 2024-06
   v
response in client's pinned version
```

## Backwards compatibility

Most changes shouldn't need a new version at all. The key is knowing which changes are safe.

| Change | Safe? |
|---|---|
| Add optional request field | Yes |
| Add response field | Yes, if tolerant |
| Add new endpoint | Yes |
| Add new enum value | Risky |
| Remove or rename field | No |
| Make optional field required | No |
| Change a field's type | No |
| Change default behaviour | No |

Adding response fields is only safe if clients follow the **robustness principle**: be tolerant of unknown fields. Strict deserialisers that reject unknown properties turn every additive change into an outage. Say so in your docs.

New **enum values** are a classic trap. If a client has a `switch` over `status` with no default case, a new `"partially_refunded"` value can crash it. Document that enums may grow and clients must handle unknown values.

> [!warning] Hyrum's Law
> "With a sufficient number of users of an API, all observable behaviours of your system will be depended on by somebody." Response ordering, timing, error message wording: someone relies on it. Be deliberate about what you expose and document what is *not* guaranteed.

### Deprecating safely

1. Announce in docs and changelog with a date.
1. Return `Deprecation` (RFC 9745) and `Sunset` (RFC 8594) headers on affected endpoints, so clients' tooling can warn developers automatically.
1. Monitor usage per client; contact heavy users directly.
1. Consider communicated, risk-assessed brownouts only where deliberate temporary failures are acceptable; critical integrations may need other migration signals.
1. Remove only when traffic is near zero.

## Key takeaways
- **Always paginate**, with a default and a maximum page size.
- **Offset** pagination is O(offset) and unstable under writes. **Cursor/keyset** pagination is roughly O(log n + limit), avoids offset shifts with stable sort keys, and cannot jump directly to page N.
- Cursors need a **unique tiebreaker** and a matching **index**, and should be **opaque**.
- Allow-list filters and sorts; budget the cost of supported sorts; reject unknown parameters.
- Use one structured error format everywhere; **RFC 9457 Problem Details** is the standard.
- Prefer **additive, backwards-compatible** changes. When you must break, version (URL or Stripe-style dates) and deprecate gradually.

## Further reading
- [Use The Index, Luke: Paging through results (no offset)](https://use-the-index-luke.com/no-offset)
- [Stripe API: Pagination](https://docs.stripe.com/api/pagination)
- [Stripe blog: APIs as infrastructure, future-proofing with versioning](https://stripe.com/blog/api-versioning)
- [RFC 9457: Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457)
- [Google Cloud API design guide](https://cloud.google.com/apis/design)
- [Google AIP-158: Pagination](https://google.aip.dev/158)
