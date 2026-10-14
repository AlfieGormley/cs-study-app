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

Divide each daily count by the seconds in a day (rounded to 100,000), then multiply by an assumed peak factor of 3:

```formula
writes ≈ 100M / (10^5 s) = 1,000/s
peak writes ≈ 1,000/s × 3 = 3,000/s
reads ≈ 1B / (10^5 s) = 10,000/s
peak reads ≈ 10,000/s × 3 = 30,000/s
where
writes: average links created per second
reads: average redirects per second; 10 per link created, so 1 billion a day
peak writes, peak reads: the same rates at the busiest time, using an assumed peak factor of 3
M: million (10^6)
B: billion (10^9)
10^5: 100,000, the seconds in a day (86,400) rounded up
s: seconds; /s means per second
≈: approximately equal to (rounded)
In words: 100 million links a day is about 1,000 creates a second and ten times that in redirects, tripled at peak.
```

Cache sizing using the 80/20 rule: if 20% of links get most of the traffic, suppose the chosen hot set contains 200 million distinct links. At 500 B each its raw payload is 100 GB, before cache overhead and replication. The 80/20 rule and a billion daily requests do not determine the number of distinct hot links; estimate that from access traces and the desired hit rate.

The cache hit rate then sets the database read load, because only misses reach the store:

```formula
db reads = reads × (1 − h)
db reads = 30,000/s × (1 − 0.9) = 3,000/s
db reads = 30,000/s × (1 − 0.99) = 300/s
where
db reads: redirects per second that miss the cache and read the store
reads: peak redirects per second, here 30,000
h: the cache hit rate, the fraction of lookups the cache answers, between 0 and 1 (90% = 0.9)
/s: per second
In words: at a 90% hit rate one lookup in ten reaches the store; at 99% only one in a hundred does.
```

So at a 90% hit rate, 30,000 peak redirects/s leaves about 3,000 reads/s for the store; at 99%, only 300. A skewed access trace can support high hit rates, but the achieved hit rate depends on the hot set, cache capacity and expiry policy. Measure it rather than assuming a universal link-lifetime distribution.

## Key takeaways

- State the redirect ratio and peak multiplier explicitly.
- Measure distinct hot links rather than deriving them from the 80/20 rule.
- Compare cache hit rates by the resulting database misses.

## Further reading

- [RFC 9111: HTTP caching](https://www.rfc-editor.org/rfc/rfc9111.html)
- [System Design Primer: design approach](https://github.com/donnemartin/system-design-primer/blob/master/README.md)
