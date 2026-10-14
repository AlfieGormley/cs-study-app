---
id: api-query-validation-errors
title: Query validation and structured errors
level: intermediate
minutes: 2
summary: Allow-list query operations and give clients stable Problem Details instead of message matching.
sourceLesson: api-designing-good-apis
---

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

## Key takeaways
- Allow supported filters and sorts only when their query cost is acceptable.
- Reject unknown parameters and cursors that do not match the selected sort.
- Branch on Problem Details type, expose a request id and keep internal errors out of responses.

## Further reading
- [RFC 9457: Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457)
- [Google Cloud API design guide](https://cloud.google.com/apis/design)
