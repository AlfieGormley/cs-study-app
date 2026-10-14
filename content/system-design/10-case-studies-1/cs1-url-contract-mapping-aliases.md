---
id: cs1-url-contract-mapping-aliases
title: Design the mapping contract and custom aliases
level: intermediate
minutes: 3
summary: Point lookup by code and listing by owner are different access patterns.
sourceLesson: cs1-url-shortener
---

At the assumed peak, redirect traffic is 30,000 requests a second and creation is 3,000. The storage estimate uses seven-character generated codes; this unit connects those requirements to the API, data model and read/write paths.

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

## Custom alias uniqueness

**Custom aliases** go in the same table using a conditional write ("insert if not exists": DynamoDB `attribute_not_exists`, or a primary key constraint in SQL). To stop a custom alias colliding with a future generated code, either reserve a distinct format for aliases (for example, require them to be 8+ characters or contain a hyphen) or have the generator skip codes that already exist.

## Key takeaways

- Point lookup by code and listing by owner are different access patterns.
- Make retried creates idempotent and keep click processing off the redirect path.
- Reserve alias formats or atomically skip codes already claimed by aliases.

## Further reading

- [DynamoDB: conditional writes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.ConditionExpressions.html)
- [AWS: transactional outbox pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)
- [Google: Safe Browsing usage](https://developers.google.com/safe-browsing)
