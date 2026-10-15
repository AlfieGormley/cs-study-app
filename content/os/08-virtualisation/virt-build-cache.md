---
id: virt-build-cache
title: Dockerfile order and build cache inputs
level: intermediate
minutes: 3
sourceLesson: virt-runtimes-images
summary: Cache reuse follows inputs and dependency structure, not live checks of remote repositories.
---

This unit focuses on dockerfile order and build cache inputs. It builds on the earlier virtualisation units in this module.

## Building images

A Dockerfile is a recipe. `RUN`, `COPY` and `ADD` can produce filesystem changesets; empty results and build optimisations affect exported layers. Instructions like `ENV`, `CMD` and `EXPOSE` only change the config.

```dockerfile
FROM python:3.12-slim
# Install dependencies before changing code.
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

## Key takeaways

- Cache reuse follows inputs and dependency structure, not live checks of remote repositories.
- Keep stable dependency installation ahead of frequently changed application files.

## Further reading

- [OCI Image Format Specification — GitHub](https://github.com/opencontainers/image-spec/blob/main/spec.md)
- [OCI Runtime Specification — GitHub](https://github.com/opencontainers/runtime-spec/blob/main/spec.md)
- [Docker build cache — Docker docs](https://docs.docker.com/build/cache/)
- [Building best practices — Docker docs](https://docs.docker.com/build/building/best-practices/)
- [Container Runtime Interface — Kubernetes docs](https://kubernetes.io/docs/concepts/architecture/cri/)
