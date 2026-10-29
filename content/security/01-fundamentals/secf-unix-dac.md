---
id: secf-unix-dac
title: Unix discretionary permissions and octal modes
level: intermediate
minutes: 3
sourceLesson: secf-access-control
summary: DAC normally lets the owner set permissions.
---

## Discretionary access control (DAC)

In **DAC** the **owner** of an object decides who can access it. Unix file permissions are the classic example:

```
$ ls -l report.txt
-rw-r----- 1 alice finance report.txt
 |  |  |
 |  |  other: ---  (no access)
 |  group finance: r--
 owner alice: rw-
```

The permission bits are often written in **octal** (base 8), one digit per class. Each class has three on/off bits, and three bits can count from 0 to 7, which is exactly one octal digit. Read is worth 4, write 2 and execute 1:

```formula reference
d = 4r + 2w + x
where
d: one octal digit of the mode, from 0 to 7, for one class (owner, group or other)
r: 1 if the class may read (an r in the string), 0 if not (a -)
w: 1 if the class may write (a w), 0 if not
x: 1 if the class may execute (an x), 0 if not
4: the place value of the read bit; 2 and 1 are the place values of the write and execute bits, the base-2 place values of the bit patterns 100, 010 and 001
In words: add 4 for read, 2 for write and 1 for execute in each class, so rw-r----- becomes the digits 6, 4 and 0.
```

So `rw-r-----` is set with `chmod 640`. Going the other way, 7 is `rwx`, 5 is `r-x` and 0 is no access.

For ordinary users and these mode bits alone, without extended ACLs or overriding privileges, Unix checks the classes **in order and stops at the first class that matches**: if you're the owner, only the owner bits apply; else if you're in the group, the group bits; else other. So with `chmod 604`, the owner can read and write, any *other* user can read, but members of the group cannot read, because they match the group class first and stop there.

DAC is flexible and intuitive. Its weakness: any program you run acts with your authority, so malware (or a confused user) can share your files with anyone. The owner's discretion is the attacker's discretion.

## Key takeaways
- DAC normally lets the owner set permissions.
- Read, write and execute bits form an octal digit for each class.
- For the stated mode-bit model, stop at the first matching class.

## Further reading
- [Linux inode permissions](https://man7.org/linux/man-pages/man7/inode.7.html)
