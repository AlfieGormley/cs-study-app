---
id: cs2-video-streaming
title: Video streaming (YouTube / Netflix)
level: intermediate
minutes: 16
summary: Design a video platform end to end, covering resumable upload, a chunked transcoding pipeline, adaptive bitrate with HLS/DASH, and a CDN strategy like Netflix Open Connect.
---

Video streaming is the classic "bandwidth is the system" design. The metadata service is a fairly ordinary CRUD app. What makes it hard is the **bytes**: petabytes arriving every day that must be transcoded, and hundreds of petabytes leaving every day that must reach phones on flaky 4G without stalling.

A strong answer spends little time on the metadata tables and most of its time on three pipelines: **upload → transcode → deliver**.

## Requirements

### Functional
- Creators upload videos (up to several hours long, many GB).
- Viewers watch on any device, with playback that adapts to their network.
- Search and browse metadata: title, description, thumbnails.
- Record view counts and watch progress ("resume where you left off").

### Non-functional
- **Playback start under 2 s**, and rebuffering kept to a tiny fraction of watch time. This is the metric that drives engagement.
- **Very high availability for playback.** A short delay in a new upload becoming watchable is fine; failed playback is not.
- **Durability**: never lose an uploaded original.
- Read-heavy: views outnumber uploads by many orders of magnitude.
- Cost matters a lot. Egress and transcoding compute are the main bills.

Clarify scope early. YouTube-style means a huge long tail of user uploads. Netflix-style means a small, curated catalogue (tens of thousands of titles) watched by a huge audience. The CDN strategy is very different for each.

## Back-of-the-envelope

Assume a YouTube-scale platform.

**Uploads.** In 2019 YouTube said that more than 500 hours of video were uploaded every minute. Use that dated figure as an illustrative planning input, not a measurement of current upload volume.

First, turn the per-minute upload rate into hours of video per day, because storage is planned per day. A day has 24 × 60 = 1,440 minutes.

```formula
H_day = H_min × 1,440 min/day
H_day = 500 h/min × 1,440 min/day
H_day = 720,000 h/day
where
H_day: hours of new video uploaded per day, in hours per day (h/day)
H_min: hours of new video uploaded per minute, in hours per minute (h/min); here 500
h: hours of video playing time
min: minutes
day: one day of 24 hours (1,440 minutes)
In words: 500 hours arriving every minute, for all 1,440 minutes of a day, is 720,000 hours of new video a day.
```

Next, work out how many bytes one hour of source video takes. A video's bitrate is given in bits per second, but storage is counted in bytes, and one byte is 8 bits, so you divide by 8 at the end. Assume an average source of about 10 megabits per second (Mbps), typical of a 1080p upload.

```formula
S_hour = r × t / 8
S_hour = 10,000,000 b/s × 3,600 s / 8
S_hour = 4,500,000,000 B ≈ 4.5 GB
where
S_hour: the size of one hour of source video, in bytes (B)
r: the source bitrate, in bits per second (b/s); here 10 Mbps = 10,000,000 b/s
t: the length of the video, in seconds (s); one hour is 3,600 s
8: the number of bits in one byte
b/s: bits per second; a bit is a single 0 or 1
s: seconds
B: bytes; one byte is 8 bits
GB: gigabytes; 1 GB = 1,000,000,000 bytes
≈: approximately equal to
In words: a 10 megabit-per-second video uses 4.5 gigabytes for every hour of footage.
```

Multiply the two to get the daily volume of original uploads:

```formula
S_day = H_day × S_hour
S_day = 720,000 h/day × 4.5 GB/h
S_day = 3,240,000 GB/day ≈ 3.2 PB/day
where
S_day: bytes of original uploads stored per day, in gigabytes per day (GB/day)
H_day: hours uploaded per day; here 720,000 h/day
S_hour: bytes per hour of source; here 4.5 GB per hour (GB/h)
h: hours
GB: gigabytes; 1 GB = 1,000,000,000 bytes
PB: petabytes; 1 PB = 1,000,000 GB = 10^15 bytes
day: one day
≈: approximately equal to
In words: 720,000 hours a day at 4.5 GB an hour is about 3.2 petabytes of originals every day.
```

For a hypothetical storage model, assume additional renditions bring total new storage to **6–8 PB/day**. This multiplier depends on the actual ladders/codecs and is not a measured YouTube ratio. Over a year that is:

```formula
S_year = S_day × 365 days
S_year = 6 PB/day × 365 = 2,190 PB ≈ 2.2 EB
S_year = 8 PB/day × 365 = 2,920 PB ≈ 2.9 EB
where
S_year: new storage needed per year, in petabytes (PB) or exabytes (EB)
S_day: total new storage per day including renditions, in petabytes per day (PB/day); here 6 to 8
PB: petabytes; 1 PB = 10^15 bytes
EB: exabytes; 1 EB = 1,000 PB = 10^18 bytes
days: days in the year (365)
day: one day
≈: approximately equal to
In words: adding 6 to 8 petabytes a day for a year comes to about 2 to 3 exabytes, before any replication copies.
```

So the platform grows by **about 2–3 EB** a year, before replication. These are deliberately rough: real sources range from 5 Mbps phone clips to 50+ Mbps 4K. Clip duration does not itself reduce the assumed bytes per hour; source bitrate and format determine that.

**Viewing.** Say 200 M (200 million) daily viewers each watching 1 hour at an average 3 Mbps.

The network has to be sized for how many people are watching *at the same moment*, not per day. If viewing were spread evenly over the day, the average number watching at once is total viewing hours divided by the hours in a day:

```formula
C_avg = D × T_watch / 24 h
C_avg = 200 M × 1 h / 24 h ≈ 8.3 M
C_peak ≈ 2 × C_avg ≈ 17 M
where
C_avg: average number of viewers watching at the same moment
C_peak: number watching at once at the busiest time of day; assumed about twice the average
D: daily viewers, people who watch at least once a day; here 200 M
T_watch: viewing time per viewer per day, in hours (h); here 1 h
24 h: the hours in one day
h: hours
M: million (1,000,000)
≈: approximately equal to
In words: 200 million people each watching an hour a day means about 8.3 million watching at any moment on average, and roughly 17 million at the evening peak.
```

The "2x" peak factor is an assumption: real daily curves depend on time zones and audience. Egress (data sent out of your network to viewers) at peak is the number watching times the bitrate each one receives:

```formula
E_peak = C_peak × r
E_peak = 17 M × 3 Mbps ≈ 51 Tbps ≈ 50 Tbps
where
E_peak: peak egress, in terabits per second (Tbps)
C_peak: viewers watching at once at peak; here about 17 M
r: average bitrate each viewer streams, in megabits per second (Mbps); here 3
M: million
Mbps: megabits per second; 1 Mbps = 1,000,000 bits per second
Tbps: terabits per second; 1 Tbps = 1,000,000 Mbps
≈: approximately equal to
In words: 17 million streams at 3 megabits per second each add up to about 50 terabits per second leaving the platform.
```

Daily egress, in bytes, is every viewer's watch time in seconds times the bitrate, divided by 8 to turn bits into bytes:

```formula
E_day = D × t × r / 8
E_day = 200 M × 3,600 s × 3 Mbps / 8
E_day = 2.7 × 10^17 B ≈ 270 PB
where
E_day: data sent to viewers per day, in bytes (B)
D: daily viewers; here 200 M
t: viewing time per viewer per day, in seconds (s); 1 hour is 3,600 s
r: average bitrate, in megabits per second (Mbps); here 3
8: bits per byte
M: million
Mbps: megabits per second; 1 Mbps = 1,000,000 bits per second
s: seconds
B: bytes
PB: petabytes; 1 PB = 10^15 bytes
≈: approximately equal to
In words: 200 million hours of viewing at 3 megabits per second is about 270 petabytes of video delivered every day.
```

Serving 50 Tbps to a global audience makes geographic distribution, network capacity and egress cost central design concerns. A CDN also reduces network distance; 50 Tbps is not a universal single-data-centre limit.

**Transcoding.** As a working assumption (it varies hugely with presets and hardware), assume 15 core-hours per source hour across the chosen ladder. A core-hour is one CPU core busy for one hour. This is a hypothetical input, not a hardware/codec benchmark.

To find how many cores must run around the clock, multiply total compute per day and divide by the 24 hours each core can work:

```formula
N_cores = H_day × c / 24 h
N_cores = 720,000 × 15 core-h / 24 h
N_cores = 10,800,000 core-h / 24 h
N_cores = 450,000 cores
where
N_cores: CPU cores that must run non-stop to keep up
H_day: hours of source video uploaded per day; here 720,000
c: compute needed per hour of source, in core-hours; here 15
core-h: core-hours: one processor core busy for one hour
24 h: the hours in a day each core can work
h: hours
cores: processor cores, each able to run one stream of work at a time
In words: 10.8 million core-hours of work a day needs about 450,000 cores running all day.
```

Even if the assumption is off by 2x either way, the answer is hundreds of thousands of cores. This is why platforms spend expensive codecs (AV1, heavy VP9 presets) on videos that actually get watched.

## API design

```
POST /v1/uploads
  { title, size_bytes, content_type }
  -> { upload_id, upload_url }

PUT  {upload_url}
  Content-Range: bytes 0-8388607/...
  (GCS-style resumable chunks, e.g. 8 MiB)

POST /v1/uploads/{id}/complete
  -> { video_id, status: "processing" }

GET  /v1/videos/{video_id}
  -> metadata, status, thumbnails

GET  /v1/videos/{video_id}/play
  -> { manifest_url (signed, CDN),
       drm_licence_url }

POST /v1/videos/{video_id}/progress
  { position_s }
```

Two points matter here. First, the upload URL points straight at **object storage** (a pre-signed S3/GCS URL or a resumable-upload endpoint), so multi-GB bodies never pass through your API servers. Second, `/play` doesn't stream video. It returns a **manifest URL** on the CDN, and the player does the rest.

## Data model

| Store | What lives there |
|---|---|
| Sharded SQL | videos, channels, renditions |
| Object store | originals, segments |
| Wide-column / KV | watch progress, counters |
| Search index | titles, tags, captions |

```
videos(video_id PK, owner_id, title,
       status, duration_s, created_at)
renditions(video_id, codec, height,
           bitrate_kbps, manifest_path)
watch_progress(user_id, video_id,
               position_s, updated_at)
```

YouTube scaled its MySQL metadata tier by building Vitess, a sharding layer that is now an open-source CNCF project. Shard `videos` by `video_id` and `watch_progress` by `user_id`, because the access patterns are "load this video" and "load this user's history".

## High-level architecture

```
 Creator                          Viewer
    |                               |
    v                               v
+--------+   +-------+        +---------+
| Upload |-->| Blob  |        |   CDN   |
|  API   |   | store |        |  edge   |
+--------+   +-------+        +---------+
    |            |  ^               | miss
    v            v  |               v
+--------+   +---------+      +---------+
| Queue  |-->|Transcode|      | Origin/ |
| (jobs) |   | workers |----->| shield  |
+--------+   +---------+      +---------+
    |
    v
+----------+  +--------+
| Metadata |  | Search |
|   DB     |  | index  |
+----------+  +--------+
```

## Deep dive 1: the upload and transcoding pipeline

### Resumable upload

A 4 GB upload from a phone *will* get interrupted. Use a resumable protocol (Google's resumable upload API, tus, or S3 multipart). Offset-based protocols such as tus/GCS resumable upload report committed offsets. S3 multipart instead tracks an upload ID, numbered parts and their returned ETags/checksums; parts can arrive out of order and retry individually. A generic presigned S3 PUT does not implement a Content-Range resumable session.

When the upload completes, the storage service fires an event ("object created") onto a queue. Don't have the client call the transcoder directly. The queue makes the pipeline durable and lets you absorb upload spikes.

### Split, transcode in parallel, stitch

Encoding a 2-hour film serially on one machine takes hours. Instead:

1. **Validate and probe** the file (container, codec, duration, corrupt frames).
2. **Split** it into chunks of a few seconds, cut on keyframe (GOP) boundaries using independently decodable boundaries (such as closed GOPs/appropriate random-access points), aligned across renditions. An arbitrary keyframe in an open GOP may still depend on other frames.
3. **Fan out** one task per (chunk × rendition) to a worker pool. A 2-hour film in 4 s chunks across 6 renditions is about 10,800 tasks (worked out below), giving parallel work units; completion time depends on actual encoder throughput, available workers, input decoding and assembly.
4. **Assemble** the outputs into packaged segments and write the manifests.
5. Generate thumbnails, run content checks (copyright matching, safety classifiers) and extract captions in parallel branches.
6. Mark the video `ready` in the metadata DB.

The task count in step 3 is the number of chunks times the number of renditions:

```formula
N_tasks = (T / c) × R
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

### Spending compute where views are

Assume a skewed popularity distribution for this design; measure the actual catalogue before allocating expensive encode work. A sensible policy:

- On upload, encode a fast H.264 ladder so the video is watchable within minutes.
- When a video crosses a view threshold, re-encode it in VP9/AV1. Potential bitrate savings and encoding cost depend on content, encoder settings and quality metrics; benchmark a representative corpus before choosing a migration threshold. Re-encode only when expected egress savings exceed compute, storage and operational costs for supported playback devices.

## Deep dive 2: adaptive bitrate streaming

Progressive download of a single MP4 can't adapt to the network. **Adaptive bitrate (ABR)** streaming encodes the video at several bitrates, splits each into short segments, and lets the **client** choose a rendition per segment.

### HLS and DASH

- **HLS** (Apple) uses a *master playlist* (`.m3u8`) listing the variants, and a *media playlist* per variant listing segment URLs. Apple's HLS authoring specification recommends a target segment duration of 6 seconds.
- **MPEG-DASH** uses an XML *MPD* manifest with the same idea.
- **CMAF** standardises fragmented-MP4 segments, so one set of files can serve both HLS and DASH. This avoids duplicate segment copies when codec, encryption and player compatibility allow both protocols to share them; it does not universally halve total storage.

```
#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=1000000
480p/index.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=5000000
1080p/index.m3u8
```

Because segments are plain HTTP objects with immutable URLs, any HTTP cache or CDN can serve them. This is the main reason HTTP streaming won over specialised streaming protocols such as RTMP.

### How the player chooses

- **Throughput-based**: measure how fast recent segments downloaded and pick the highest bitrate below, say, 80% of that. It reacts quickly but oscillates on noisy links.
- **Buffer-based** (Netflix's BBA research): choose the bitrate from buffer occupancy. With a nearly empty buffer, play safe. With a full buffer, go high. Buffer-aware policies can reduce oscillation; compare stability, startup and stalls on representative traces.
- Player implementations vary: many combine bandwidth estimates with buffer or switching constraints. Startup choices depend on their configuration and history.

Segment length is a trade-off. Short segments (2 s) adapt quickly and cut live latency, but they mean more requests and slightly worse compression, because there are more keyframes. Long segments (10 s) are efficient but adapt slowly.

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

## View counts and progress

Writing a row per view at 17 M concurrent viewers is wasteful. Players emit heartbeats every few tens of seconds into a stream such as Kafka. A stream processor deduplicates (one view per session, with a product-specific minimum watch time and additional abuse controls), aggregates per video per minute, and writes counters. Displayed counts can lag by minutes. A lag of minutes may be acceptable for a display counter; billing or audit metrics may need another contract.

The numbers show why. The event rate is the number of viewers divided by the gap between each viewer's heartbeats:

```formula
E = C / i
E = 17,000,000 / 30 s ≈ 570,000 events/s
where
E: heartbeat events arriving per second
C: viewers watching at the same moment; here 17 million at peak
i: the interval between one player's heartbeats, in seconds (s); here 30
s: seconds
events: heartbeat messages
≈: approximately equal to
In words: 17 million players each reporting once every 30 seconds send about 570,000 events every second.
```

That is a workload to benchmark for the chosen partitioning and durability settings, but a viral video would turn `UPDATE videos SET views = views + 1` into a single hot row taking tens of thousands of writes a second. Pre-aggregating in the stream turns that into one write per video per minute.

Watch progress can use a versioned KV record keyed by `(user_id, video_id)`. Define ordering across sessions/devices; client-clock LWW can let a delayed update overwrite newer progress, while taking the maximum position breaks intentional rewinds. It is debounced on the client so it isn't written every second.

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

## Key takeaways
- The design is dominated by bytes. Estimate peak egress first (tens of Tbps) and let that justify the CDN.
- Upload directly to object storage with a resumable protocol, then drive a queue-backed, idempotent DAG of chunked transcode tasks.
- ABR (HLS/DASH, ideally CMAF) puts the client in charge of choosing bitrates segment by segment, and makes video cacheable by ordinary HTTP caches.
- Spend expensive encoding (AV1, per-title, per-shot) in proportion to popularity. Use a measured break-even model; it need not pay off for every video or device mix.
- A curated catalogue (Netflix) can be proactively pushed to ISP-embedded caches off-peak. A long-tail catalogue (YouTube) needs tiered pull-through caching with an origin shield.

> **Content gap:** no reproducible encoder benchmark, CDN hit-rate measurement or current egress quote is supplied. Capacity, bitrate and cost calculations use explicit scenario inputs. Historical platform descriptions do not establish current internal implementations.

## Further reading
- [Netflix Open Connect overview](https://openconnect.netflix.com/en/)
- [HTTP Live Streaming (Apple developer docs)](https://developer.apple.com/documentation/http-live-streaming)
- [Adaptive bitrate streaming (Wikipedia)](https://en.wikipedia.org/wiki/Adaptive_bitrate_streaming)
- [Dynamic Adaptive Streaming over HTTP (Wikipedia)](https://en.wikipedia.org/wiki/Dynamic_Adaptive_Streaming_over_HTTP)
- [Content delivery network (Wikipedia)](https://en.wikipedia.org/wiki/Content_delivery_network)
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
