---
id: proc-ipc-message-priorities
sourceLesson: proc-ipc
title: "Bounded priority message queues"
level: advanced
minutes: 2
summary: "POSIX queues preserve messages and select the oldest among the highest available priority."
---

POSIX queues preserve messages and select the oldest among the highest available priority. This lesson focuses on bounded priority message queues.

## Message queues: kernel-managed mailboxes

A **message queue** keeps message boundaries and lets unrelated processes exchange discrete messages through a named kernel object. POSIX queues (`mq_open`, `mq_send`, `mq_receive`) add a **priority** per message: `mq_receive` returns the oldest available message at the highest available priority.

```c
struct mq_attr a = {
    .mq_maxmsg = 10,
    .mq_msgsize = 256 };
mqd_t q = mq_open("/jobs",
                  O_CREAT | O_RDWR,
                  0600, &a);
/* Send 12 bytes, including the final */
/* NUL. */
/* Priority 5 orders this queued message. */
mq_send(q, "resize img7", 12, 5);
```

Queues are bounded: on Linux the defaults allow 10 messages of up to 8 KiB, tunable under `/proc/sys/fs/mqueue/`. A full queue blocks `mq_send`, which gives natural back-pressure. The older System V API (`msgget`, `msgsnd`) still exists but is awkward; prefer POSIX. In practice many teams reach for sockets instead, because related socket interfaces support local and network communication, although address families, credentials and fd-passing features differ.

## Key takeaways
- POSIX queues preserve messages and select the oldest among the highest available priority.
- Queue bounds create back-pressure and are configurable on Linux.

## Further reading
- [pipe(7) — Linux manual page](https://man7.org/linux/man-pages/man7/pipe.7.html)
- [signal(7) — Linux manual page](https://man7.org/linux/man-pages/man7/signal.7.html)
- [signal-safety(7) — Linux manual page](https://man7.org/linux/man-pages/man7/signal-safety.7.html)
- [shm_overview(7) — Linux manual page](https://man7.org/linux/man-pages/man7/shm_overview.7.html)
- [mq_overview(7) — Linux manual page](https://man7.org/linux/man-pages/man7/mq_overview.7.html)
- [unix(7) — Linux manual page](https://man7.org/linux/man-pages/man7/unix.7.html)
- [Inter-process communication — Wikipedia](https://en.wikipedia.org/wiki/Inter-process_communication)
- [mq_receive priority order](https://man7.org/linux/man-pages/man3/mq_receive.3.html)
