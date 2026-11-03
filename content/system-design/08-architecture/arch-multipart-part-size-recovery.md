---
id: arch-multipart-part-size-recovery
title: Choosing multipart sizes and recovery
level: intermediate
minutes: 3
summary: Choose part sizes against service limits, request overhead and the cost of retrying failed transfers.
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

```formula reference
P = ⌈F / S⌉
where
P: number of parts, a whole-number count
F: file size in bytes
S: chosen part size in bytes; all but the last part have this size
⌈ ⌉: ceiling, rounding up to the next whole number
In words: larger parts reduce the number of upload requests, but a failed part then contains more bytes to resend. Round up because the final part may be smaller.
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

The 10,000-part cap means a fixed part size also limits the largest upload it can represent. Larger files need larger parts, while smaller parts reduce the bytes resent after one failed transfer.

The current maximum object size is 48.8 TiB, requiring parts near the 5 GiB ceiling. Keep decimal file sizes and binary service limits in consistent units when planning.

Pick a part size from the largest file you support, then bound parallel requests to the client’s memory and network capacity.

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
