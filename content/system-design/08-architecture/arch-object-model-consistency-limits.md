---
id: arch-object-model-consistency-limits
title: Understanding object-storage guarantees
level: intermediate
minutes: 4
summary: Separate flat object keys, direct-read consistency and concurrent-write controls from database and CDN guarantees.
sourceLesson: arch-object-storage-media
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

## Key takeaways
- General purpose S3 buckets store whole objects by flat keys; database metadata can provide richer queries.
- Direct authorised reads after a successful object write observe that write or a later modification.
- Concurrent read-modify-write clients need conditional writes to detect changes; strong reads alone do not prevent lost updates.
- Service limits, prefix scaling and other bucket types require current documentation rather than universal assumptions.

## Further reading
- [AWS: What is Amazon S3?](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)
- [AWS: Best practices for S3 performance](https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html)
- [AWS: Multipart upload limits](https://docs.aws.amazon.com/AmazonS3/latest/userguide/qfacts.html)
- [AWS: Conditional writes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html)
