---
id: cache-application-and-buffer-caches
title: Compare local caches, shared caches and buffer pools
level: basic
minutes: 2
summary: Choose between per-process and remote application caches, and check database memory before adding a new service.
sourceLesson: cache-fundamentals
---

Application caches store values your code chooses; database buffer pools store recently used pages. Both can avoid backend work, but they have different sharing and consistency costs.

### Application cache

This is the cache you code against. There are two flavours:

- **In-process** (a dictionary, Caffeine in Java, `functools.lru_cache` in Python). Avoids a network hop and can avoid serialisation; actual lookup cost depends on the implementation. But each server has its own copy, so 50 servers means 50 copies that can disagree, and memory is limited to one process.
- **Remote / distributed** (Redis, Memcached). A shared service (possibly with multiple replicas), accessed over the network at deployment-dependent latency. Survives app deploys and scales independently.

Many systems use both: a tiny in-process cache with a short TTL (say 1–5 seconds) in front of Redis, to absorb very hot keys.

### Database buffer pool

Databases cache too. PostgreSQL keeps recently used pages, normally 8 KiB (8,192 bytes) in `shared_buffers` and also relies on the operating system's page cache. PostgreSQL's docs suggest starting `shared_buffers` at about 25% of RAM on a dedicated server with at least 1 GB of RAM. MySQL's InnoDB has the **buffer pool**, which on a dedicated host is often given up to about 80% of RAM. Cached pages avoid storage reads, but the speedup depends on query execution, hardware and the rest of the workload.

> [!tip] The "free" cache
> Before adding Redis, check that your database's working set fits in RAM. Sizing the buffer pool correctly is often the cheapest caching win available.

## Key takeaways
- A local cache avoids network and decoding work but gives every process its own potentially stale copy.
- Redis or Memcached shares cached values across application servers and scales separately from them.
- Size and measure the database buffer pool before assuming an additional cache is the cheapest improvement.

## Further reading
- [PostgreSQL resource consumption (shared_buffers)](https://www.postgresql.org/docs/current/runtime-config-resource.html)
- [InnoDB buffer pool — MySQL](https://dev.mysql.com/doc/refman/8.4/en/innodb-buffer-pool.html)
- [Caching overview — AWS](https://aws.amazon.com/caching/)
