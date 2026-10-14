---
id: arch-multipart-part-size-recovery
title: Choosing multipart sizes and recovery
level: intermediate
minutes: 4
summary: Calculate part counts and size ceilings while retrying only incomplete work.
sourceLesson: arch-object-storage-media
---

A direct single-request upload still has a large failure boundary. Multipart and resumable designs keep already transferred work when a connection fails.

## Big files: multipart and resumable uploads

Uploading a 4 GB video in one request is fragile: if the connection drops at 3.9 GB, you start again.

**Multipart upload** (S3's approach):

1. `CreateMultipartUpload` returns an upload ID.
2. The client uploads parts (5 MiB to 5 GiB each, except the last part, which can be smaller; up to 10,000 parts) **in parallel**, each with its own presigned URL.
3. Failed parts are retried individually.
4. `CompleteMultipartUpload` stitches the parts into one object.

The number of parts is the file size divided by the part size, rounded up (the last part holds whatever is left over):

```formula
P = ⌈F / S⌉
P = ⌈4 GB / 100 MB⌉
P = ⌈4000 MB / 100 MB⌉ = 40
where
P: the number of parts to upload
F: the file size, here 4 gigabytes (GB)
S: the part size, here 100 megabytes (MB)
GB: gigabyte; 1 GB = 1,000 MB
MB: megabyte, a million bytes
⌈ ⌉: ceiling: round up to the next whole number
In words: a 4 GB file in 100 MB parts is 40 parts, which can be uploaded side by side.
```

```
 40 parts of 100 MB each
 [p1][p2][p3] ... [p40]
   \   |   /        |
   parallel PUTs, retry failures
          |
   Complete -> one object
```

Benefits: parallelism (faster uploads on fat pipes), resilience (lose only one part on failure) and the ability to pause and resume. AWS suggests considering multipart for anything over about 100 MB.

The 10,000-part cap means **part size sets the maximum file size**:

```formula
F_max = N_max × S
F_max = 10000 × 100 MB = 1000000 MB
F_max = 1 TB
where
F_max: the largest file you can upload with that part size
N_max: S3's maximum number of parts in one upload, 10,000
S: the part size you chose, here 100 megabytes (MB)
MB: megabyte, a million bytes
TB: terabyte, a million MB (10^12 bytes)
^: "to the power of": 10^12 is a 1 followed by 12 zeros
In words: with 100 MB parts you top out at about 1 TB.
```

To reach the 48.8 TiB maximum object size you need parts near the 5 GiB ceiling:

```formula
F_max = 10000 × 5 GiB = 50000 GiB
F_max = (50000 / 1024) TiB ≈ 48.8 TiB
where
F_max: the largest file with maximum-size parts
GiB: gibibyte, 1,024 × 1,024 × 1,024 bytes (about 1.07 GB)
TiB: tebibyte, 1,024 GiB
≈: approximately equal to (rounded)
In words: 10,000 parts of 5 GiB each is 50,000 GiB, about 48.8 TiB.
```

Pick a part size from the largest file you expect.

Set a lifecycle rule to abort incomplete multipart uploads after a few days, or orphaned parts will quietly cost money.

For flaky mobile networks, **resumable upload protocols** let the client ask "how many bytes did you get?" and continue from there. Examples are the open **tus** protocol and Google Cloud Storage's resumable uploads.

## Key takeaways
- Multipart upload retries individual failed parts and combines completed parts into one object.
- Round file size divided by part size up, and keep the result within the current part-count limit.
- Choose part size from maximum expected file size, distinguishing decimal and binary units.
- Abort abandoned uploads with lifecycle rules; resumable protocols also support weak connections.

## Further reading
- [AWS: Uploading objects using multipart upload](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html)
- [tus: Resumable upload protocol](https://tus.io/protocols/resumable-upload)
- [AWS: Multipart upload limits](https://docs.aws.amazon.com/AmazonS3/latest/userguide/qfacts.html)
