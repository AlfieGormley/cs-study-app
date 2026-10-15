---
id: rep-bitwise-precedence
title: Reading bitwise operator precedence
level: intermediate
minutes: 3
summary: In C, equality binds tighter than bitwise AND.
sourceLesson: rep-bitwise
---

This unit continues the preceding material on unsigned bit patterns and masks.

## Precedence traps

In C, `&`, `^` and `|` bind **more loosely** than `==`. This is a historical leftover from before C had `&&`.

```c
/* Compare the unintended / intended */
/* tests. */
if (x & 1 == 0)    /* x & (1 == 0) */
                   /* = x & 0 = 0   */
if ((x & 1) == 0)  /* what you meant */
```

Python fixed this: its bitwise operators bind tighter than comparisons, so `x & 1 == 0` means `(x & 1) == 0`. Code ported between the two languages can therefore change meaning silently. Shifts also bind looser than `+` in both languages: `1 << n - 1` is `1 << (n - 1)`. When in doubt, add brackets.

### Read the expression in stages

Take the displayed C condition with an even input such as six. Equality is evaluated first: comparing one with zero produces false, represented as zero. Bitwise AND then receives the original value and zero, so its result is zero for every input. The condition therefore takes the false branch; an even number does not rescue it.

Bracketing the mask operation first instead asks whether the low bit is clear. An even input has a zero low bit, so comparing that masked result with zero succeeds. An odd input has a one low bit and fails that comparison.

Do not infer a language's precedence from a similar-looking operator in another language. When reviewing a mask test, identify the mask, bracket the extraction, and then compare with the expected masked value. Brackets explain the intended operation order to the next reader as well as to the parser.

## Key takeaways
- In C, equality binds tighter than bitwise AND.
- Use brackets to express the intended test across languages.

## Further reading
- [C working draft N3220](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf)
- [Python bitwise integer operations](https://docs.python.org/3/library/stdtypes.html#bitwise-operations-on-integer-types)
