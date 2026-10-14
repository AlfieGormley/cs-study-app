---
id: cs1-url-expiry-negative-cache-freshness
title: Keep expiry and negative caching race-safe
level: intermediate
minutes: 3
summary: Check logical expiry on reads instead of waiting for physical deletion.
sourceLesson: cs1-url-shortener
---

The mapping store may replicate asynchronously, while redirect services cache both mappings and not-found results. This unit examines how those two optimisations can hide a new link and how to prevent that race.

## Deep dive 4: Caching and expiry

The application uses cache-aside: check Redis, read the store on a miss, then populate Redis. Links are effectively immutable, so cache invalidation is easy; set a TTL (say, 24 hours) and evict on expiry or deletion.

Two subtleties:

- **Negative caching.** Bots hammer random codes. Cache "not found" for a short time (60 s) so they don't all fall through to the database. A Bloom filter can reject absent codes only when it covers all committed codes relevant to that read; a stale filter must not suppress fresh links.
- **Expiry.** Check `expires_at` on every read (lazy expiry), and let a background job or the store's TTL feature (DynamoDB TTL, Cassandra TTL) physically delete rows later.

## Deep dive 5: Consistency after create

A subtle bug lurks between negative caching and replication. A user creates a link and pastes it into a chat; a friend clicks within 200 ms. If the redirect hits a replica (or another region) that hasn't received the write yet, it returns 404 and *caches the 404 for 60 seconds*. The link looks broken for a minute.

Fixes, roughly in order of preference:

- **Write-through on create.** The write API puts `code → long_url` into the cache as it writes the store, and deletes any negative entry for that code.
- **Fall back to the primary on a miss.** If the replica says "not found", retry against the primary (or home region) before caching a negative result. Misses on real codes are rare, so the extra cost is small.
- **Keep negative TTLs short** (seconds, not minutes) and only negatively cache after a cheap format rejection or a Bloom filter check whose completeness for relevant committed codes is guaranteed.

Immutable mappings simplify replication, but deletion, expiry, abuse blocking, custom-alias uniqueness and stale negative-cache fills still need consistency rules. A create racing with an older miss can be overwritten by a late negative fill; version or condition cache writes, or avoid negative caching valid-looking codes when strict freshness is required.

## Bottlenecks and trade-offs

- **Hot links**: in a scenario where a viral link gets over 100,000 requests a second, compare that load with measured shard capacity. Add a small in-process cache on each redirect server, or serve the redirect from the CDN edge.
- **ID coordinator**: range allocation makes it nearly irrelevant, but run it replicated (etcd/ZooKeeper) so block allocation survives a node loss.
- **Abuse**: shorteners are used to hide phishing links. Scan on creation, rescan periodically, and be able to disable a link globally (another reason to keep browser caching of redirects short).

## Key takeaways

- Check logical expiry on reads instead of waiting for physical deletion.
- A stale replica or Bloom filter must not hide a freshly created mapping.
- Version cache fills and combine hot-link caching with bounded blocking delays.

## Further reading

- [DynamoDB: time to live](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html)
- [RFC 9111: HTTP caching](https://www.rfc-editor.org/rfc/rfc9111.html)
