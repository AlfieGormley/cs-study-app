---
id: sys-format-input
title: Keep untrusted text out of format strings
level: intermediate
minutes: 3
sourceLesson: sys-memory-bugs
summary: A constant format and a valid string argument keep message contents as data.
---

## Format-string bugs

```c
/* BUG: text controls the directives. */
printf(user_input);
/* Fixed: percent signs remain literal. */
printf("%s", user_input);
```

An untrusted format can request conversions such as `%x` or `%n`. Missing or incorrectly typed arguments invoke undefined behaviour; depending on the calling convention and program, this can expose values or attempt a memory write. `%n` stores a character count through its supplied pointer. Use a fixed format and valid string argument. GCC/Clang warnings such as `-Wformat -Wformat-security -Werror=format-security` reject the illustrated no-extra-arguments mistake.

A format string is a small instruction language for output. Its directives tell the function which extra arguments to consume and what types they have. User text should be an argument to that language, not the language itself.

> [!analogy] Real-world analogy: a mail-merge template
> A mail merge fills a letter template such as "Dear {name}, your balance is {balance}". If a customer types "{balance} {account number}" as their name and the software uses the name *as the template*, the merge fills in those fields for them.
>
> **How it maps:** The template is the format string and the `{...}` fields are `%` directives. Passing user text as the template, as in `printf(user_input)`, lets the user choose which fields are filled. `printf("%s", user_input)` puts the text into a fixed slot, where braces or percent signs are just characters.
>
> **Where it stops:** A mail merge with a missing field usually prints a blank or an error. `printf` has no list of the arguments actually supplied, so a directive with no matching argument is undefined behaviour: it may print unrelated values, or with `%n`, attempt a write.

For example, a message containing the literal characters `%x` should print those characters. `printf("%s", user_input)` and `fputs(user_input, stdout)` do that for a valid C string. Neither function makes an invalid pointer or an unterminated array safe.

`%n` is different from ordinary output conversions: with a valid pointer argument it records how many characters have been emitted. When an untrusted format asks for arguments the caller never supplied, there is no portable output trace to predict. Test the fixed version for literal output, and use compiler diagnostics to reject the specific faulty call. Filtering newlines or enlarging the message buffer does not change which parameter is treated as the format.

## Key takeaways
- A constant format and a valid string argument keep message contents as data.
- fputs writes a string without interpreting percent directives.
- Format warnings can reject the illustrated missing-argument misuse; they do not prove every formatting call is valid.

## Further reading
- [C11 committee draft: objects and library contracts](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Warning options — GCC](https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html)
