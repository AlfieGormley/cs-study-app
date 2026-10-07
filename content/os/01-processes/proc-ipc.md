---
id: proc-ipc
title: Inter-process communication
level: advanced
minutes: 14
summary: How isolated processes talk to each other on Linux, using pipes, signals, shared memory, message queues and sockets, and how to choose between them.
---

Processes are isolated on purpose. Each has its own address space, so one can't read or scribble on another's memory. This can contain a tab-process fault, though shared resources, browser dependencies and privileged bugs can still affect other components.

But useful systems are made of processes that cooperate: a shell pipeline, a web server and its workers, a database and its client. **Inter-process communication (IPC)** is the set of kernel-provided channels that let isolated processes exchange data and events without giving up that isolation.

Think of processes as people in separate sealed offices. They can pass notes through a slot in the wall (pipes), ring a bell (signals), agree to share a whiteboard in a room between them (shared memory), use the internal post room (message queues), or pick up the phone (sockets). Each has a different cost, capacity and etiquette.

## Pipes: a one-way byte stream

A **pipe** is a kernel buffer with two file descriptors: one end to write, one end to read. `pipe(fd)` fills `fd[0]` with the read end and `fd[1]` with the write end (think "0 is stdin, 1 is stdout").

Pipes become useful with `fork`, because the child inherits both descriptors:

```c
int fd[2];
pipe(fd);
pid_t pid = fork();
if (pid == 0) {          /* child */
    close(fd[1]);
    char buf[64];
    ssize_t n;
    while ((n = read(fd[0], buf,
                     sizeof buf)) > 0)
        write(1, buf, n);
    _exit(0);
}
close(fd[0]);            /* parent */
const char *m = "hello\n";
write(fd[1], m, strlen(m));
close(fd[1]);   /* child now sees EOF */
waitpid(pid, NULL, 0);
```

The child prints `hello`. The rules that make this work:

- `read` on an empty pipe **blocks** until data arrives.
- `read` returns **0 (EOF)** only once *every* write end, in every process, is closed. That's why the child closes its inherited copy of `fd[1]`. If it didn't, it would wait forever for data from itself.
- `write` to a full pipe blocks until the reader drains it. Linux commonly defaults to 16 pages (64 KiB with 4 KiB pages), but resource limits and configuration can reduce it. Query `F_GETPIPE_SZ`; `F_SETPIPE_SZ` requests a resize subject to limits.
- `write` to a pipe with **no readers left** raises `SIGPIPE`, which kills the writer by default. If that signal is ignored, `write` fails with `EPIPE` instead.

### How the shell builds `ls | wc -l`

```
shell: pipe(fd)
  fork -> child 1:
          dup2(fd[1], 1)  stdout->pipe
          close both fds
          exec("ls")
  fork -> child 2:
          dup2(fd[0], 0)  stdin<-pipe
          close both fds
          exec("wc", "-l")
  close both fds; wait for both
```

Neither program knows a pipe is involved; they just use fds 0 and 1. When `ls` exits, the last write end closes, `wc` sees EOF and prints its count. This is the `fork`/`exec` gap from the previous lessons doing its job.

### Byte streams have no message boundaries

A pipe carries bytes, not messages. Two `write` calls of 10 bytes each may come out as one 20-byte `read`, or as 7 then 13. If you need messages, add framing: a length prefix, or a delimiter such as a newline.

### Atomic writes and `PIPE_BUF`

When several processes write to the same pipe, a write of at most **`PIPE_BUF`** bytes (4,096 on Linux; POSIX requires at least 512) is **atomic**: it won't be interleaved with other writers' data. Larger writes may be split and interleaved. This is why many processes can safely log short lines into one pipe.

### Named pipes (FIFOs)

Anonymous pipes commonly connect processes that inherit them, but descriptors can also be passed to unrelated processes over Unix sockets. A **FIFO** is a pipe with a name in the file system, so unrelated processes can find it:

```
$ mkfifo /tmp/jobs
$ cat /tmp/jobs &          # reader
$ echo "build" > /tmp/jobs # writer
build
```

The data still goes through a kernel buffer; nothing is written to disk.

## Signals: asynchronous notifications

A **signal** is a small integer delivered to a process to say "something happened". It carries almost no data, just the signal number (plus a little metadata with `SA_SIGINFO`). Signals are how the kernel and other processes interrupt you.

| Signal | Typical cause | Default |
|---|---|---|
| `SIGINT` (2) | Ctrl-C | terminate |
| `SIGTERM` (15) | `kill`, shutdown | terminate |
| `SIGKILL` (9) | `kill -9`, OOM killer | terminate |
| `SIGSEGV` (11) | bad memory access | core dump |
| `SIGPIPE` (13) | write to dead pipe | terminate |
| `SIGCHLD` (17) | child exited | ignore |

(Numbers are for Linux on x86 and ARM.) A process can, for most signals, **ignore** it, **block** it (hold it pending), or install a **handler**. `SIGKILL` and `SIGSTOP` are the exceptions: they can't be caught, blocked or ignored, though permissions, init semantics and uninterruptible waits can prevent or delay the expected effect.

The kernel delivers a pending signal when the target next returns from kernel to user mode: after a syscall, an interrupt or being scheduled. If a handler is installed, the kernel arranges for the process to run it, then resume where it was.

### Writing a safe handler

A handler can run *between any two instructions* of your program, including in the middle of `malloc` or `printf`. If the handler calls `malloc` too, the allocator's internal state may be half-updated and you get corruption or deadlock. Only **async-signal-safe** functions (listed in `signal-safety(7)`: `write`, `_exit`, `kill` and others) may be called. The standard pattern is to set a flag and do the real work in the main loop:

```c
static volatile sig_atomic_t stop;

static void on_term(int sig) {
    (void)sig;
    stop = 1;
}

int main(void) {
    struct sigaction sa = {0};
    sa.sa_handler = on_term;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGTERM, &sa, NULL);
    while (!stop)
        do_work();
    cleanup();   /* flush, close */
    return 0;
}
```

This is a schematic shutdown loop: include `<signal.h>`, define the work and cleanup routines, check sigaction errors and ensure do_work returns or responds to shutdown. A flag alone does not wake an indefinitely blocked operation. `docker stop` sends `SIGTERM`, waits a grace period (10 seconds by default), then sends `SIGKILL`. Kubernetes does the same with a 30-second default. A service that ignores `SIGTERM` gets killed mid-request.

> [!warning] Standard signals don't queue
> A standard signal is a single pending bit. If three children exit before your `SIGCHLD` handler runs, the handler may run once. Never count signals; reap in a `waitpid(-1, &st, WNOHANG)` loop while returns are positive; handle -1, including EINTR and ECHILD, as well as 0. Real-time signals (`SIGRTMIN` to `SIGRTMAX`) do queue.

Modern Linux code often avoids handlers altogether: `signalfd` turns signals into readable events on a file descriptor, which fits neatly into an `epoll` loop.

## Shared memory: avoiding payload copies

With pipes and sockets, data is copied twice: from the sender's buffer into the kernel, then from the kernel into the receiver's buffer, with a syscall on each side. **Shared memory** maps the *same physical pages* into both processes' address spaces. After setup, payload can be accessed with loads and stores without copying it through a kernel channel. Synchronisation, notification, cache coherence and page faults still have costs.

```c
/* creator initialises; peers attach */
int fd = shm_open("/stats",
                  O_CREAT | O_RDWR, 0600);
ftruncate(fd, 4096);
long *p = mmap(NULL, 4096,
               PROT_READ | PROT_WRITE,
               MAP_SHARED, fd, 0);
p[0] = 42; /* publish with proper sync */
```

On Linux, POSIX shared memory objects live in the `tmpfs` at `/dev/shm`. You can also share memory by `mmap`ing an ordinary file with `MAP_SHARED`, or by creating an anonymous `MAP_SHARED` mapping before `fork`.

The speed comes with responsibility:

- **No synchronisation is provided.** Two processes doing `p[0]++` can lose updates, exactly like two threads. Use a process-shared mutex or semaphore. Atomics require a platform/implementation that supports the chosen atomic representation across processes; non-lock-free atomics may use unsuitable process-local locks.
- **No notification.** The reader doesn't know new data has arrived. You need a semaphore, a futex, or a separate pipe or socket to say "look now".
- **Pointers don't travel.** The region may be mapped at different virtual addresses in each process, so store validated offsets or another relocatable representation rather than assuming raw pointers are usable.
- **Names outlive processes.** An object stays in `/dev/shm` until `shm_unlink` or reboot. A crashed process can leak it.

PostgreSQL is a classic user: each client connection is a separate backend process, and they all share the buffer cache and lock tables in shared memory. Chromium and many audio and video pipelines use shared memory to move large buffers between processes.

## Message queues: kernel-managed mailboxes

A **message queue** keeps message boundaries and lets unrelated processes exchange discrete messages through a named kernel object. POSIX queues (`mq_open`, `mq_send`, `mq_receive`) add a **priority** per message: `mq_receive` returns the oldest available message at the highest available priority.

```c
struct mq_attr a = {
    .mq_maxmsg = 10,
    .mq_msgsize = 256 };
mqd_t q = mq_open("/jobs",
                  O_CREAT | O_RDWR,
                  0600, &a);
mq_send(q, "resize img7", 12, 5);
```

Queues are bounded: on Linux the defaults allow 10 messages of up to 8 KiB, tunable under `/proc/sys/fs/mqueue/`. A full queue blocks `mq_send`, which gives natural back-pressure. The older System V API (`msgget`, `msgsnd`) still exists but is awkward; prefer POSIX. In practice many teams reach for sockets instead, because they work the same way locally and across a network.

## Sockets: bidirectional and general

**Unix domain sockets** (`AF_UNIX`) use the socket API but stay on one machine. They're addressed by a path such as `/var/run/docker.sock` or by an abstract name. Compared with pipes they are:

- **Bidirectional**: one connection carries requests and replies.
- **Client–server**: many clients can `connect` to one listening server, which `accept`s each.
- **Message-capable**: `SOCK_STREAM` is a byte stream, while `SOCK_DGRAM` and `SOCK_SEQPACKET` keep message boundaries (and on Unix sockets, datagrams are reliable).
- **Able to pass file descriptors**. With `sendmsg` and an `SCM_RIGHTS` control message, a process can hand an open fd to another. The receiver gets a new fd number referring to the same open file. Wayland clients pass buffer fds to the compositor this way, and privilege-separated servers use it so a privileged process opens files or sockets and gives them to a sandboxed worker.
- **Able to identify the peer**: `SO_PEERCRED` reports the connecting process's PID, UID and GID, checked by the kernel. PostgreSQL's `peer` authentication and the D-Bus daemon rely on this.

Because they skip the TCP/IP stack (no checksums, no congestion control, no loopback routing), Unix sockets avoid those TCP/IP protocol layers, but their performance relative to loopback TCP requires a workload-specific measurement. That's why PostgreSQL and MySQL clients use a Unix socket by default for local connections, and Redis can listen on one too.

**TCP sockets** provide the network-capable choice in this comparison; UDP and other network transports also exist. Writing to a socket interface means a service can later be split onto another host with little code change, which is a strong reason to default to sockets. D-Bus on Linux desktops and Android's Binder are higher-level IPC systems: D-Bus runs over Unix sockets, while Binder is its own kernel driver.

## Choosing a mechanism

| Need | Use |
|---|---|
| Stream between parent and child | pipe |
| Unrelated processes, simple stream | FIFO |
| "Stop", "reload", "child died" | signal |
| Bulk data, lowest latency | shared memory + a sync primitive |
| Discrete prioritised messages | POSIX message queue |
| Request/reply, fd passing, auth | Unix socket |
| Across machines | TCP socket |

A useful mental model is cost per message. Conventional read/write channel use often copies bytes into and out of kernel buffers. Batching and zero-copy APIs change the per-message costs, and a wake-up does not imply a fixed switch count. Shared memory avoids those payload copies but still pays synchronisation, coherence and notification costs. Large systems often combine them: a Unix socket for control messages and fd passing, and shared memory for the bulk data.

## Pitfalls

- **Forgetting to close unused pipe ends.** The reader never sees EOF because some process (often itself) still holds a write end. Close every end you don't use, straight after `fork`.
- **Assuming message boundaries on a stream.** One `write` doesn't equal one `read`. Frame your messages.
- **Unsafe signal handlers.** `printf`, `malloc` or taking a lock in a handler can deadlock. Set a flag or use `signalfd`.
- **Counting signals.** They coalesce. Reap children in a loop.
- **Dying on `SIGPIPE`.** A server writing to a client that disconnected is killed silently. Network servers usually ignore `SIGPIPE` and handle `EPIPE`, or pass `MSG_NOSIGNAL` to `send`.
- **Leaking named objects.** FIFOs, `/dev/shm` objects, message queues and socket paths persist after a crash. Unlink them on startup or shutdown.

> [!note] Content gap: IPC performance
> No reproducible IPC benchmark is supplied. Universal fastest-channel rankings and fixed copy/syscall counts are omitted. Code fragments illustrate mechanisms and need headers, error handling, ownership and synchronisation before production use.

## Key takeaways
- Pipes are one-way, bounded byte streams (query the actual Linux capacity); readers get EOF only when every write end is closed, and writes of up to `PIPE_BUF` (4,096) bytes are atomic.
- Signals are asynchronous notifications with almost no payload; `SIGKILL` and `SIGSTOP` can't be caught, standard signals don't queue, and handlers may only call async-signal-safe functions.
- Shared memory can avoid kernel-mediated payload copies, but requires synchronisation and notification; fastest depends on the workload.
- POSIX message queues keep message boundaries and priorities; Unix domain sockets are bidirectional, can pass file descriptors and verify peer credentials.
- Pick by need: pipes for simple streams, signals for events, shared memory for bulk data, sockets for request/reply and anything that might one day cross machines.

## Further reading
- [pipe(7) — Linux manual page](https://man7.org/linux/man-pages/man7/pipe.7.html)
- [signal(7) — Linux manual page](https://man7.org/linux/man-pages/man7/signal.7.html)
- [signal-safety(7) — Linux manual page](https://man7.org/linux/man-pages/man7/signal-safety.7.html)
- [shm_overview(7) — Linux manual page](https://man7.org/linux/man-pages/man7/shm_overview.7.html)
- [mq_overview(7) — Linux manual page](https://man7.org/linux/man-pages/man7/mq_overview.7.html)
- [unix(7) — Linux manual page](https://man7.org/linux/man-pages/man7/unix.7.html)
- [Inter-process communication — Wikipedia](https://en.wikipedia.org/wiki/Inter-process_communication)
