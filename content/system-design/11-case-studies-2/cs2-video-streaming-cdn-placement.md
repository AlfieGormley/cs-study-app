---
id: cs2-video-streaming-cdn-placement
title: Video CDN placement and access
level: intermediate
minutes: 3
summary: Match catalogue popularity to proactive placement or tiered demand-driven caching.
sourceLesson: cs2-video-streaming
---

## Deep dive 3: CDN strategy

At about 50 Tbps peak, the CDN *is* the product.

### Netflix Open Connect

Netflix built its own CDN. **Open Connect Appliances (OCAs)** are storage-heavy servers given free of charge to ISPs and installed *inside* their networks or at internet exchange points.

- The **control plane** (catalogue, auth, playback steering, recommendations) runs in AWS.
- The **data plane** (the video bytes) is served almost entirely from OCAs.
- Because the catalogue is curated and popularity is predictable, Netflix **proactively fills** OCAs overnight, during off-peak hours, with what each region is expected to watch tomorrow. Fills are cheap off-peak, and cache-hit video traffic can stay inside a participating ISP’s network; misses and other deployment arrangements still need upstream connectivity.
- At playback, the steering service returns URLs for the OCAs best placed for that client, ranked by health, load and network proximity.

### YouTube-style long tail

YouTube can't predict which of millions of new uploads will be watched, a long-tail design can use **pull-through caching** in tiers; Google Global Cache documents caching popular Google content inside ISP networks:

```
client -> ISP edge cache (e.g. Google
          Global Cache)
       -> regional cache / shield
       -> origin object store
```

The head of the distribution (viral and popular videos) lives at the edge with workload-dependent hit rates. The long tail is fetched from regional caches or origin on demand. An **origin shield** layer collapses many edge misses for the same segment into a single origin fetch.

### Security on the CDN

Manifests and segment URLs carry **signed tokens** with an expiry, so URLs can't be hot-linked forever. Paid content is encrypted (Widevine, FairPlay, PlayReady DRM), with keys from a separate licence server. For this protected-media path, cache encrypted segments; manifests, metadata and other CDN content need not be encrypted media ciphertext. Validate authorization separately from the shared object cache key.

## Bottlenecks and trade-offs

- **Egress cost** dominates. The levers are better codecs, per-title encoding, and ISP-embedded caches that avoid transit fees.
- **Transcode backlog** during spikes. Prioritise short videos and popular creators, and autoscale on queue depth using spot or pre-emptible instances, since tasks are idempotent and retryable.
- **Cold start for the long tail**. The first viewer of an obscure video pays origin latency. Prefetch the first few segments of each rendition into the regional tier.
- **Storage growth** of roughly 2–3 EB/year. Move old, rarely watched renditions to colder tiers, and consider deleting high-bitrate renditions of dead videos and re-transcoding on demand.

## Evolving at 10x

- **500 Tbps peak**: push caches deeper into ISPs (the Open Connect model), and use multicast-like fills between caches.
- **Live streaming**: use LL-HLS or low-latency DASH with partial segments, an ingest tier that accepts RTMP/SRT, and real-time transcoding (no time to split and fan out a finished file).
- **Global metadata**: replicate read-mostly metadata to every region, with a single write region per shard.
- **ML everywhere**: predictive prefetch and quality-per-bit models (Netflix's VMAF metric) to tune the ladder automatically.

> **Content gap:** no reproducible encoder benchmark, CDN hit-rate measurement or current egress quote is supplied. Capacity, bitrate and cost calculations use explicit scenario inputs. Historical platform descriptions do not establish current internal implementations.

## Key takeaways
- Curated predictable demand makes off-peak placement useful; a long tail also needs misses.
- Origin shields coalesce requests, subject to routing, eviction and failure behaviour.
- Check viewer authorisation separately from shareable encrypted segment caching.

## Further reading
- [Netflix Open Connect overview](https://openconnect.netflix.com/en/)
- [Content delivery network (Wikipedia)](https://en.wikipedia.org/wiki/Content_delivery_network)
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Open Connect technical overview](https://openconnect.netflix.com/Open-Connect-Overview.pdf)
