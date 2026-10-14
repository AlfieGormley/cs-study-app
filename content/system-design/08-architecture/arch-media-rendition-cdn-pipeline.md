---
id: arch-media-rendition-cdn-pipeline
title: Publishing renditions through a CDN
level: intermediate
minutes: 3
summary: Build a retryable media pipeline that produces adaptive renditions and protects private delivery.
sourceLesson: arch-object-storage-media
---

After a validated upload, viewers need deliverable images or video renditions. This unit connects asynchronous processing to versioned outputs and CDN access.

## Serving media: CDNs

Object storage can serve clients directly. To improve geographic delivery and reduce repeated origin work, put a **CDN** (CloudFront, Cloudflare, Fastly, Akamai) in front:

- Nearby edge caches can reduce network distance for cache hits; measure the actual latency and hit rate.
- The origin sees misses, revalidations and requests that bypass caching.
- For private content, use **signed CDN URLs or cookies** rather than making the bucket public.
- Use **immutable keys** (`img/42/v3/abc.jpg` with a content hash) to avoid routine invalidation when publishing a new version. Removal or access-policy changes may still require invalidation or other controls.

## Transcoding pipelines

Raw uploads aren't what you want to serve. A phone video might be 4K HEVC at 50 Mbit/s; viewers need everything from 240p on a weak 3G link to 4K on a TV. So you **transcode** into a ladder of renditions and package them for **adaptive bitrate streaming** (HLS or DASH), where the video is cut into segments of a few seconds and the player switches quality per segment based on bandwidth.

```
 upload -> [raw bucket]
              | ObjectCreated event
              v
           [queue]
              |
   [transcode workers, autoscaled]
     split -> encode chunks ->
     240p / 480p / 720p / 1080p
              |
              v
   [output bucket] -> [CDN] -> player
   (HLS .m3u8 playlist + .ts/.m4s
    segments)
```

Design points:

- **Event-driven and asynchronous**: the upload API returns immediately; the video shows "processing" until done.
- **Parallelise by chunk**: split work at boundaries the video codec allows, encode chunks concurrently, then assemble and package them. Handle keyframes/GOPs, timestamps, audio alignment and rendition boundaries; speedup depends on available workers and split/encode/assembly costs.
- **Idempotent, retryable steps**: workers can die (often on cheap spot instances). Include source version and encoding settings in output identity. Deterministic names alone do not guarantee idempotency: write temporary outputs, validate them, and conditionally publish a manifest so a stale retry cannot replace newer work.
- **A workflow engine** (Step Functions, Temporal, or a simple state table) tracks each video's progress through stages: validate → transcode → thumbnail → moderate → publish.
- **Prioritise**: publish a low-resolution rendition first so the video is watchable sooner, and fill in higher qualities afterwards.

> [!example] Image pipeline
> Instagram-style photos follow the same shape on a smaller scale: upload original via presigned URL → event → workers generate 150px, 640px and 1080px versions in WebP/AVIF → write to output bucket → CDN. Some systems resize lazily at the edge instead, generating a size the first time it's requested and caching it.

## Key takeaways
- CDNs reduce repeated origin work for hits; private media needs signed access and protected origin storage.
- Immutable versioned keys simplify publishing new assets without routine cache invalidation.
- Adaptive streaming packages a rendition ladder into short segments for changing bandwidth.
- Chunk workers need codec-safe boundaries, source/version identity and conditional publication to make retries safe.

## Further reading
- [Wikipedia: HTTP Live Streaming](https://en.wikipedia.org/wiki/HTTP_Live_Streaming)
