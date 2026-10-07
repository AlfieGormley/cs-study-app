---
id: arch-object-storage-media
title: Blob storage, uploads and media pipelines
level: intermediate
minutes: 14
summary: How S3-style object storage works and why it differs from file systems and databases, how presigned URLs and multipart uploads keep big files off your servers, and how video transcoding pipelines are built.
---

Photos, videos, PDFs, backups and logs are **blobs**: large, opaque chunks of bytes. Large media collections can increase database backup, replication and serving costs; database BLOBs can still suit smaller or transactionally coupled workloads. Depending on app-local files makes instance replacement harder. A common media architecture uses **object storage**: Amazon S3, Google Cloud Storage, Azure Blob Storage, or self-hosted options like MinIO and Ceph.

## The object storage model

This lesson uses S3 general purpose buckets as its main example: a flat key–value model for objects. Other products and bucket types differ; S3 Express One Zone directory buckets, for example, support appending to objects.

- A **bucket** is a namespace (`acme-user-uploads`).
- An **object** is bytes plus metadata, addressed by a **key** (`avatars/42/2026-09-01.jpg`). The slashes are just characters; there are no real directories.
- Operations are whole-object: `PUT`, `GET` (with optional byte ranges), `DELETE`, `LIST` by prefix. You can't modify byte 500 in place; you overwrite the object.

What you get:

- **Durability**: S3 Standard is designed for 99.999999999% (eleven nines) durability by storing data redundantly across multiple Availability Zones.
- **Large objects**: a single PUT supports up to 5 GB; larger objects require multipart upload. The current multipart limits page lists a maximum of 48.8 TiB, with up to 10,000 parts. Check current service limits when implementing a client.
- **Throughput by parallelism**: S3 supports at least 3,500 `PUT`/`COPY`/`POST`/`DELETE` and 5,500 `GET`/`HEAD` requests per second *per key prefix*. Parallel requests and prefixes can increase throughput, but scaling is gradual and can produce temporary 503 Slow Down responses; workload and other dependencies still limit performance.
- **Cheap tiers**: infrequent-access and archive classes (Glacier) cost a fraction of standard storage, with lifecycle rules moving objects automatically.

General purpose buckets do not provide arbitrary in-place byte updates, application editing mutexes, or multi-key transactional updates. S3 Object Lock provides retention protection, not a read-modify-write mutex. Use a separate query layer for rich metadata queries.

> [!note] Evidence gap
> Fixed object-store/CDN latency and transcoding speedup figures are omitted because no representative deployment benchmark supports them. Calculations below are hypothetical.

On consistency, S3 is better than its old reputation. Since December 2020 it provides **strong read-after-write consistency** for object `PUT`s (new and overwrite) and `DELETE`s, and for the `GET`, `HEAD` and `LIST` requests that follow them. If your `PUT` returned success, a subsequent authorized direct read of the same bucket sees that write or a later modification. This does not make CDN caches or cross-Region replication synchronous. Two caveats:

- **Concurrent writers to one key**: the last write wins. S3 has no application editing mutex, but it does support conditional writes (`If-None-Match` to create only if absent, `If-Match` on an ETag), which you can use for optimistic concurrency.
- **Bucket configuration** (policies, versioning, lifecycle) is still eventually consistent; AWS advises waiting about 15 minutes after first enabling versioning before writing.

> [!tip] Store metadata in a database, bytes in object storage
> Keep a row like `(photo_id, owner_id, s3_key, size, status, created_at)` in your database and the image itself in S3. The database answers "which photos does user 42 have?"; S3 serves the bytes.

## Keep large uploads off your servers: presigned URLs

The naive design streams uploads through the app tier:

```
 client --100MB--> [app] --100MB--> [S3]
```

This uses app-server bandwidth and adds an app-to-store transfer leg. Streaming can use bounded buffers rather than hold the whole object in RAM, but proxy limits and timeouts still matter.

Instead, the app hands the client a **presigned URL**: a URL that embeds a signature granting permission for one specific operation, on one specific key, for a limited time. Azure calls this the **Valet Key** pattern.

```
1. client -> app: "I want to upload"
2. app: auth check, create DB row
   (status=pending), sign URL for
   PUT uploads/abc123, expires 15m
3. client --bytes--> S3 (direct)
4. S3 -> event -> app: mark uploaded
```

- The app never touches the bytes; S3 does the heavy lifting.
- The URL is scoped: one key, one method, short expiry. You can also constrain content type and maximum size (with presigned POST policies).
- Downloads work the same way: a presigned `GET` lets a user fetch a private file for 5 minutes.
- A presigned URL is a **bearer token**: anyone holding it can use it, as many times as they like, until it expires. There is no individual URL-token revocation API. Revoking credentials or changing applicable access policies can deny later requests; short expiry and narrow scope reduce exposure.

How long can one last? With SigV4 and long-term IAM user keys, up to **7 days**. With temporary credentials (an IAM role, an EC2 instance profile, an STS session), the URL dies when those credentials expire, often within an hour or a few hours, *even if you asked for longer*. This catches people out: a server running on a role signs a "24-hour" link that stops working after an hour. S3 checks expiry when the request starts, so a download already in progress isn't cut off.

> [!warning] Don't trust the client's word that it uploaded
> Confirm the upload with S3, then validate the exact object version (file type, size and required scans). Notifications can be duplicated or out of order. A reusable presigned PUT can overwrite a key after a scan, so publish the validated version or protected processed output under an immutable key, not whichever bytes later occupy the upload key.

## Big files: multipart and resumable uploads

Uploading a 4 GB video in one request is fragile: if the connection drops at 3.9 GB, you start again.

**Multipart upload** (S3's approach):

1. `CreateMultipartUpload` returns an upload ID.
2. The client uploads parts (5 MiB to 5 GiB each, except the last part, which can be smaller; up to 10,000 parts) **in parallel**, each with its own presigned URL.
3. Failed parts are retried individually.
4. `CompleteMultipartUpload` stitches the parts into one object.

```
 4 GB file, 100 MB parts = 40 parts
 [p1][p2][p3] ... [p40]
   \   |   /        |
   parallel PUTs, retry failures
          |
   Complete -> one object
```

Benefits: parallelism (faster uploads on fat pipes), resilience (lose only one part on failure) and the ability to pause and resume. AWS suggests considering multipart for anything over about 100 MB.

The 10,000-part cap means **part size sets the maximum file size**. With 100 MB parts you top out at about 1 TB; to reach the 48.8 TiB maximum you need parts near the 5 GiB ceiling (10,000 × 5 GiB). Pick a part size from the largest file you expect.

Set a lifecycle rule to abort incomplete multipart uploads after a few days, or orphaned parts will quietly cost money.

For flaky mobile networks, **resumable upload protocols** let the client ask "how many bytes did you get?" and continue from there. Examples are the open **tus** protocol and Google Cloud Storage's resumable uploads.

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
- **Parallelise by chunk**: split work at suitable codec boundaries, encode chunks concurrently, then assemble and package them. Handle keyframes/GOPs, timestamps, audio alignment and rendition boundaries; speedup depends on available workers and split/encode/assembly costs.
- **Idempotent, retryable steps**: workers can die (often on cheap spot instances). Include source version and encoding settings in output identity. Deterministic names alone do not guarantee idempotency: write temporary outputs, validate them, and conditionally publish a manifest so a stale retry cannot replace newer work.
- **A workflow engine** (Step Functions, Temporal, or a simple state table) tracks each video's progress through stages: validate → transcode → thumbnail → moderate → publish.
- **Prioritise**: publish a low-resolution rendition first so the video is watchable sooner, and fill in higher qualities afterwards.

> [!example] Image pipeline
> Instagram-style photos follow the same shape on a smaller scale: upload original via presigned URL → event → workers generate 150px, 640px and 1080px versions in WebP/AVIF → write to output bucket → CDN. Some systems resize lazily at the edge instead, generating a size the first time it's requested and caching it.

## Key takeaways
- S3 general purpose buckets use a flat object-key model; distinguish their guarantees from other products and bucket types. A database can maintain searchable metadata.
- S3 has been strongly read-after-write consistent for object operations since December 2020, but concurrent writers to one key still race (last writer wins) unless you use conditional writes.
- Presigned URLs (the valet key pattern) let clients upload and download directly, keeping bytes off your app servers while keeping access scoped and short-lived. They're bearer tokens, capped at 7 days and cut short by temporary signing credentials.
- Multipart and resumable uploads make large uploads parallel and recoverable. With a 10,000-part cap, part size limits file size; clean up incomplete uploads.
- Serve media through a CDN with immutable, versioned keys.
- Transcoding is an asynchronous, event-driven, chunk-parallel pipeline of idempotent steps producing an adaptive bitrate ladder.

## Further reading
- [AWS: What is Amazon S3?](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)
- [AWS: Sharing objects with presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ShareObjectPreSignedURL.html)
- [AWS: Uploading objects using multipart upload](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html)
- [AWS: Best practices for S3 performance](https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html)
- [Azure Architecture Center: Valet Key pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/valet-key)
- [tus: Resumable upload protocol](https://tus.io/protocols/resumable-upload)
- [Wikipedia: HTTP Live Streaming](https://en.wikipedia.org/wiki/HTTP_Live_Streaming)
