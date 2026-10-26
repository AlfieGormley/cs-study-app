---
id: fund-estimation-media-bandwidth
title: Estimate media storage and delivery bandwidth
level: intermediate
minutes: 3
summary: Explain why media can dominate storage, repeated delivery drives egress, and simultaneous viewers determine streaming demand.
sourceLesson: fund-estimation
---

The preceding record estimate is only part of a media service. Large objects and repeated delivery can dominate the storage and network budget even when the metadata database is modest.

## A social feed: separate metadata from media

Assume 200 million daily active users, each posting twice and viewing 100 posts daily. Ten per cent of posts contain a 500 KB photo; text and metadata take about 1 KB per post. These are exercise inputs, with decimal size units.

Using a rounded 100,000 seconds per day gives about **4,000 posts/s** and **200,000 post views/s** on average. An assumed threefold peak raises these to about 12,000 and 600,000 respectively. The read-heavy pattern makes caching and precomputation candidates, subject to freshness and fan-out costs.

The important storage result is the imbalance:

| One-copy payload | Per day | Per 365-day year |
|---|---|---|
| Text and metadata | 400 GB | About 150 TB |
| Photos | 20 TB | About 7.3 PB |

Photos dominate even though they occur in a minority of posts. Keeping large media in object storage and keeping references and searchable metadata in the database is a useful starting design; the estimate does not require every byte to live in a database disk.

## Delivered bytes differ from stored bytes

Assume ten per cent of the 20 billion daily views fetch a photo. That delivers about **1 PB per day**, or roughly **80 Gbps** using the same rounded day. A photo stored once can be downloaded many times, so upload volume alone cannot size egress.

A CDN can serve repeat requests near users and reduce origin traffic. Its cache hit rate changes how much delivery load reaches the origin; it does not remove the bytes users receive. Measure geography, cacheability, payload sizes and peak demand.

> [!tip] Say what an estimate changes
> A large result should lead to a resource or architecture question: where are the objects stored, which traffic can an edge cache serve, and can the origin survive misses? It should not automatically lead to sharding the metadata database.

## A streaming service: concurrency matters

Assume **one million concurrent viewers**, each consuming an average **5 Mbps** stream. Their combined peak delivery is **5 Tbps**, equivalent to **625 GB/s**. These assumed values explain why delivery placement and bandwidth can dominate a streaming design.

The number of viewers watching at once matters here, rather than daily active users or uploads. Higher bitrate or more simultaneous viewers raises delivery demand directly. Provision measured server capacity with headroom and geographic redundancy; one generic network-card rate cannot determine the fleet. Netflix's Open Connect places delivery appliances inside ISP networks to serve traffic close to viewers.

## Key takeaways
- Photos can dominate storage even when only a small share of posts contain them.
- Estimate media bytes delivered as well as bytes retained, with bits and bytes kept distinct.
- A CDN supports offload, geography and redundancy; assumed NIC rates need workload-specific validation.

## Further reading
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Netflix Open Connect](https://openconnect.netflix.com/en/)
