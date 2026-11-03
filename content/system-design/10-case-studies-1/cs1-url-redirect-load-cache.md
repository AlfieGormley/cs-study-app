---
id: cs1-url-redirect-load-cache
title: Estimate redirect traffic and cache misses
level: intermediate
minutes: 4
summary: State the redirect ratio and peak multiplier explicitly.
sourceLesson: cs1-url-shortener
---

A URL shortener looks trivial: map a short code to a long URL. That's why it's a favourite opener. The interviewer isn't interested in the mapping; they want to see how you generate billions of unique short codes without a bottleneck, how you serve a very read-heavy workload, and what you do about analytics.

## Step 1: Requirements

**Functional**

- Create a short link from a long URL. Returns something like `https://sho.rt/aZ3kQ9x`.
- Visiting a short link redirects to the original URL.
- Optional custom alias (`sho.rt/summer-sale`).
- Optional expiry.
- Link owners can see click counts (by day, country, referrer).

**Non-functional**

- Very read-heavy: assume 10 redirects for every link created.
- Low latency redirects: p99 under ~50 ms server-side.
- Highly available: a broken redirect breaks someone else's website, email or printed poster.
- Durable: a created link must never be lost or remapped.
- Avoid exposing sequential allocation through codes. Truly private links require authorization: at 10% namespace occupancy, a random probe finds some valid code about once in ten attempts, regardless of the permutation.

Out of scope: user management, billing, link editing UI.

## Step 2: Estimates

Assume **100 million new links per day** and a **10:1** read:write ratio.

Separate the create path from the redirect path:

In this hypothetical workload, redirects greatly outnumber creates. Use a measured or explicitly assumed peak profile to assess both paths; daily totals do not determine the burst rate.

Cache sizing using the 80/20 rule: if 20% of links get most of the traffic, suppose the chosen hot set contains 200 million distinct links. At 500 B each its raw payload is 100 GB, before cache overhead and replication. The 80/20 rule and a billion daily requests do not determine the number of distinct hot links; estimate that from access traces and the desired hit rate.

The cache hit rate then sets the database read load, because only misses reach the store:

At a 90% hit rate, one lookup in ten reaches the store; at 99%, one in a hundred does. Compare miss traffic, including cache failure, with the measured database capacity.

A skewed access trace can support high hit rates, but the achieved hit rate depends on the hot set, cache capacity and expiry policy. Measure it rather than assuming a universal link-lifetime distribution.

## Key takeaways

- State the redirect ratio and peak multiplier explicitly.
- Measure distinct hot links rather than deriving them from the 80/20 rule.
- Compare cache hit rates by the resulting database misses.

## Further reading

- [RFC 9111: HTTP caching](https://www.rfc-editor.org/rfc/rfc9111.html)
- [System Design Primer: design approach](https://github.com/donnemartin/system-design-primer/blob/master/README.md)
