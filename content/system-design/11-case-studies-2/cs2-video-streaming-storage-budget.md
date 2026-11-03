---
id: cs2-video-streaming-storage-budget
title: Video storage capacity
level: intermediate
minutes: 4
summary: Estimate original and rendition storage from explicitly dated upload inputs.
sourceLesson: cs2-video-streaming
---

## Storage grows with the catalogue

Uploading a video creates several storage obligations: the original, its delivery renditions, thumbnails and metadata, and the copies or erasure-coded fragments needed for durability. Count those separately. An original is not a delivery ladder, and a ladder is not a replica policy.

For an **illustrative** large platform, suppose creators supply 720,000 hours of video each day and originals average 10 Mbps. That is about 3.24 decimal petabytes of original payload per day. This is a chosen workload, not a current YouTube measurement or a universal bitrate for 1080p video.

| Budget input | Why it changes storage |
|---|---|
| Uploaded duration | More source hours add more original bytes |
| Source bitrate | Higher bitrate adds bytes even if duration is unchanged |
| Rendition ladder and codecs | Each retained encode adds another representation |
| Durability scheme | Replication or erasure coding adds physical overhead |
| Retention and deletion | Keeping everything makes the accumulated catalogue grow |

Measure rendition sizes on representative material. A complex sports clip and a static lecture need not use the same bitrate for comparable quality. Adding another codec for compatible devices may save delivery bandwidth while increasing stored bytes if the old codec remains available.

## Turn a storage total into a policy

Separate **daily growth** from **total retained storage**. A daily ingest estimate is not a one-time capacity requirement. Account for deletion, retention, indexes, unfinished uploads and temporary transcode outputs as well as completed media. Budget physical overhead once rather than multiplying the same replica factor twice.

Keep originals if the product needs future re-encoding. For seldom-watched renditions, compare keeping a ready copy with regenerating it after a request. Colder storage can reduce cost but adds retrieval delay and possibly retrieval charges; that choice must fit the playback promise. Monitor growth by object category so a temporary-output leak cannot hide inside an apparently plausible total.

## Key takeaways
- Convert incoming video hours into source bytes using the assumed bitrate.
- Model renditions and replication separately rather than treating a multiplier as measured.
- A dated upload figure is a planning example rather than current platform telemetry.

## Further reading
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Netflix Open Connect overview](https://openconnect.netflix.com/en/)
- [YouTube 2019 official historical statements](https://youtube.googleblog.com/2019/?hl=ms)
- [S3 multipart lifecycle and unfinished uploads](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html)
