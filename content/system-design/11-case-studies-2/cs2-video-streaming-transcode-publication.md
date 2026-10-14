---
id: cs2-video-streaming-transcode-publication
title: Parallel transcoding and safe publication
level: intermediate
minutes: 4
summary: Version independent encode tasks and publish only validated winning outputs.
sourceLesson: cs2-video-streaming
---

**Transcoding.** As a working assumption (it varies hugely with presets and hardware), assume 15 core-hours per source hour across the chosen ladder. A core-hour is one CPU core busy for one hour. This is a hypothetical input, not a hardware/codec benchmark.

To find how many cores must run around the clock, multiply total compute per day and divide by the 24 hours each core can work:

```formula
N_cores = (H_in × c) / T_day
N_cores = (720,000 h × 15 core-h/h) / (24 h)
N_cores = 10,800,000 core-h / (24 h)
N_cores = 450,000 cores
where
N_cores: continuously busy processor cores needed to finish this one day's incoming work within the same day
H_in: total source-video duration arriving in the planned day, 720,000 hours (h)
c: compute per source hour, 15 core-hours per hour of video (core-h/h); an assumed encoder input
T_day: available operating time within that day, 24 hours (h)
core-h: a core-hour, one processor core busy for one hour
h: an hour
cores: processor cores being counted
In words: 10.8 million core-hours of daily encoding work require 450,000 cores each busy for twenty-four hours, under this assumed compute model.
```

Even if the assumption is off by 2x either way, the answer is hundreds of thousands of cores. This is why platforms spend expensive codecs (AV1, heavy VP9 presets) on videos that actually get watched.

### Split, transcode in parallel, stitch

Encoding a 2-hour film serially on one machine takes hours. Instead:

1. **Validate and probe** the file (container, codec, duration, corrupt frames).
2. **Split** it into chunks of a few seconds, cut on keyframe (GOP) boundaries using independently decodable boundaries (such as closed GOPs/appropriate random-access points), aligned across renditions. An arbitrary keyframe in an open GOP may still depend on other frames.
3. **Fan out** one task for each chunk-and-rendition combination to a worker pool. A 2-hour film in 4 s chunks across 6 renditions is about 10,800 tasks (worked out below), giving parallel work units; completion time depends on actual encoder throughput, available workers, input decoding and assembly.
4. **Assemble** the outputs into packaged segments and write the manifests.
5. Generate thumbnails, run content checks (copyright matching, safety classifiers) and extract captions in parallel branches.
6. Mark the video `ready` in the metadata DB.

The task count in step 3 is the number of chunks times the number of renditions:

```formula
N_tasks = (T / c)R
N_tasks = (7,200 s / 4 s) × 6
N_tasks = 1,800 × 6 = 10,800 tasks
where
N_tasks: independent encoding tasks
T: length of the film, in seconds (s); 2 hours is 7,200 s
c: length of one chunk, in seconds (s); here 4
R: number of renditions (quality levels) in the ladder; here 6
s: seconds
tasks: the unit being counted (encoding jobs)
In words: 1,800 four-second chunks, each encoded at 6 quality levels, gives 10,800 tasks.
```

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

Netflix moved from one fixed ladder to **per-title encoding**: a cartoon with flat colours can look excellent at 1080p for well under the fixed ladder's bitrate, while grainy action footage needs far more. They later moved to **shot-based** encoding, which chooses settings per scene. The pay-off is the same quality for fewer bits, which saves egress on every future view.


## Key takeaways
- Chunk and rendition fan-out creates independently retryable work.
- Use independently decodable aligned boundaries; arbitrary open-GOP keyframes are insufficient.
- Publish immutable attempt objects through a conditional winning-result pointer.

## Further reading
- [HTTP Live Streaming (Apple developer docs)](https://developer.apple.com/documentation/http-live-streaming)
- [Netflix Open Connect overview](https://openconnect.netflix.com/en/)
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
