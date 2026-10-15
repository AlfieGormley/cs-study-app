---
id: proc-ipc-pipe-protocol
sourceLesson: proc-ipc
title: "Pipes, EOF and stream framing"
level: advanced
minutes: 4
summary: "Pipe readers see EOF only after every write end is closed."
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
    /* Drop our writer so EOF can arrive. */
    close(fd[1]);
    char buf[64];
    ssize_t n;
    while ((n = read(fd[0], buf,
                     sizeof buf)) > 0)
        write(1, buf, n);
    _exit(0);
}
/* The parent only produces bytes. */
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

Neither program knows a pipe is involved; they just use fds 0 and 1. When `ls` exits, the last write end closes, `wc` sees EOF and prints its count. This is the `fork`/`exec` gap from the earlier process-creation units doing its job.

### Byte streams have no message boundaries

A pipe carries bytes, not messages. Two `write` calls of 10 bytes each may come out as one 20-byte `read`, or as 7 then 13. If you need messages, add framing: a length prefix, or a delimiter such as a newline.



## Key takeaways
- Pipe readers see EOF only after every write end is closed.
- Byte streams require framing when applications need messages.

## Further reading
- [pipe(7) — Linux manual page](https://man7.org/linux/man-pages/man7/pipe.7.html)
- [signal(7) — Linux manual page](https://man7.org/linux/man-pages/man7/signal.7.html)
- [signal-safety(7) — Linux manual page](https://man7.org/linux/man-pages/man7/signal-safety.7.html)
- [shm_overview(7) — Linux manual page](https://man7.org/linux/man-pages/man7/shm_overview.7.html)
- [mq_overview(7) — Linux manual page](https://man7.org/linux/man-pages/man7/mq_overview.7.html)
- [unix(7) — Linux manual page](https://man7.org/linux/man-pages/man7/unix.7.html)
- [Inter-process communication — Wikipedia](https://en.wikipedia.org/wiki/Inter-process_communication)
