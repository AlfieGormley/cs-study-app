---
id: virt-oci-content
title: OCI image graphs, layers and immutable digests
level: intermediate
minutes: 3
sourceLesson: virt-runtimes-images
summary: Descriptors identify exact content, while tags may move to different content.
---

The last lesson built a container by hand from namespaces, cgroups and overlayfs. Production platforms automate those primitives. This lesson covers the three standards and the stack of programs that do it for you: what a **container image** is, and how a **runtime** turns one into running processes.

## The OCI standards

Docker defined the de facto formats in 2013. The **Open Container Initiative (OCI)** was established in 2015; its specifications support interoperability across tools. Three specs matter:

- **Image spec**: how an image is laid out (manifest, config, layers).
- **Distribution spec**: the HTTP API registries speak (Docker Hub, ECR, GHCR, Artifact Registry).
- **Runtime spec**: how to run a container from an unpacked file system plus a `config.json`.

Compatible Docker/OCI images can be used by runtimes underlying these platforms. OS/architecture, media types and required runtime features must still match.

## Anatomy of an image

An OCI image is a graph of **content-addressed blobs**, which can also be packaged in an archive. Descriptors identify bytes using a digest algorithm and value; SHA-256 is widely used, but the format is not limited to it.

```
image index (optional, multi-arch)
 |- linux/amd64 -> manifest
 |- linux/arm64 -> manifest
                    |- config (JSON)
                    |- layer 1 (tar.gz)
                    |- layer 2 (tar.gz)
                    |- layer 3 (tar.gz)
```

- **Image layers** are tar archives of file system *changes*: files added or modified, plus whiteout entries (files named `.wh.<name>`) for deletions. Applying the changesets produces a rootfs; an overlayfs snapshotter is one implementation. OCI whiteout files must be interpreted, not exposed as ordinary application files. Layers may be uncompressed, gzip or Zstandard (zstd) according to supported media types.
- The **image config** holds runtime defaults (`Env`, `Entrypoint`, `Cmd`, `WorkingDir`, `User`, exposed ports), the build history and the `diff_ids`, digests of each *uncompressed* layer.
- The **manifest** lists the config digest and each layer's digest, media type and size.
- An **image index** (a "manifest list") points to platform-specific manifests and other supported entries, so `python:3.12` resolves to the right one for your CPU.

Content addressing has big consequences:

- **Integrity.** Verification checks downloaded content against its descriptor digest. That detects mismatching content, but publisher authenticity requires a trusted reference or separate verification policy.
- **Deduplication.** Identical blobs can be reused by content stores and registries; actual deduplication across stores, repositories and unpacked snapshots depends on implementation. Pulling a new version of your app often downloads only its top layer.
- **Tags are mutable; digests are not.** `myapp:latest` can point at a different manifest tomorrow. `myapp@sha256:4f1c...` always means exactly the same bytes. Production deployments should pin digests.

## Key takeaways

- Descriptors identify exact content, while tags may move to different content.
- Digest integrity does not establish publisher authenticity or future availability.

## Further reading

- [OCI Image Format Specification — GitHub](https://github.com/opencontainers/image-spec/blob/main/spec.md)
- [OCI Runtime Specification — GitHub](https://github.com/opencontainers/runtime-spec/blob/main/spec.md)
- [Docker build cache — Docker docs](https://docs.docker.com/build/cache/)
- [Building best practices — Docker docs](https://docs.docker.com/build/building/best-practices/)
- [Container Runtime Interface — Kubernetes docs](https://kubernetes.io/docs/concepts/architecture/cri/)
