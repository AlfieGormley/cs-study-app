---
id: fs-vfs-lookup
title: The VFS and path permissions
level: basic
minutes: 2
summary: The VFS exposes common objects and operation tables across filesystems.
sourceLesson: fs-file-abstraction
---

This unit focuses on the VFS and path permissions. The preceding units provide the file and storage concepts used here.

## The VFS: one interface, many file systems

Linux supports dozens of file systems: ext4, XFS, Btrfs, FAT, NFS, and in-memory ones like `tmpfs` and `procfs`. Many common operations work across them, although features and semantics still vary, because of the **Virtual File System** (VFS) layer.

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

The VFS also keeps the **dentry cache**, so a dentry-cache hit can avoid repeated name-to-inode lookup work for paths such as `/usr/lib/python3/os.py`, and it owns the **page cache** (covered in the page-cache units), so most file systems share the same caching code.

### Path resolution

To open `/home/alfie/notes.txt`, the kernel:

1. Starts at the root directory's inode.
2. Looks up `home` in it (needs **execute** permission on `/`).
3. Looks up `alfie` in `home`, then `notes.txt` in `alfie`, checking execute permission at each step.
4. Checks the requested access (read, write) against `notes.txt` itself.
5. Allocates a `struct file` and returns the lowest free fd.

This is why a directory needs the `x` bit for you to reach anything inside it, even if the file itself is world-readable.

## Key takeaways
- The VFS exposes common objects and operation tables across filesystems.
- Searching each parent directory needs execute permission before the final file access is checked.

## Further reading
- [OSTEP: Interlude: Files and Directories (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-intro.pdf)
- [Overview of the Linux Virtual File System — kernel.org](https://www.kernel.org/doc/html/latest/filesystems/vfs.html)
- [open(2) — Linux manual page](https://man7.org/linux/man-pages/man2/open.2.html)
- [dup(2) — Linux manual page](https://man7.org/linux/man-pages/man2/dup.2.html)
- [File descriptor — Wikipedia](https://en.wikipedia.org/wiki/File_descriptor)
- [Everything is a file — Wikipedia](https://en.wikipedia.org/wiki/Everything_is_a_file)
