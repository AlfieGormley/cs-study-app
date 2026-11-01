---
id: sys-bounded-strings
title: Bounded strings and explicit truncation
level: basic
minutes: 3
sourceLesson: sys-memory-bugs
summary: Check snprintf for a negative error before interpreting its non-negative required length.
---

A destination capacity limits writes; it does not decide whether losing part of a name or identifier is acceptable. Start with a valid NUL-terminated source and treat truncation as a separate outcome.

The fix is to pass the destination size and handle truncation deliberately:

```c
void greet(const char *name) {
    char buf[16];
    /* Bound writes, then test lost text. */
    int n = snprintf(buf, sizeof buf,
                     "%s", name);
    if (n < 0 || (size_t)n >= sizeof buf) {
        /* Reject errors and truncation. */
        return;
    }
    /* Print the validated string. */
    printf("Hello, %s\n", buf);
}
```

With arguments that are valid and non-overlapping, `snprintf` bounds output by the supplied capacity and terminates it when that capacity is non-zero. Its non-negative return reports the required length excluding NUL; a negative return reports an error. The example rejects both errors and truncation. The source must itself be a valid NUL-terminated string.

The truncation test `(size_t)n >= sizeof buf` follows from what the return value means. `snprintf` returns the length the *complete* text would have had, not counting the NUL. The complete text fits only if there is room for all of it plus one NUL byte, so a return value equal to or greater than the buffer's capacity means some text was cut off. A return value smaller than the capacity means everything fitted.

For example, formatting the 11-character `"hello world"` into an 8-byte buffer returns 11. Since 11 is at least 8, the output was truncated: the buffer holds the first 7 characters, `hello w`, then the NUL. In the `greet` function above, a 15-character name passes and a 16-character name is rejected.

> [!warning] strncpy is not a safe strcpy
> `strncpy(dst, src, n)` stops at `n` bytes, but if the source is `n` bytes or longer it does **not** write a terminating NUL. An unbounded string operation on that unterminated destination violates its input requirements and can read past the end. Prefer `snprintf`, or `strlcpy` where available (it was added to POSIX in the 2024 edition and, like `snprintf`, returns the full source length so you can detect truncation).

## Key takeaways
- Check snprintf for a negative error before interpreting its non-negative required length.
- A return at least as large as the destination capacity means truncation.
- strncpy can fill its whole destination without writing NUL; bounded writes alone do not make a valid C string.

## Further reading
- [C11 committee draft: objects and library contracts](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Source fortification — glibc](https://sourceware.org/glibc/manual/latest/html_node/Source-Fortification.html)
- [strlcpy — POSIX](https://pubs.opengroup.org/onlinepubs/9799919799/functions/strlcpy.html)
