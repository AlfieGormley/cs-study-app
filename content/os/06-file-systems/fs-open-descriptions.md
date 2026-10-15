---
id: fs-open-descriptions
title: Shared and independent file offsets
level: basic
minutes: 3
summary: Separate opens create independent offsets; dup and fork share an open description.
sourceLesson: fs-file-abstraction
---

This unit focuses on shared and independent file offsets. The preceding units provide the file and storage concepts used here.

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
> # A second open gets a separate offset.
> fd2 = os.open("demo.txt", os.O_RDONLY)
> # Dup shares fd1's advancing offset.
> fd3 = os.dup(fd1)
> os.read(fd1, 5)   # b'hello'
> os.read(fd2, 5)   # b'hello'
> os.read(fd3, 6)   # b' world'
> ```
> fd2 has its own offset, so it starts at 0. fd3 shares fd1's offset, which is already at 5.

## Key takeaways
- Separate opens create independent offsets; dup and fork share an open description.
- Descriptor flags belong to the descriptor, while offsets and status flags belong to the open description.

## Further reading
- [OSTEP: Interlude: Files and Directories (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-intro.pdf)
- [Overview of the Linux Virtual File System — kernel.org](https://www.kernel.org/doc/html/latest/filesystems/vfs.html)
- [open(2) — Linux manual page](https://man7.org/linux/man-pages/man2/open.2.html)
- [dup(2) — Linux manual page](https://man7.org/linux/man-pages/man2/dup.2.html)
- [File descriptor — Wikipedia](https://en.wikipedia.org/wiki/File_descriptor)
- [Everything is a file — Wikipedia](https://en.wikipedia.org/wiki/Everything_is_a_file)
