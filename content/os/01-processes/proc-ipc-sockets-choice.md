---
id: proc-ipc-sockets-choice
sourceLesson: proc-ipc
title: "Unix sockets and choosing an IPC channel"
level: advanced
minutes: 4
summary: "Unix sockets can pass file descriptors and expose authenticated peer credentials."
---

Unix sockets can pass file descriptors and expose authenticated peer credentials. This lesson focuses on unix sockets and choosing an ipc channel.

## Sockets: bidirectional and general

**Unix domain sockets** (`AF_UNIX`) use the socket API but stay on one machine. They're addressed by a path such as `/var/run/docker.sock` or by an abstract name. Compared with pipes they are:

- **Bidirectional**: one connection carries requests and replies.
- **Client–server**: many clients can `connect` to one listening server, which `accept`s each.
- **Message-capable**: `SOCK_STREAM` is a byte stream, while `SOCK_DGRAM` and `SOCK_SEQPACKET` keep message boundaries (and on Unix sockets, datagrams are reliable).
- **Able to pass file descriptors**. With `sendmsg` and an `SCM_RIGHTS` control message, a process can hand an open fd to another. The receiver gets a new fd number referring to the same open file. Wayland clients pass buffer fds to the compositor this way, and privilege-separated servers use it so a privileged process opens files or sockets and gives them to a sandboxed worker.
- **Able to identify the peer**: On supported connected/socket-pair cases, `SO_PEERCRED` reports kernel-supplied PID, UID and GID recorded at connection, listen or socket-pair creation time. These are a snapshot, not a live query of later credential changes. PostgreSQL's `peer` authentication and the D-Bus daemon rely on this.

Because they skip the TCP/IP stack (no checksums, no congestion control, no loopback routing), Unix sockets avoid those TCP/IP protocol layers, but their performance relative to loopback TCP requires a workload-specific measurement. That's why PostgreSQL and MySQL clients use a Unix socket by default for local connections, and Redis can listen on one too.

**TCP sockets** provide the network-capable choice in this comparison; UDP and other network transports also exist. Writing to a socket interface means a service can later be split onto another host with little code change, which is a strong reason to default to sockets. D-Bus on Linux desktops and Android's Binder are higher-level IPC systems: D-Bus runs over Unix sockets, while Binder is its own kernel driver.

## Choosing a mechanism

| Need | Use |
|---|---|
| Stream between parent and child | pipe |
| Unrelated processes, simple stream | FIFO |
| "Stop", "reload", "child died" | signal |
| Bulk data without channel copies | shared memory + synchronisation |
| Discrete prioritised messages | POSIX message queue |
| Request/reply, fd passing, auth | Unix socket |
| Across machines | TCP socket |

A useful mental model is cost per message. Conventional read/write channel use often copies bytes into and out of kernel buffers. Batching and zero-copy APIs change the per-message costs, and a wake-up does not imply a fixed switch count. Shared memory avoids those payload copies but still pays synchronisation, coherence and notification costs. Large systems often combine them: a Unix socket for control messages and fd passing, and shared memory for the bulk data.

## Pitfalls

- **Forgetting to close unused pipe ends.** The reader never sees EOF because some process (often itself) still holds a write end. Close every end you don't use, straight after `fork`.
- **Assuming message boundaries on a stream.** One `write` doesn't equal one `read`. Frame your messages.
- **Unsafe signal handlers.** `printf`, `malloc` or taking a lock in a handler can deadlock. Set a flag or use `signalfd`.
- **Counting standard signals.** Signal coalescing can combine notifications. Reap children in a loop.
- **Dying on `SIGPIPE`.** A server writing to a client that disconnected is killed silently. Network servers usually ignore `SIGPIPE` and handle `EPIPE`, or pass `MSG_NOSIGNAL` to `send`.
- **Leaking named objects.** FIFOs, `/dev/shm` objects, message queues and socket paths persist after a crash. Unlink them on startup or shutdown.

> [!note] Content gap: IPC performance
> No reproducible IPC benchmark is supplied. Universal fastest-channel rankings and fixed copy/syscall counts are omitted. Code fragments illustrate mechanisms and need headers, error handling, ownership and synchronisation before production use.

## Key takeaways
- Unix sockets can pass file descriptors and expose authenticated peer credentials.
- Choose channels by boundaries, ownership, topology and measured workload costs.

## Further reading
- [pipe(7) — Linux manual page](https://man7.org/linux/man-pages/man7/pipe.7.html)
- [signal(7) — Linux manual page](https://man7.org/linux/man-pages/man7/signal.7.html)
- [signal-safety(7) — Linux manual page](https://man7.org/linux/man-pages/man7/signal-safety.7.html)
- [shm_overview(7) — Linux manual page](https://man7.org/linux/man-pages/man7/shm_overview.7.html)
- [mq_overview(7) — Linux manual page](https://man7.org/linux/man-pages/man7/mq_overview.7.html)
- [unix(7) — Linux manual page](https://man7.org/linux/man-pages/man7/unix.7.html)
- [Inter-process communication — Wikipedia](https://en.wikipedia.org/wiki/Inter-process_communication)
