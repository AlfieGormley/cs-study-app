---
id: fs-file-abstraction
title: The file abstraction
level: basic
minutes: 12
summary: Files, directories and paths, file descriptors and the open/read/write/close calls, the three tables behind every descriptor, the VFS layer and what "everything is a file" really means on Linux.
---

A disk is just a huge array of numbered blocks. Nobody wants to write a program that says "put these bytes in block 81,442". The **file system** gives us something far nicer: named, growable sequences of bytes, organised into a tree.

That idea, the **file**, is one of the most successful abstractions in computing. Unix extended this model: on Linux, disks, terminals, pipes, sockets and even kernel statistics all look like files. This lesson covers what a file is to a program, and how the kernel makes so many different things look the same.

## Files, directories and paths

An ordinary **regular file** presents a byte sequence whose application-level format is not imposed by the OS. Special files such as devices and directories have additional semantics. Whether it holds a JPEG or a database is up to the program reading it. The kernel tracks its size, owner, permissions and timestamps.

A **directory** is a special file that maps names to files. Directories contain directories, which gives a tree rooted at `/`.

A **path** names a file by walking that tree:

- **Absolute**: starts at the root, e.g. `/home/alfie/notes.txt`.
- **Relative**: normally starts at the process's current working directory (or a supplied directory descriptor for calls such as openat), e.g. `notes.txt` or `../docs/a.md`.
- `.` means "this directory" and `..` means "the parent".

> [!note] Names are not part of the file
> On Unix, a file's name lives in the *directory*, not in the file. One file can have several names (hard links), and a file can exist with no name at all while it is open. The next lesson shows how.

Other file systems (a USB stick, a network share) are attached into the tree at a **mount point**, so a process sees a unified tree within its mount namespace and root. Containers or other processes can see different trees. `/` might be ext4 on an NVMe drive while `/mnt/usb` is FAT32.

## The system call interface

Programs use files through a handful of system calls. The core four:

| Call | Does |
|---|---|
| `open(path, flags)` | Returns a file descriptor |
| `read(fd, buf, n)` | Reads up to n bytes |
| `write(fd, buf, n)` | Writes up to n bytes |
| `close(fd)` | Releases the descriptor |

A **file descriptor** (fd) is a small non-negative integer that names an open file *within one process*. By convention, descriptors 0, 1 and 2 are standard input, output and error, but they may be closed or redirected and processes can inherit additional descriptors. `open` returns the lowest unused number, so the first file you open is usually 3.

Python's `os` module exposes the raw calls (the built-in `open()` adds buffering on top):

```python
import os

fd = os.open("demo.txt",
             os.O_WRONLY | os.O_CREAT
             | os.O_TRUNC, 0o644)
print(fd)                    # often 3
n = os.write(fd, b"hello world\n")
print(n)                     # 12
os.close(fd)

fd = os.open("demo.txt", os.O_RDONLY)
print(os.read(fd, 5))        # b'hello'
print(os.read(fd, 100))      # b' world\n'
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
    while view:
        n = os.write(fd, view)
        if n <= 0:
            raise OSError("write stalled")
        view = view[n:]
```

Forgetting this loop is a bug that can appear under load or other short-transfer conditions, when sockets and pipes start returning partial results.

## Behind the number: three tables

A descriptor is an index into a table. In fact there are three levels:

```
 process A fd table
 +---+
 | 3 |--+
 | 4 |--|--+     open file table
 | 5 |--+  |    (system-wide)
 +---+  |  |   +--------------+
        +----->| offset=5     |--+
           |   | flags=RDONLY |  |
           |   +--------------+  |  inode
           +-->| offset=0     |--+->+------+
               | flags=RDONLY |     | size |
               +--------------+     | perms|
                                    +------+
```

1. **Per-process fd table**: maps the integer to an entry in the open file table.
2. **Open file table** (the kernel calls each entry an *open file description*, or `struct file`): holds the **current offset**, access mode and file-status flags. Descriptor flags such as close-on-exec belong to the descriptor entry; creation flags are not all retained as status flags.
3. **Inode**: the file itself, with its size, permissions and the location of its data. In the simplified ordinary-filesystem model, open descriptions of the same inode share the cached inode object; filesystem instances and layered/network implementations add detail.

This structure explains behaviour that otherwise looks odd:

- **Two separate `open` calls** on the same file create two open file descriptions, so they have **independent offsets**.
- **`dup(fd)`** creates a second descriptor pointing at the *same* description, so the two **share an offset**.
- **`fork()`** copies the fd table, so parent and child share descriptions and offsets. This is why `cmd > log 2>&1` works: the shell `dup`s stdout into stderr, so both share the same advancing offset rather than two independent offsets.

> [!example] Shared and separate offsets
> `demo.txt` holds `hello world\n`.
> ```
> fd1 = os.open("demo.txt", os.O_RDONLY)
> fd2 = os.open("demo.txt", os.O_RDONLY)
> fd3 = os.dup(fd1)
> os.read(fd1, 5)   # b'hello'
> os.read(fd2, 5)   # b'hello'
> os.read(fd3, 6)   # b' world'
> ```
> fd2 has its own offset, so it starts at 0. fd3 shares fd1's offset, which is already at 5.

### Closing, and files with no name

`close` drops the descriptor. The open file description can be freed when its final reference is released. Mappings, queued descriptor passing or in-flight operations can retain references after the last numeric descriptor closes.

`unlink(path)` removes a *name*. Ordinary unlinked file storage becomes reclaimable once no links and no remaining open/mapping references retain it. Snapshots or filesystem-specific features can retain underlying blocks further. So you can delete a 50 GB log file that a process is still writing, and `df` shows no space freed while its open reference remains; mappings or other references may retain it longer. `lsof +L1` lists such deleted-but-open files. The same trick is used deliberately for temporary files: open, unlink immediately, and the file vanishes automatically when the process dies.

Descriptors are a limited resource. `ulimit -n` shows the per-process limit (the actual soft/hard limits depend on shell, service and system settings). A server that leaks a descriptor per request eventually fails with `EMFILE: Too many open files`.

## The VFS: one interface, many file systems

Linux supports dozens of file systems: ext4, XFS, Btrfs, FAT, NFS, and in-memory ones like `tmpfs` and `procfs`. Many common operations work across them, although capabilities and semantics still vary, because of the **Virtual File System** (VFS) layer.

```
  read(fd, buf, n)       user space
 ---------------------------------------
        VFS              kernel
   (path lookup, perms,
    page cache, fds)
   |       |       |        |
  ext4    XFS     NFS     procfs
   |       |       |        |
  NVMe   SATA   network   (kernel
  SSD    disk             data)
```

The VFS defines a set of common objects, and each file system supplies the functions that operate on them:

| VFS object | Represents |
|---|---|
| superblock | A mounted file system |
| inode | One file or directory |
| dentry | A name in a path |
| file | One open file description |

Each file system fills in tables of function pointers such as `file_operations` (read, write, mmap, fsync...) and `inode_operations` (lookup, create, link...). When you call `read`, the VFS finds the `struct file`, then calls that file system's read function. It is interface-based polymorphism, written in C.

The VFS also keeps the **dentry cache**, so a cache hit can avoid underlying lookup I/O for paths such as `/usr/lib/python3/os.py`, and it owns the **page cache** (lesson 4), so most file systems share the same caching code.

### Path resolution

To open `/home/alfie/notes.txt`, the kernel:

1. Starts at the root directory's inode.
2. Looks up `home` in it (needs **execute** permission on `/`).
3. Looks up `alfie` in `home`, then `notes.txt` in `alfie`, checking execute permission at each step.
4. Checks the requested access (read, write) against `notes.txt` itself.
5. Allocates a `struct file` and returns the lowest free fd.

This is why a directory needs the `x` bit for you to reach anything inside it, even if the file itself is world-readable.

## "Everything is a file"

Unix's big idea is that one interface (open, read, write, close) works for nearly everything:

- **Devices**: `/dev/sda` is a whole disk, `/dev/null` discards writes, `/dev/urandom` produces random bytes.
- **Pipes**: `ls | wc -l` connects two processes with a pair of descriptors.
- **Sockets**: once connected, a TCP socket accepts `read` and `write`.
- **Kernel state**: `/proc/self/status` shows your own process; `/sys/block/nvme0n1/queue/scheduler` exposes the I/O scheduler.

```
$ head -c 8 /dev/urandom | xxd
$ cat /proc/loadavg
0.42 0.37 0.31 1/523 81234
```

The payoff is composability: `cat`, `grep` and your own programs can reuse byte-stream operations for many of these, while seeking, readiness and device-specific behavior can differ.

> [!warning] Not quite everything
> The slogan describes a broad interface convention, not literally every kernel resource. Sockets need `socket`, `bind` and `connect` before they behave like files, devices need `ioctl` for anything beyond reading and writing (setting a terminal's baud rate, ejecting a disk), and network interfaces such as eth0 are not ordinary /dev stream nodes; related attributes do appear under /sys/class/net. Plan 9, Unix's successor from Bell Labs, took the idea much further.

I/O APIs such as readiness-oriented `epoll` and submission/completion-oriented `io_uring` also work in terms of descriptors; they get their own treatment in the next module.

## Pitfalls

- **Assuming `read` fills the buffer.** Always loop, or use a buffered wrapper.
- **Leaking descriptors.** Use `with open(...)` in Python, or `try/finally` around `os.close`.
- **Expecting `close` to mean "on disk".** It doesn't. Data may sit in memory for many seconds (lesson 3 covers `fsync`).
- **Relying on `O_APPEND` over NFS.** On a local file system, "seek to end and write" happens as one atomic step. NFS has no atomic append, so concurrent appenders can overwrite each other.

## Key takeaways
- An ordinary regular file exposes bytes; a directory maps names to files; mounts join file systems into one tree.
- A file descriptor indexes a per-process table, which points to a shared open file description (offset, flags), which points to the inode.
- Separate `open` calls get separate offsets; `dup` and `fork` share them.
- `read` and `write` can be short; production code must loop.
- Unlinking removes a name; storage can be reclaimed after links and retaining references (including mappings) disappear, subject to filesystem features.
- The VFS gives every file system the same interface through superblock, inode, dentry and file objects.

## Further reading
- [OSTEP: Interlude: Files and Directories (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-intro.pdf)
- [Overview of the Linux Virtual File System — kernel.org](https://www.kernel.org/doc/html/latest/filesystems/vfs.html)
- [open(2) — Linux manual page](https://man7.org/linux/man-pages/man2/open.2.html)
- [dup(2) — Linux manual page](https://man7.org/linux/man-pages/man2/dup.2.html)
- [File descriptor — Wikipedia](https://en.wikipedia.org/wiki/File_descriptor)
- [Everything is a file — Wikipedia](https://en.wikipedia.org/wiki/Everything_is_a_file)
