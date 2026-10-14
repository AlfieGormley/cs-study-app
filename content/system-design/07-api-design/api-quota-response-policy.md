---
id: api-quota-response-policy
title: Quota policy and client signals
level: advanced
minutes: 3
summary: Explain why limits exist and signal client quotas with 429, Retry-After and remaining allowance.
sourceLesson: api-rate-limiting
---

Rate limiting caps how many requests a client can make in a period. It's one of the most common system design interview questions, and one of the most important pieces of real API infrastructure.

## Why rate limit?

- **Protect the service.** One buggy client in a tight loop shouldn't take down everyone else.
- **Fairness.** Share capacity between tenants, so a noisy neighbour can't starve the rest.
- **Cost control.** Expensive endpoints (search, AI inference, SMS sending) cost real money per call.
- **Security.** Slow down credential stuffing, scraping and enumeration attacks.
- **Commercial tiers.** Free plan 60 requests/min, paid plan 5,000.

Stripe runs several limiters in layers: a request-rate limiter per user, a concurrent-requests limiter, and load shedders that drop low-priority traffic when the whole fleet is under stress.

## Signalling limits to clients

When a client is over its limit, return **429 Too Many Requests** (defined in RFC 6585), and tell it when to come back:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 12
RateLimit-Policy: "min";q=100;w=60
RateLimit: "min";r=0;t=12
Content-Type: application/problem+json

{"title": "Rate limit exceeded",
 "detail": "100 requests per minute"}
```

- `Retry-After` is a standard header: seconds to wait, or an HTTP date.
- `RateLimit-Policy` and `RateLimit` are being standardised by the IETF (still a draft in 2026). The policy says "quota `q` = 100 per window `w` = 60 s"; `RateLimit` says how much is left (`r`) and the effective time window in seconds (`t`), rather than a universal guarantee of a full reset. Earlier drafts used three separate `RateLimit-Limit`, `-Remaining` and `-Reset` headers, which some gateways still emit, and many APIs (GitHub, for example) use the older `X-RateLimit-Limit`, `X-RateLimit-Remaining` and `X-RateLimit-Reset`. Note that GitHub's `X-RateLimit-Reset` is a Unix timestamp, not a number of seconds, so always read the docs.
- Send the remaining-quota headers on **successful** responses too, so well-behaved clients can slow down *before* hitting the wall.

Don't use `503` for per-client limits. `503` describes temporary inability to serve this request, which clients and monitors may handle differently. Load shedding or maintenance can legitimately use `503` even if other endpoints or clients are still served.

## Key takeaways
- Limits protect capacity, fairness, cost and accounts; request and concurrency limits have different jobs.
- Return 429 for a client quota and use Retry-After to guide recovery.
- Expose remaining allowance on successes too; header formats and reset units depend on the contract.

## Further reading
- [Stripe blog: Scaling your API with rate limiters](https://stripe.com/blog/rate-limiters)
- [MDN: 429 Too Many Requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429)
- [IETF draft: RateLimit header fields for HTTP](https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/)
- [GitHub: Rate limits for the REST API](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)
