---
id: cache-invalidation-leases
title: Use invalidation-aware leases for stale fills
level: intermediate
minutes: 2
summary: Follow a lease token from miss to refill and explain how leases also reduce concurrent database loads.
sourceLesson: cache-invalidation
---

A lease grants permission to fill a missing key, then invalidation can revoke that permission. This closes the stale-set race when the lease protocol is enforced by the cache.

## Leases (Facebook memcache)

Facebook's 2013 paper *Scaling Memcache at Facebook* introduced **leases** to fix both stale sets and thundering herds.

1. On a miss, memcached gives the client a **lease token** for that key.
2. The client reads the database and calls `set` with the token.
3. If the key was **deleted** in the meantime, the token is invalidated and the `set` is rejected.

```
 R: get -> miss, token=T1
 R: SELECT -> old
 W: UPDATE, DELETE key (T1 voided)
 R: set(key, old, T1) -> REJECTED
```

The stale set in Race 2 simply fails. The paper compares this to load-link/store-conditional on a CPU: the write only succeeds if nothing touched the key in between.

> [!analogy] Real-world analogy: the numbered restock slip
> A shelf is empty. The shop manager gives one assistant a numbered restock slip and asks everyone else to wait a moment. If the product is recalled while the assistant is in the stockroom, the manager cancels that slip, and the assistant's old stock is refused at the shelf.
>
> **How it maps:** The shelf is the cache key, the slip is the lease token issued on a miss, the recall is the delete that follows a database write, and refusing the cancelled slip is the cache rejecting the stale `set`. Handing out one slip at a time while others wait is the thundering-herd half of leases.
>
> **Where it stops:** Shoppers can simply stand and wait; memcached clients are told to back off briefly and retry, so they poll. And the "manager" is the cache server itself, not the database: no database rows are locked while a token is outstanding.

Leases also tame **thundering herds**. By default Facebook's servers handed out at most one token per key every 10 seconds. Other clients that missed were told to wait briefly and retry; the token holder usually set the value within a few milliseconds, so the retry tended to hit. Over a week of measurements on keys particularly prone to herds, the paper reports peak database query rates falling from 17K/s (17,000 queries per second) without leases to 1.3K/s with them, roughly a 13-fold cut.

A refinement lets readers accept **stale values**: a deleted item is kept briefly in a side structure, and a miss can return it marked as stale. Applications that can tolerate slightly old data carry on without waiting.

Leases were Facebook's own extension, but modern memcached (1.6+) offers similar ideas through its *meta commands*, which can tell one client it has "won" the right to recache a key while others are served a stale value.

## Key takeaways
- A token-bearing refill fails if a delete invalidated the token after the reader’s miss.
- Limiting tokens per key also reduces the number of concurrent database rebuilds.
- Eligible stale values can keep readers moving while the winner refreshes; Facebook’s lease extension and modern meta commands are implementation-specific.

## Further reading
- [Scaling Memcache at Facebook — full paper PDF](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf)
- [Meta text protocol — Memcached](https://docs.memcached.org/protocols/meta/)
