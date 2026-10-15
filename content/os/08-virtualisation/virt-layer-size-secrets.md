---
id: virt-layer-size-secrets
title: Image size, multi-stage builds and secrets
level: intermediate
minutes: 4
sourceLesson: virt-runtimes-images
summary: Deleting a file in a later layer does not remove it from earlier layers.
---

This unit focuses on image size, multi-stage builds and secrets. It builds on the earlier virtualisation units in this module.

### Making images small

Published immutable layer content remains part of images that reference it; unreferenced blobs can be garbage-collected. Deleting a file in a later layer only adds a whiteout; the bytes still ship.

The following illustrates uncompressed file bytes and ignores metadata/compression:

```dockerfile
# Separate steps retain earlier file bytes.
RUN curl -o big.tgz $URL # +300 MB
RUN tar xf big.tgz       # +600 MB
RUN rm big.tgz           # +0, still 900
```

Each `RUN` step becomes its own layer, and an image ships every layer, so the image's file data is the sum of the layers:

```formula
S = S_1 + S_2 + S_3
S = 300 MB + 600 MB + 0 MB
S = 900 MB
where
S: the total uncompressed file data shipped across the image's layers, in megabytes (MB)
S_1: the layer from the download step: the 300 MB archive
S_2: the layer from the extract step: 600 MB of extracted files
S_3: the layer from the rm step: only a whiteout, 0 MB
MB: megabyte, 1,000,000 bytes in this decimal-unit illustration
In words: layers only ever add; deleting the archive in a later layer adds a whiteout of size zero and cannot subtract the 300 MB already captured.
```

Do download, extract and clean-up in one `RUN`, or better, use a **multi-stage build**: compile in a full toolchain image, then copy only the output into a minimal runtime image.

```dockerfile
FROM golang:1 AS build
# Build tools stay in this earlier stage.
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /app

FROM gcr.io/distroless/static
# Copy the binary, not the compiler/source.
COPY --from=build /app /app
ENTRYPOINT ["/app"]
```

For a compatible Go project, this copies only the built binary into the final base. `CGO_ENABLED=0` does not make every project buildable or eliminate runtime data dependencies. Distroless provides selected runtime files but not a general shell/package-manager environment. Image size and vulnerability exposure must be measured; no fixed size reduction is asserted.

BuildKit adds more tools: independent stages build **in parallel**, `RUN --mount=type=cache` keeps a package manager's download cache between builds without putting it in a layer, and `--mount=type=secret` temporarily exposes credentials without automatically persisting the mount. A build command can still copy secrets into layers or print them to logs, so handling matters.

## Pitfalls

- **Secrets in layers.** `COPY .env` followed by `RUN rm .env` still ships `.env` in the earlier layer; anyone who pulls the image can extract it.
- **`latest` in production.** Two nodes pulling `latest` an hour apart can run different code. Pin digests.
- **Architecture mismatch.** An amd64-only image on an arm64 node (Graviton, Apple silicon) cannot execute its foreign instructions natively; configured emulation may work with workload-dependent overhead. Publish multi-arch indexes.
- **Exposing the Docker socket.** Access to an unrestricted rootful daemon API can grant host-root-equivalent power, including privileged containers and host mounts. Rootless daemons and authorization policies change that scope; a socket mount still exposes the daemon's authority.

> [!note] Measurement gaps
> No reproducible image-size, startup-time or rebuild-speed benchmark accompanies these examples, so fixed performance claims are omitted. These Dockerfiles use compatible teaching-project fixtures for build checks, rather than a supplied production application. They assume compatible source projects and available base images; pin and maintain reviewed versions for an actual deployment.

## Key takeaways

- Deleting a file in a later layer does not remove it from earlier layers.
- Use suitable build mounts and keep credentials out of exported layers, logs and caches.

## Further reading

- [OCI Image Format Specification — GitHub](https://github.com/opencontainers/image-spec/blob/main/spec.md)
- [OCI Runtime Specification — GitHub](https://github.com/opencontainers/runtime-spec/blob/main/spec.md)
- [Docker build cache — Docker docs](https://docs.docker.com/build/cache/)
- [Building best practices — Docker docs](https://docs.docker.com/build/building/best-practices/)
- [Container Runtime Interface — Kubernetes docs](https://kubernetes.io/docs/concepts/architecture/cri/)
