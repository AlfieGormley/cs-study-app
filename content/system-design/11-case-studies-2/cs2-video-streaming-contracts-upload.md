---
id: cs2-video-streaming-contracts-upload
title: Video contracts and resumable upload
level: intermediate
minutes: 4
summary: Keep control requests small while uploading video directly to durable storage.
sourceLesson: cs2-video-streaming
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

## API design

This is an illustrative endpoint contract, not a runnable HTTP request. Arrows distinguish responses from submitted fields.

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

Follow the arrows as data paths; the drawing is not a deployment specification.

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

## Key takeaways
- The play endpoint returns a manifest URL; the CDN transfers the video bytes.
- Choose a resumable protocol with explicit committed-offset or part accounting.
- Separate video metadata, source objects, search and progress by their access patterns.

## Further reading
- [HTTP Live Streaming (Apple developer docs)](https://developer.apple.com/documentation/http-live-streaming)
- [Netflix Open Connect overview](https://openconnect.netflix.com/en/)
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
- [GCS resumable uploads](https://cloud.google.com/storage/docs/performing-resumable-uploads)
- [S3 multipart upload](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html)
