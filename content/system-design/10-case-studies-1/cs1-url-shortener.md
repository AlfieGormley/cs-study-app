---
id: cs1-url-shortener
title: Design a URL shortener
level: intermediate
minutes: 18
summary: Design a TinyURL/Bitly-style service, focusing on short-code generation (hashing, counters, Snowflake), 301 vs 302 redirects, caching and click analytics.
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

```
Writes: 100M / 10^5 s    ≈ 1,000/s
        (peak x3)        ≈ 3,000/s
Reads:  1B / 10^5 s      ≈ 10,000/s
        (peak x3)        ≈ 30,000/s
```

Storage, keeping links for 10 years at about 500 bytes each (long URL, code, owner, timestamps):

```
Links: 100M x 365 x 10  ≈ 365 billion
Size:  365B x 500 B     ≈ 180 TB
With 3x replication     ≈ 550 TB
```

How long must the code be? Using **base62** (`a–z`, `A–Z`, `0–9`):

| Length | Codes |
|---|---|
| 6 | 62^6 ≈ 57 billion |
| 7 | 62^7 ≈ 3.5 trillion |
| 8 | 62^8 ≈ 218 trillion |

Six characters would run out in about 1.5 years. **Seven** gives 3.5 trillion, about ten times our 10-year need. That headroom matters for one of the ID strategies below.

Cache sizing using the 80/20 rule: if 20% of links get most of the traffic, suppose the chosen hot set contains 200 million distinct links. At 500 B each its raw payload is 100 GB, before cache overhead and replication. The 80/20 rule and a billion daily requests do not determine the number of distinct hot links; estimate that from access traces and the desired hit rate.

The cache hit rate then sets the database read load. At a 90% hit rate, 30,000 peak redirects/s leaves about 3,000 reads/s for the store; at 99%, only 300. Link popularity is heavily skewed (most links are clicked mostly in the first days after being shared), so high hit rates are realistic.

What the numbers tell us: writes are modest, reads are high but cache well, and storage (180 TB raw, over half a petabyte replicated) motivates evaluating horizontal partitioning, storage tiers and recovery costs; raw size alone does not prove a universal single-node limit.

## Step 3: API

```
POST /v1/links
  {longUrl, customAlias?, expiresAt?}
  -> 201 {code, shortUrl}

GET /{code}
  -> 302 Location: <longUrl>
  -> 404 if unknown or expired

GET /v1/links/{code}/stats?from&to
  -> {clicks, byCountry, byReferrer}
```

The create endpoint takes an API key and is rate limited per key (spammers love shorteners). It should accept an `Idempotency-Key` header so a retried request doesn't create two links.

## Step 4: Data model

The core access pattern is a point lookup: **code → long URL**. No joins, no range scans. That suits a key-value or wide-column store partitioned by `code`: DynamoDB, Cassandra, or a sharded MySQL/Postgres with `code` as the shard key.

```
links
  code        PK  (7-char string)
  long_url        (up to ~2 KB)
  owner_id
  created_at
  expires_at      (nullable)
```

Owners also want "list my links", which is a different access pattern (by `owner_id`). Handle it with a secondary index (a DynamoDB GSI) or a separate `links_by_owner` table, rather than scanning.

Analytics data is a completely different shape (high-volume, append-only, aggregated) and lives elsewhere.

## Step 5: High-level design

```
        Client
          |
          v
   CDN / load balancer
          |
     +----+------+
     v           v
 Write API    Redirect svc
     |           |      \
     v           v       v
 ID allocator  Redis   Kafka
     |           |    (clicks)
     v           v       |
   Links store <-+       v
   (KV, sharded)     Analytics
                     (OLAP)
```

**Create**: the write API validates the URL (and checks an appropriate threat-intelligence service under its usage terms; Google Safe Browsing is limited to non-commercial use, while commercial users are directed to Web Risk), obtains a unique code, writes `code → long_url` to the links store, and returns.

**Redirect**: the redirect service looks up the code in Redis; on a miss it reads the store and populates the cache. It returns a redirect and fires a click event to Kafka *asynchronously*, with bounded buffers and an explicit drop/backpressure policy so analytics do not block redirect completion.

Read and write paths are separate services because they scale very differently: 30k reads/s vs 3k writes/s, with different latency targets.

## Deep dive 1: Generating short codes

This is the heart of the problem. You need billions of unique, short, ideally unguessable codes, generated by many servers without a global lock.

### Option A: Hash the long URL

Hash the URL with SHA-256 and map it approximately uniformly into the base62 code space. The collision arithmetic below assumes uniform codes; naively taking leading digits of a variable-width integer encoding can introduce bias.

- **Pro**: stateless; any server can compute it.
- **Con: collisions.** Truncating to 7 characters leaves a 3.5-trillion space. By the [birthday problem](https://en.wikipedia.org/wiki/Birthday_problem), collisions become likely after about √(3.5T) ≈ 1.9 million links. With hundreds of billions of links you will collide constantly, so every write needs an atomic insert-if-absent and a retry on conflict (for example, appending a counter and rehashing).
- **Con: same URL, same code.** Two users shortening the same URL get the same link, which breaks per-owner analytics and expiry. You can salt with the user ID, but then you lose the dedup that was the main appeal.

### Option B: A counter, base62-encoded

Give each link the next integer and base62-encode it. With the alphabet ordered `0–9`, `a–z`, `A–Z`: `1 → "1"`, `125 → "21"` (2 × 62 + 1), and 62^7 − 1 (about 3.5 trillion) → `"ZZZZZZZ"`, the largest 7-character code.

- **Pro**: no collisions, ever. Codes are as short as possible.
- **Con**: a single global counter is a bottleneck and single point of failure.
- **Fix: range allocation.** A coordination service (a small database table, ZooKeeper or etcd) hands each write server a *block* of, say, 1 million IDs. The server allocates from its block in memory and only goes back for a new block when it runs out. At 3,000 writes/s, the coordinator is contacted once every few minutes. If a server crashes, the rest of its block is simply wasted. With 3.5 trillion codes, wasting millions is irrelevant.
- **Con: guessable.** Sequential codes let anyone enumerate links (`aaaaaab`, `aaaaaac`...). Fix this by passing the counter through a reversible permutation before encoding: for example, multiply by a large constant that shares no factor with 62^7 (so not a multiple of 2 or 31) modulo 62^7, or use a small Feistel network keyed with a secret. It stays collision-free (it's a bijection) but looks random. The multiplication trick only hides the pattern from casual eyes (two known codes reveal the constant); a vetted keyed permutation can hide sequence relationships, but a custom small Feistel construction is not established as secure here.

### Option C: Snowflake-style IDs

[Snowflake](https://en.wikipedia.org/wiki/Snowflake_ID), from Twitter, packs a 64-bit ID as:

```
| 1 | 41 bits ms | 10 bits  | 12 bits |
|   | timestamp  | machine  | seq     |
```

Each worker has 4,096 sequence values per millisecond. Generation avoids per-ID coordination, but worker IDs must be assigned uniquely and restart/clock behavior must prevent reuse.

- **Pro**: fully decentralised, roughly time-ordered.
- **Con: length.** A Snowflake ID uses 63 bits, and today's values are around 10^18, which takes **11 base62 characters**, not 7. For a *short*ener, that's a real cost.
- **Con: clocks.** If a machine's clock goes backwards (NTP correction), it can reissue IDs unless the generator refuses to run until the clock catches up.

### Option D: Pre-generated key service

A key generation service pre-computes random 7-character codes, stores them in an "unused" table, and hands batches to write servers. It's essentially Option B with random rather than sequential codes. It works, but you have to store and manage billions of unused keys.

> [!tip] Recommended answer
> Range-allocated counters with a bijective shuffle, base62-encoded to 7 characters. Collision-free and short when ranges are never reused; the shuffle is not an access-control mechanism, and the coordinator is touched only once per million links.

**Custom aliases** go in the same table using a conditional write ("insert if not exists": DynamoDB `attribute_not_exists`, or a primary key constraint in SQL). To stop a custom alias colliding with a future generated code, either reserve a distinct format for aliases (for example, require them to be 8+ characters or contain a hyphen) or have the generator skip codes that already exist.

## Deep dive 2: 301 vs 302

Both send the browser to the long URL. The difference is caching.

| | 301 Permanent | 302 Found |
|---|---|---|
| Heuristic cacheability | Yes | Not normally; explicit freshness can permit storage |
| Later clicks hit us? | Depends on freshness policy | Depends on freshness policy |
| Analytics | Cached visits may be missed | Cached visits may be missed |
| Updated target seen? | Depends on cache policy | Depends on cache policy |

A fresh cached redirect can bypass your service, hiding visits and delaying target or expiry changes. A **301** is heuristically cacheable; **302/307** can also be cached with explicit freshness. Use an explicit policy such as `Cache-Control: no-store` when repeat navigation should resolve through your service, and account for analytics delivery failures separately.

Without explicit cache headers, browsers treat a 301 as cacheable and may keep it indefinitely; a 302 is cached only if headers say so. A permanent redirect can still use a short freshness lifetime or `no-store`; the status and cache policy serve different purposes.

> [!note] Content gap: live provider headers
> Exact Bitly, t.co and TinyURL cache-header claims have been removed. No reproducible set of representative URLs and dated response captures was supplied, so this audit cannot reliably present those variable deployment settings as provider-wide facts.

So the real lever is `Cache-Control`, not only the status code. Say the trade-off explicitly; that's what the interviewer is checking.

## Deep dive 3: Analytics

Never update a counter row synchronously on every redirect. At 30,000 redirects/s, a popular link would become a hot row and add latency to every redirect.

Instead:

1. The redirect service emits a click event (`code, timestamp, country from IP, user agent, referrer`) to Kafka, fire-and-forget, and returns immediately.
2. A stream processor (Flink, Kafka Streams) aggregates events into per-link, per-hour buckets.
3. Aggregates go into an OLAP store such as ClickHouse or Druid, which answers "clicks by country last 7 days" quickly.

Raw events can also be written to object storage (S3) for reprocessing. If Kafka is briefly unavailable, the redirect must still work: buffer locally and drop analytics before you ever fail a redirect. Redirects are the product; analytics are a feature.

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
- **Keep negative TTLs short** (seconds, not minutes) and only negatively cache codes that fail a cheap format or Bloom filter check.

Immutable mappings simplify replication, but deletion, expiry, abuse blocking, custom-alias uniqueness and stale negative-cache fills still need consistency rules. A create racing with an older miss can be overwritten by a late negative fill; version or condition cache writes, or avoid negative caching valid-looking codes when strict freshness is required.

## Bottlenecks and trade-offs

- **Hot links**: a viral link can get 100k+ requests/s, more than a single Redis shard wants. Add a small in-process cache on each redirect server, or serve the redirect from the CDN edge.
- **ID coordinator**: range allocation makes it nearly irrelevant, but run it replicated (etcd/ZooKeeper) so block allocation survives a node loss.
- **Abuse**: shorteners are used to hide phishing links. Scan on creation, rescan periodically, and be able to disable a link globally (another reason to keep browser caching of redirects short).

## At 10x scale

At 1 billion new links a day and 300k redirects/s:

- **Seven characters is no longer enough** for 10 years (3.65 trillion links vs 3.5 trillion codes). Move to 8 characters (218 trillion) for new links. An 8-character string can never equal a 7-character one, so new generated links use exactly eight characters (left-pad short encodings), with a fresh permutation over [0, 62^8). Also revise alias reservations or atomically skip already-claimed aliases.
- **Storage reaches petabytes** (about 1.8 PB raw over 10 years). Expire links nobody has clicked for years, or move them to cheaper storage.
- **Go multi-region.** Redirects are read-only and links are immutable, so replicate the links store asynchronously to every region and serve redirects locally. Give each region its own ID ranges so regions never need to coordinate on writes. A link created in Europe might take a second to resolve in Asia; the primary-fallback from deep dive 5 covers that window.
- **Push redirects to the edge.** CDN workers (Cloudflare Workers, Lambda@Edge) can hold hot mappings and reduce origin work; end-to-end latency still needs measurement, shipping click logs back in batches.
- **Shard the analytics pipeline** by code and pre-aggregate at the edge before sending upstream.

## Key takeaways

- Seven base62 characters give 3.5 trillion codes; size the code length from your 10-year link count.
- Hashing needs collision checks (birthday bound ≈ √N), counters need coordination, Snowflake IDs are too long for a shortener.
- Non-reused range allocations plus a bijective shuffle avoid collisions; private links still need authorization.
- Redirect caching trades origin load against freshness and click visibility. `Cache-Control` matters for both 301 and 302; choose it explicitly.
- Cache hit rate sets database load; negative caching requires race-safe fills and fresh source/filter checks to avoid hiding newly created links.
- Emit clicks asynchronously to a log and aggregate in a stream processor; never block a redirect on analytics.
- Links are immutable, so caching, multi-region replication and edge serving are all easy wins.

## Further reading

- [URL shortening (Wikipedia)](https://en.wikipedia.org/wiki/URL_shortening)
- [Snowflake ID (Wikipedia)](https://en.wikipedia.org/wiki/Snowflake_ID)
- [MDN: 301 Moved Permanently](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/301)
- [MDN: 302 Found](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/302)
- [System Design Primer: design Pastebin / Bit.ly](https://github.com/donnemartin/system-design-primer/blob/master/solutions/system_design/pastebin/README.md)
- [Hello Interview: design a URL shortener like Bit.ly](https://www.hellointerview.com/learn/system-design/problem-breakdowns/bitly)
- [Base62 (Wikipedia)](https://en.wikipedia.org/wiki/Base62)
