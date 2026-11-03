---
id: cs2-video-streaming-transcode-publication
title: Parallel transcoding and safe publication
level: intermediate
minutes: 4
summary: Version independent encode tasks and publish only validated winning outputs.
sourceLesson: cs2-video-streaming
---

## Compute follows the chosen quality target

Measure encoding work per source hour on representative content, codecs, presets and hardware. A core-hour is one processor core busy for an hour; the same core-hour count does not imply equal performance across machines. Daily work and available processing time inform fleet size, with headroom for retries and uneven task costs.

Keep the capacity model separate from completion latency. Enough total daily compute does not guarantee that one newly uploaded film becomes ready quickly.

### Split, transcode in parallel, stitch

A long serial encode can delay publication. To expose parallel work:

1. **Validate and probe** the file (container, codec, duration, corrupt frames).
2. **Split** it into chunks of a few seconds, cut on keyframe (GOP) boundaries using independently decodable boundaries (such as closed GOPs/appropriate random-access points), aligned across renditions. An arbitrary keyframe in an open GOP may still depend on other frames.
3. **Fan out** one task for each chunk-and-rendition combination to a worker pool. A 2-hour film in 4 s chunks across 6 renditions is about 10,800 tasks under these illustrative inputs, giving parallel work units; completion time depends on actual encoder throughput, available workers, input decoding and assembly.
4. **Assemble** the outputs into packaged segments and write the manifests.
5. Generate thumbnails, run content checks (copyright matching, safety classifiers) and extract captions in parallel branches.
6. Mark the video `ready` in the metadata DB.

A small chunk can be retried independently, but more tasks also add scheduling, metadata and assembly overhead. Measure both rather than assuming that finer chunks always finish sooner.

Model this as a **DAG** of tasks with a workflow engine. Every task must be **idempotent**, keyed on video/source version, chunk, rendition and encoding profile. Publish only complete validated outputs, using immutable attempt objects plus an atomic winning-result pointer or conditional writes. A deterministic path alone cannot stop a stale attempt overwriting a newer encode.

### The bitrate ladder

An illustrative H.264 ladder (not a universal recommendation):

| Rendition | Bitrate |
|---|---|
| 240p | 0.3 Mbps |
| 480p | 1.0 Mbps |
| 720p | 2.5 Mbps |
| 1080p | 5 Mbps |
| 2160p (4K) | 15 Mbps |

**Per-title encoding** chooses the ladder for each video's content and quality target. **Shot-based encoding** makes choices at scene boundaries. Static and complex motion footage can need different bitrates for comparable quality; measure savings on representative material. These techniques change the encode policy, not the requirement to publish compatible, complete segments.

> [!analogy] Real-world analogy: Publishing a finished edition
> A printer can produce sections independently, but a publisher releases one chosen complete edition.
>
> **How it maps:** Chunk/rendition tasks correspond to separate print jobs; the ready manifest identifies the validated set selected for publication.
>
> **Where it stops:** Physical pages do not model stale network workers. The storage protocol still needs version checks and atomic winner selection.

## Key takeaways
- Chunk and rendition fan-out creates independently retryable work.
- Use independently decodable aligned boundaries; arbitrary open-GOP keyframes are insufficient.
- Publish immutable attempt objects through a conditional winning-result pointer.

## Further reading
- [HTTP Live Streaming (Apple developer docs)](https://developer.apple.com/documentation/http-live-streaming)
- [Netflix Open Connect overview](https://openconnect.netflix.com/en/)
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
- [HLS segment and playlist specification](https://www.rfc-editor.org/rfc/rfc8216.html)
