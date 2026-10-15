---
id: fs-descriptor-io
title: Descriptors and partial I/O
level: basic
minutes: 3
summary: A descriptor is a process-local handle; open chooses the lowest available number.
sourceLesson: fs-file-abstraction
---

This unit focuses on descriptors and partial I/O. The preceding units provide the file and storage concepts used here.

## The system call interface

Programs use files through a handful of system calls. The essential four:

| Call | Does |
|---|---|
| `open(path, flags)` | Returns a file descriptor |
| `read(fd, buf, n)` | Reads up to n bytes |
| `write(fd, buf, n)` | Writes up to n bytes |
| `close(fd)` | Releases the descriptor |

A **file descriptor** (fd) is a small non-negative integer that names an open file *within one process*. By convention, descriptors 0, 1 and 2 are standard input, output and error, but they may be closed or redirected and processes can inherit additional descriptors. `open` returns the lowest unused number, so the first file you open is usually 3.

Python's `os` module exposes the raw calls (the built-in `open()` adds buffering on top). This isolated regular-file demonstration assumes calls succeed, the small write completes fully, and no other process changes the file:

```python
import os


# Replace prior contents for this demo.
fd = os.open("demo.txt",
             os.O_WRONLY | os.O_CREAT
             | os.O_TRUNC, 0o644)
print(fd)                    # often 3
# This small write reports bytes accepted.
# General output needs the loop below.
n = os.write(fd, b"hello world\n")
print(n)                     # 12
os.close(fd)


# Reopen the existing file for reading.
fd = os.open("demo.txt", os.O_RDONLY)
# Each read advances this open offset.
print(os.read(fd, 5))        # b'hello'
print(os.read(fd, 100))      # b' world\n'
# Positive-length read at EOF is empty.
print(os.read(fd, 100))      # b''
os.close(fd)
```

Three things to notice:

1. **There is a current offset.** Each `read` continues where the last one stopped. `lseek(fd, pos, whence)` moves it.
2. **`read` can return fewer bytes than asked.** Asking for 100 got 7 because the file ended. For a positive-length read of an ordinary regular file or byte stream, an empty result normally signals EOF. A zero-byte request and some special files or zero-length datagrams need different interpretation.
3. **Flags shape behaviour.** `O_CREAT` creates the file if missing, `O_TRUNC` empties it, `O_APPEND` makes every write go to the end, and mode `0o644` requests owner read/write and other read permissions on creation, subject to umask/default ACL rules. It does not reset an existing file's mode.

### Short reads and short writes

`read` and `write` may transfer less than you asked for, and this is not an error. It happens at end of file, on pipes and sockets (you get whatever has arrived), when a signal interrupts the call, or when a disk fills up mid-write. For blocking byte-stream/file output, handle partial progress and errors. This helper propagates errors; nonblocking I/O needs readiness/retry handling, while datagram message boundaries require a different API contract:

```python
def write_all(fd, data):
    view = memoryview(data)
    # Retry only the bytes not yet accepted.
    while view:
        n = os.write(fd, view)
        if n <= 0:
            raise OSError("write stalled")
        # Keep only unwritten bytes.
        view = view[n:]
```

Forgetting this loop is a bug that can appear under load or other short-transfer conditions, when sockets and pipes start returning partial results.

## Key takeaways
- A descriptor is a process-local handle; open chooses the lowest available number.
- Read and write can make partial progress; byte-stream writers must handle that progress.

## Further reading
- [OSTEP: Interlude: Files and Directories (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-intro.pdf)
- [Overview of the Linux Virtual File System — kernel.org](https://www.kernel.org/doc/html/latest/filesystems/vfs.html)
- [open(2) — Linux manual page](https://man7.org/linux/man-pages/man2/open.2.html)
- [dup(2) — Linux manual page](https://man7.org/linux/man-pages/man2/dup.2.html)
- [File descriptor — Wikipedia](https://en.wikipedia.org/wiki/File_descriptor)
- [Everything is a file — Wikipedia](https://en.wikipedia.org/wiki/Everything_is_a_file)
