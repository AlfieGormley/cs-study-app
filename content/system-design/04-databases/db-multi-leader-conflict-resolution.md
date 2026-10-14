---
id: db-multi-leader-conflict-resolution
title: Multi-leader conflict resolution
level: intermediate
minutes: 2
summary: Trade local regional writes for explicit conflict handling and compare last-write-wins, merging and CRDTs.
sourceLesson: db-replication
---

Putting a writer in each region removes a remote round trip from local writes. It also permits independent histories that must be reconciled after they meet.

## Multi-leader replication

Several nodes accept writes, typically **one leader per datacentre**, and replicate to each other asynchronously.

```
 DC London         DC Virginia
┌────────┐ async  ┌────────┐
│Leader A│◄──────►│Leader B│
└───┬────┘        └───┬────┘
 followers         followers
```

Benefits: local write latency in every region, and each datacentre keeps working if the link between them fails. Also the model behind offline-first apps (each device is a "leader") and collaborative editing.

The cost: **write conflicts**. Two users edit the same record in different regions at the same moment; both writes succeed locally, then collide.

Conflict resolution strategies:

- **Last write wins (LWW)**: highest timestamp wins. Simple, but silently drops data, and clock skew decides the "winner".
- **Merge**: e.g. union of shopping cart items, or application callbacks.
- **CRDTs**: data types (counters, sets, text) designed so concurrent updates merge deterministically. Used by Riak, Redis Enterprise active-active, and collaborative-editing libraries such as Automerge and Yjs.
- **Avoid conflicts**: route all writes for a given record to one "home" region.

Examples: MySQL/MariaDB multi-source setups, Postgres with BDR/pgEdge, CouchDB, and DynamoDB global tables (LWW in their default multi-region eventually consistent mode).

## Key takeaways
- Several leaders can accept local writes during an inter-region partition.
- Last-write-wins converges by discarding competing values and depends on timestamp ordering.
- Merging, CRDTs or a home region make different trade-offs for the application.

## Further reading
- [DeCandia et al.: Dynamo, Amazon's highly available key-value store](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [docs.aws.amazon.com: globaltables_HowItWorks](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/globaltables_HowItWorks.html)
