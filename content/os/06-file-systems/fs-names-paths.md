---
id: fs-names-paths
title: Files, names and paths
level: basic
minutes: 2
summary: A regular file exposes bytes; directories map names to files.
sourceLesson: fs-file-abstraction
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
> On Unix, a file's name lives in the *directory*, not in the file. One file can have several names (hard links), and a file can exist with no name at all while it is open. The open-file lifetime and link units explain how.

Other file systems (a USB stick, a network share) are attached into the tree at a **mount point**, so a process sees a unified tree within its mount namespace and root. Containers or other processes can see different trees. `/` might be ext4 on an NVMe drive while `/mnt/usb` is FAT32.

## Key takeaways
- A regular file exposes bytes; directories map names to files.
- Absolute and relative paths begin from different places; mounts join filesystem trees.

## Further reading
- [OSTEP: Interlude: Files and Directories (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-intro.pdf)
- [Overview of the Linux Virtual File System — kernel.org](https://www.kernel.org/doc/html/latest/filesystems/vfs.html)
- [open(2) — Linux manual page](https://man7.org/linux/man-pages/man2/open.2.html)
- [dup(2) — Linux manual page](https://man7.org/linux/man-pages/man2/dup.2.html)
- [File descriptor — Wikipedia](https://en.wikipedia.org/wiki/File_descriptor)
- [Everything is a file — Wikipedia](https://en.wikipedia.org/wiki/Everything_is_a_file)
