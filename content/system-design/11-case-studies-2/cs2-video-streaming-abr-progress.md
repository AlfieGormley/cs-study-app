---
id: cs2-video-streaming-abr-progress
title: Adaptive playback and view aggregation
level: intermediate
minutes: 4
summary: Choose rendition quality on the client and aggregate popular-video counters.
sourceLesson: cs2-video-streaming
---

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

Because segments are plain HTTP objects with immutable URLs, any HTTP cache or CDN can serve them. Cacheability and reuse of HTTP infrastructure are important practical advantages over specialised streaming delivery protocols such as RTMP.

### How the player chooses

- **Throughput-based**: measure how fast recent segments downloaded and pick the highest bitrate below, say, 80% of that. It reacts quickly but oscillates on noisy links.
- **Buffer-based** (Netflix's BBA research): choose the bitrate from buffer occupancy. With a nearly empty buffer, play safe. With a full buffer, go high. Buffer-aware policies can reduce oscillation; compare stability, startup and stalls on representative traces.
- Player implementations vary: many combine bandwidth estimates with buffer or switching constraints. Startup choices depend on their configuration and history.

Segment length is a trade-off. Short segments (2 s) offer more adaptation opportunities and can reduce live latency under the chosen buffering policy. They mean more requests. Compression may worsen if random-access spacing also shortens; segment duration alone does not prove a keyframe increase. Long segments (10 s) reduce request frequency but offer fewer switching opportunities.

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

## Key takeaways
- HLS and DASH can share compatible CMAF media while retaining their own manifests.
- Buffer-aware selection and switching hysteresis can reduce noisy quality changes.
- Aggregate deduplicated views rather than serialising every start on one hot SQL row.

## Further reading
- [HTTP Live Streaming (Apple developer docs)](https://developer.apple.com/documentation/http-live-streaming)
- [Adaptive bitrate streaming (Wikipedia)](https://en.wikipedia.org/wiki/Adaptive_bitrate_streaming)
- [Dynamic Adaptive Streaming over HTTP (Wikipedia)](https://en.wikipedia.org/wiki/Dynamic_Adaptive_Streaming_over_HTTP)
- [RFC 8216: HTTP Live Streaming](https://www.rfc-editor.org/rfc/rfc8216.html)
