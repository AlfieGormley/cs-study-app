---
id: net-cdn-cache-key-safety
title: "Cache keys without fragmentation or leaks"
level: advanced
minutes: 3
summary: "Include response-changing dimensions while excluding tracking noise and protecting personalised pages."
sourceLesson: net-cdn
---
A cache key defines which requests can share bytes safely. Decide which inputs actually change the response before tuning the hit ratio; correctness and privacy come first.

## Cache keys: the most important design decision

The **cache key** decides which requests share a cached object. A key can include host, path, selected query parameters, headers and cookies. Defaults vary: CloudFront's default key excludes query strings, cookies and headers unless configured.

Get it **too broad** and users get the wrong content. Get it **too narrow** and the hit ratio collapses.

### Fragmentation: keys too narrow

Consider `/product/42?utm_source=newsletter&utm_campaign=oct`. If the full query string is in the key, every combination of tracking parameters is a separate object: one hot page becomes thousands of cold ones.

Common culprits:

- Tracking parameters (`utm_*`, `fbclid`, `gclid`).
- Query parameters in random order (`?a=1&b=2` vs `?b=2&a=1`).
- `Vary: User-Agent`, which splits the cache by thousands of user-agent strings.
- Cookies in the key, when only one cookie matters.

Fixes: include only **allow-listed** query parameters and headers, sort parameters, and normalise headers into a few buckets (e.g. map `Accept-Encoding` to `br`, `gzip` or none; map user agents to `mobile` or `desktop`).

### Leakage: keys too broad

The opposite failure is worse. If a personalised response (`/account` showing Alice's name) is cached under a key that doesn't include the user, Bob gets Alice's page. Real incidents of this kind have exposed users' personal data.

> [!warning] Defaults to protect you
> Mark personalised responses `Cache-Control: private` or `no-store`, and keep authenticated paths off the CDN cache unless the key includes the identity. Ensure CDN configuration honours those headers. In CloudFront, a positive minimum TTL can override `private` or `no-store`; use an appropriate zero-minimum-TTL or cache-disabled policy for these paths. Also beware *web cache deception*: tricking the cache into storing `/account/profile.css` because the extension looks static.

## Key takeaways

- A narrow key fragments equivalent content; a broad key merges responses that must differ.
- Allow-list and normalise response-changing parameters, headers and cookies.
- Keep personalised responses private and resist cache deception caused by path-suffix rules.

## Further reading

- [Understand the cache key (Amazon CloudFront)](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/controlling-the-cache-key.html)
- [Vary header (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Vary)
- [Cache expiry and minimum TTL (Amazon CloudFront)](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Expiration.html)
- [HTTP caching (RFC 9111)](https://www.rfc-editor.org/rfc/rfc9111)
