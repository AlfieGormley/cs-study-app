---
id: cs1-interview-contract-access-patterns
title: Connect the API, access patterns and architecture
level: basic
minutes: 3
summary: Describe retries, pagination, authentication and rate limits in the client contract.
sourceLesson: cs1-interview-framework
---

With requirements and estimates established, connect the external API to the data it reads and writes. Every architectural component should answer a stated requirement or measured constraint.

## Step 3: API design

Define the contract between clients and your system. Usually a handful of REST endpoints is enough:

```
POST /v1/links  {longUrl, alias?, ttl?}
  -> 201 {shortUrl}
GET  /{code}    -> 302 Location: longUrl
```

Things to mention: authentication (API keys or OAuth tokens), pagination (cursor-based, not offset), idempotency keys for writes that might be retried, and rate limits. For live interactive features say *how* the client connects (WebSocket, Server-Sent Events, long polling) and why.

## Step 4: Data model

Name the core entities, their key fields and, crucially, the **access patterns**: what you look up by what. The access pattern drives the choice of store and the partition key.

- "Look up a link by its short code" means a key-value lookup; any store works, and the partition key is the code.
- "Get a user's last 50 messages in a conversation" means a range scan ordered by time within a partition; a wide-column store such as Cassandra with partition key `conversation_id` and clustering key `message_id` fits well.

Justify SQL vs NoSQL by the access pattern and scale, not by fashion. "Relational, because we need transactions across the order and payment tables" is a good reason. "NoSQL because it scales" is not.

## Step 5: High-level design

Draw the boxes and arrows that satisfy the functional requirements end to end. Start simple:

```
 Client
   |
   v
 Load balancer
   |
   v
 App servers (stateless) --> Cache
   |
   v
 Database (primary + replicas)
```

Then walk a request through it: "A redirect hits the load balancer, an app server checks Redis, on a miss reads the database, and returns a 302." Walking requests through the diagram catches gaps (where does the ID come from?) before the interviewer does.

Only add components when a requirement or an estimate demands them. Every box should have a reason. A message queue appears because you need to absorb bursts or decouple a slow step, not because big systems have queues.

## Check the end-to-end contract

For a retried write, the client needs to know whether a lost response means it should retry with the same idempotency key. The storage layer must enforce that key atomically with recoverable work; an API header by itself does not prevent duplicates. For reads, the pagination cursor should describe the ordering used by the query.

A spatial query such as finding available drivers within two kilometres needs an index and query strategy that match location searches. Saying only that a database is reliable leaves the actual access pattern unexplained. Likewise, if representative benchmarks show a single relational primary meets the workload, latency and recovery targets, begin there and identify the evidence that would trigger replicas or sharding. These choices connect a contract to a concrete data path.

## Key takeaways

- Describe retries, pagination, authentication and rate limits in the client contract.
- Choose keys and stores from the queries and transaction boundaries.
- Walk a request through every component so gaps become visible.

## Further reading

- [DynamoDB: conditional writes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.ConditionExpressions.html)
- [AWS: transactional outbox pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)
