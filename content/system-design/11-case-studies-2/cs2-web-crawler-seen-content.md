---
id: cs2-web-crawler-seen-content
title: Crawler seen-URL memory
level: intermediate
minutes: 3
summary: Size exact URL state and Bloom filters without silently assuming perfect membership.
sourceLesson: cs2-web-crawler
---

A crawler can discover far more URLs than it fetches. The seen-URL budget therefore follows **discovered addresses**, while body storage follows fetched pages and retained versions. Neither is a fixed multiple of the other.

## Exact state or a probabilistic pre-filter

An exact store records the URLs or suitably collision-managed identifiers. A Bloom filter stores a compact bit array and can answer two different things:

- **Definitely absent:** under a correctly maintained insert-only filter, this item has not been inserted.
- **Possibly present:** either the item was inserted or other items happen to have set its bits.

If “possibly present” means “discard the URL”, false positives silently lose crawl coverage. A useful alternative checks positives against an exact store. Negative results can bypass an unnecessary lookup, but the eventual exact insertion still needs an atomic claim: two discoverers can see the same negative at once.

## Size for the planned population

Ten billion URLs averaging 100 stored bytes would occupy about one decimal terabyte before database overhead. A conventional Bloom filter planned for that population and roughly one per cent false positives uses about twelve gigabytes. These are illustrative inputs; an exact distributed store can use memory, disk or both.

Optional sizing reference, assuming well-distributed independent hashes and the optimal hash count:

```formula reference
b = −ln(p) / (ln(2))^2
where
b: approximate filter bits per inserted item
p: target false-positive probability, strictly between zero and one
ln: natural logarithm, the logarithm to base e
e: Euler's number, approximately 2.718
In words: demanding fewer false positives requires more filter memory per stored item.
```

The probability applies to queries for absent items, not to the fraction of all positive answers that are wrong. That latter fraction depends on the query mix. Exceeding the planned item count raises the false-positive rate; monitor occupancy or use a documented expansion policy.

A stable false positive can recur every time a URL is rediscovered. Rediscovery alone does not repair it. Lost filter updates, unsafe deletion and concurrency bugs can also invalidate the no-false-negative assumption, so maintain and recover filter state deliberately.

> [!analogy] Real-world analogy: A quick guest-list screen
> A door attendant uses a compact screening list before checking the full guest register.
>
> **How it maps:** A negative filter answer rules an item out under the filter’s maintenance assumptions; a positive sends it to the exact register when false exclusions are unacceptable.
>
> **Where it stops:** A Bloom filter uses shared bits and hashes, not a shortened human list. Its positive answers can be false, and lost updates break the absence guarantee.

## Key takeaways
- Budget discovered URLs separately from fetched page bodies.
- Independent-hash Bloom sizing trades bits per item against false positives.
- Rediscovery does not repair a stable Bloom false positive.

## Further reading
- [Bloom filters](https://en.wikipedia.org/wiki/Bloom_filter)
- [Bloom-filter error semantics](https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/)
