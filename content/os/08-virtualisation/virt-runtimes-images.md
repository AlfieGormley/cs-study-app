---
id: virt-runtimes-images
title: Container runtimes and images
level: intermediate
minutes: 13
summary: What is actually inside an OCI image, how Docker, containerd and runc divide the work of running one, and how layer caching makes builds fast or painfully slow.
---

The last lesson built a container by hand from namespaces, cgroups and overlayfs. Production platforms automate those primitives. This lesson covers the three standards and the stack of programs that do it for you: what an **image** is, and how a **runtime** turns one into running processes.

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

- **Layers** are tar archives of file system *changes*: files added or modified, plus whiteout entries (files named `.wh.<name>`) for deletions. Applying the changesets produces a rootfs; an overlayfs snapshotter is one implementation. OCI whiteout files must be interpreted, not exposed as ordinary application files. Layers may be uncompressed, gzip or zstd according to supported media types.
- The **config** holds runtime defaults (`Env`, `Entrypoint`, `Cmd`, `WorkingDir`, `User`, exposed ports), the build history and the `diff_ids`, digests of each *uncompressed* layer.
- The **manifest** lists the config digest and each layer's digest, media type and size.
- An **image index** (a "manifest list") points to platform-specific manifests and other supported entries, so `python:3.12` resolves to the right one for your CPU.

Content addressing has big consequences:

- **Integrity.** Verification checks downloaded content against its descriptor digest. That detects mismatching content, but publisher authenticity requires a trusted reference or separate verification policy.
- **Deduplication.** Identical blobs can be reused by content stores and registries; actual deduplication across stores, repositories and unpacked snapshots depends on implementation. Pulling a new version of your app often downloads only its top layer.
- **Tags are mutable; digests are not.** `myapp:latest` can point at a different manifest tomorrow. `myapp@sha256:4f1c...` always means exactly the same bytes. Production deployments should pin digests.

## The runtime stack

"Docker" is really several cooperating programs. Kubernetes uses the lower part of the same stack.

```
docker CLI       kubelet
    |  REST         |  CRI (gRPC)
 dockerd            |
    |  gRPC         |
    +---> containerd <-+
            | images, snapshots
            |
     containerd-shim-runc-v2
            | (may group containers)
           runc
            | clone, pivot_root,
            | cgroups, exec
        your process
```

| Layer | Job |
|---|---|
| CLI / kubelet | User or orchestrator request |
| dockerd | Docker API, builds, networks, volumes |
| containerd | Pull, store, snapshots, lifecycle |
| shim | Supervises task(s), I/O and exit reporting |
| runc | OCI lifecycle CLI used by the shim |

### runc: the low-level runtime

**runc** is the OCI runtime spec's reference implementation. It takes a **bundle**, a directory containing `rootfs/` and `config.json`, and makes the system calls from the last lesson: clone with namespaces, set up cgroups, pivot_root, drop capabilities, install seccomp, exec.

In the shim-managed create/start workflow, **runc lifecycle commands return** and the shim supervises the running process. An attached runc run invocation can remain until the workload exits. Alternatives such as crun, gVisor runsc and Kata provide different implementations or isolation models; compatibility and runtime integration must be checked before switching.

### containerd and the shim

**containerd** is the long-running daemon that manages images and containers on a host. It pulls and verifies blobs, unpacks layers through a **snapshotter** (overlayfs by default) and prepares bundles.

A **shim** supervises tasks and separates their lifetime from the containerd daemon. The runc-v2 shim can group multiple containers, for example a Kubernetes pod, and manages I/O and exit reporting.

The shim design allows tasks to survive a containerd daemon restart if shims/tasks are preserved and reconnection remains compatible. Service-manager stop behavior and upgrade compatibility still matter. Docker daemon shutdown normally stops containers unless supported **live restore** is enabled; live restore also has documented limitations.

### dockerd and Kubernetes

**dockerd** adds the developer-facing layer: the `docker` API on `/var/run/docker.sock`, image builds, networks and volumes. It delegates running containers to containerd.

Kubernetes talks to runtimes through the **Container Runtime Interface (CRI)**. containerd has a built-in CRI plugin; **CRI-O** is an alternative built only for Kubernetes. Kubernetes used to talk to Docker through an adapter called dockershim, removed in version 1.24 (2022). Images built with Docker still run unchanged, because supported Docker/OCI image formats remain compatible.

## Building images

A Dockerfile is a recipe. `RUN`, `COPY` and `ADD` can produce filesystem changesets; empty results and build optimisations affect exported layers. Instructions like `ENV`, `CMD` and `EXPOSE` only change the config.

```
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

### How the cache decides

BuildKit (the default Docker builder for Linux images since Engine 23.0) reuses a step's previous result if its inputs are unchanged:

- For a simple RUN, the command, parent state and relevant build configuration matter; mounts and build arguments can add inputs. Cache lookup does not execute the command to discover changed remote content.
- For `COPY` and `ADD`, it is a **checksum of the copied files' contents** (and metadata), with modification time specifically excluded from the cache checksum.
- **Dependent steps may lose cache reuse** when their inputs change. This explains a simple sequential stage; BuildKit can cache independent stages or linked COPY operations separately.

The Dockerfile above is ordered deliberately. Assuming the base image, builder configuration and other inputs stay fixed, editing `app.py` changes the final `COPY . .`, so the slow `pip install` stays cached. Swap the order (copy everything first, then install) and every one-line code change reinstalls all dependencies.

> [!warning] Classic caching bugs
> - `RUN apt-get update` on its own line can be reused from cache despite changed repositories, so a later `RUN apt-get install` uses stale package lists. Combine them in one `RUN`.
> - `RUN git clone ...` or `RUN curl .../latest.tar.gz` is cached by its command text, so you keep building the old version.
> - `COPY . .` without a `.dockerignore` pulls in `.git`, `node_modules` and local secrets, and any change to them busts the cache.

### Making images small

Published immutable layer content remains part of images that reference it; unreferenced blobs can be garbage-collected. Deleting a file in a later layer only adds a whiteout; the bytes still ship.

The following illustrates uncompressed file bytes and ignores metadata/compression:

```
RUN curl -o big.tgz $URL # +300 MB
RUN tar xf big.tgz       # +600 MB
RUN rm big.tgz           # +0, still 900
```

Do download, extract and clean-up in one `RUN`, or better, use a **multi-stage build**: compile in a full toolchain image, then copy only the output into a minimal runtime image.

```
FROM golang:1 AS build
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /app

FROM gcr.io/distroless/static
COPY --from=build /app /app
ENTRYPOINT ["/app"]
```

For a compatible Go project, this copies only the built binary into the final base. CGO_ENABLED=0 does not make every project buildable or eliminate runtime data dependencies. Distroless provides selected runtime files but not a general shell/package-manager environment. Image size and vulnerability exposure must be measured; no fixed size reduction is asserted.

BuildKit adds more tools: independent stages build **in parallel**, `RUN --mount=type=cache` keeps a package manager's download cache between builds without putting it in a layer, and `--mount=type=secret` temporarily exposes credentials without automatically persisting the mount. A build command can still copy secrets into layers or print them to logs, so handling matters.

## Pitfalls

- **Secrets in layers.** `COPY .env` followed by `RUN rm .env` still ships `.env` in the earlier layer; anyone who pulls the image can extract it.
- **`latest` in production.** Two nodes pulling `latest` an hour apart can run different code. Pin digests.
- **Architecture mismatch.** An amd64-only image on an arm64 node (Graviton, Apple silicon) cannot execute its foreign instructions natively; configured emulation may work with workload-dependent overhead. Publish multi-arch indexes.
- **Exposing the Docker socket.** Access to an unrestricted rootful daemon API can grant host-root-equivalent power, including privileged containers and host mounts. Rootless daemons and authorization policies change that scope; a socket mount still exposes the daemon's authority.

## Key takeaways

- OCI defines image, distribution and runtime specs, so tools interoperate.
- An image is a manifest pointing to a config and content-addressed layer tarballs; layers are shared and verified by digest.
- Docker CLI → dockerd → containerd → shim → runc; Kubernetes enters at containerd (or CRI-O) through CRI. in the usual shim create/start workflow the shim stays to supervise tasks.
- Cache reuse depends on declared inputs and dependency structure. Keep stable dependency installation before frequently changing source in a sequential Dockerfile stage.
- Later layers cannot shrink earlier ones; use single `RUN` clean-ups and multi-stage builds.

> [!note] Measurement gaps
> No reproducible image-size, startup-time or rebuild-speed benchmark accompanies these examples, so fixed performance claims are omitted. These illustrative Dockerfiles were source-reviewed, not built here: the required Python/Go application projects were not supplied. They assume compatible source projects and available base images; pin and maintain reviewed versions for an actual deployment.

## Further reading

- [OCI Image Format Specification — GitHub](https://github.com/opencontainers/image-spec/blob/main/spec.md)
- [OCI Runtime Specification — GitHub](https://github.com/opencontainers/runtime-spec/blob/main/spec.md)
- [Docker build cache — Docker docs](https://docs.docker.com/build/cache/)
- [Building best practices — Docker docs](https://docs.docker.com/build/building/best-practices/)
- [Container Runtime Interface — Kubernetes docs](https://kubernetes.io/docs/concepts/architecture/cri/)
