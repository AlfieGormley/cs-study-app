---
id: arch-presigned-upload-version-safety
title: Authorising direct uploads safely
level: intermediate
minutes: 3
summary: Keep bytes off application servers with scoped presigned URLs and publish only validated object versions.
sourceLesson: arch-object-storage-media
---

Object storage can serve bytes independently of the app. The application still decides who may upload or download and which validated version becomes public.

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
- A presigned URL is a **bearer token**: anyone holding it can use it, as many times as they like, until it expires. There is no individual URL-token revocation API. Invalidating signing credentials or changing applicable access policies can deny later requests; short expiry and narrow scope reduce exposure.

How long can one last? With SigV4 and long-term IAM user keys, up to **7 days**. With temporary credentials (an IAM role, an EC2 instance profile, an STS session), the URL dies when those credentials expire, often within an hour or a few hours, *even if you asked for longer*. This catches people out: a server running on a role signs a "24-hour" link that stops working after an hour. S3 checks expiry when the request starts, so a download already in progress isn't cut off.

> [!warning] Don't trust the client's word that it uploaded
> Confirm the upload with S3, then validate the exact object version (file type, size and required scans). Notifications can be duplicated or out of order. A reusable presigned PUT can overwrite a key after a scan, so publish the validated version or protected processed output under an immutable key, not whichever bytes later occupy the upload key.

## Key takeaways
- A presigned URL authorises a particular operation and key without routing file bytes through the app.
- It is reusable bearer authority until expiry or denial by credentials and policy.
- Temporary credential expiry can end a URL before its requested lifetime; request-start checks allow an active download to continue.
- Confirm and validate the exact uploaded version, then publish immutable protected output so a later overwrite cannot bypass scans.

## Further reading
- [AWS: Sharing objects with presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ShareObjectPreSignedURL.html)
- [Azure Architecture Center: Valet Key pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/valet-key)
- [AWS: Download and upload objects with presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)
