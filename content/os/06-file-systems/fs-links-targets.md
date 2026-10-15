---
id: fs-links-targets
title: File links and directory link counts
level: intermediate
minutes: 4
summary: Hard links name the same inode; symbolic links store paths and can dangle.
sourceLesson: fs-on-disk-structures
---

This unit focuses on hard links and symbolic links. The preceding units provide the file and storage concepts used here.

## Hard links and symbolic links

Since names live in directories and point to inode numbers, nothing stops two names pointing at the **same** inode. That is a **hard link**.

```
$ echo data > a
$ ln a b          # hard link
$ ln -s a c       # symbolic link
$ ls -li
7342 -rw-r--r-- 2 alfie a
7342 -rw-r--r-- 2 alfie b
7400 lrwxrwxrwx 1 alfie c -> a
```

`a` and `b` share inode 7342, and its **link count** is 2. Neither is "the original". `rm a` simply removes one name and drops the count to 1. Storage can be reclaimed after the last link and retaining open/mapping reference disappear; snapshots or other filesystem features can retain blocks further.

A **symbolic link** (symlink) is a different kind of file, with its own inode, whose content is a **path**. The kernel follows it during path resolution.

The Python alternative below starts in a fresh directory containing only `a`, with the text `data` followed by a newline. Do not first create `b` or `c` using the preceding shell example.

```python
import os
# Both names refer to the same inode.
os.link("a", "b")
# This separate file stores the path "a".
os.symlink("a", "c")
print(os.stat("a").st_nlink)   # 2
# Remove a name; the name "b" keeps data.
os.unlink("a")
print(os.stat("b").st_nlink)   # 1
# Following c now reaches a missing name.
print(os.path.exists("c"))     # False
with open("b") as f:
    print(f.read())           # data
```

After `a` is removed, `b` still works (it names the inode directly) but `c` is **dangling**: it points to a name that no longer exists.

| | Hard link | Symlink |
|---|---|---|
| Points to | inode | path |
| Own inode | no | yes |
| Across file systems | no | yes |
| To directories | no | yes |
| Survives target rm | yes | no (dangles) |

Hard links can't cross file systems because inode numbers are only unique within one. They aren't allowed to directories (except the special `.` and `..`) because that could create cycles in the tree and confuse tools like `find` and `fsck`.

### Directory link counts

Directories have link counts too, and they follow a simple rule. A new empty directory on ext4 has link count 2: its name in the parent, and its own `.` entry. Each subdirectory adds 1, because the subdirectory's `..` points back. Ordinary files inside the directory add nothing, because their entries point at their own inodes.

```formula
L_dir = 2 + d
L_dir = 2 + 3 = 5
where
L_dir: the link count of a directory: how many directory entries point at its inode
d: the number of immediate subdirectories it contains (here 3)
In words: two links for the directory's own name and its "." entry, plus one for each subdirectory's ".." entry.
```

So an ordinary small directory with three subdirectories has link count five. With dir_nlink and sufficiently large directory counts, ext4 can use one as an unknown-count marker, and some file systems (Btrfs) always report 1 for directories, so scripts shouldn't rely on the rule.

ext4 stores short symlink targets (under 60 bytes) inside the inode itself, a **fast symlink**, so obtaining the target needs no separate payload-block read when the inode is available. The inode and target path can still require lookup I/O.


## Key takeaways
- Hard links name the same inode; symbolic links store paths and can dangle.
- Unlinking a name does not destroy another hard link to the same file.

- Small ext4 directories normally count their parent name, dot entry and child dot-dot entries.
- That counting rule has filesystem and large-directory exceptions.


## Further reading
- [OSTEP: File System Implementation (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-implementation.pdf)
- [OSTEP: Locality and the Fast File System (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-ffs.pdf)
- [ext4 data structures: the inode block map — kernel.org](https://www.kernel.org/doc/html/latest/filesystems/ext4/ifork.html)
- [inode(7) — Linux manual page](https://man7.org/linux/man-pages/man7/inode.7.html)
- [symlink(7) — Linux manual page](https://man7.org/linux/man-pages/man7/symlink.7.html)
- [File Allocation Table — Wikipedia](https://en.wikipedia.org/wiki/File_Allocation_Table)
- [Extent (file systems) — Wikipedia](https://en.wikipedia.org/wiki/Extent_(file_systems))
