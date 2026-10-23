---
id: esc-c-values-types
title: C values, declarations and small functions
level: basic
minutes: 4
summary: Choose a value type deliberately and follow a small C function call.
---

Firmware spends much of its time representing things: a sampled value, a count, a setting and whether an operation succeeded. C makes the representation part of the program. A **declaration** gives an object a type and a name; an **initialiser** gives it its starting value. A semicolon ends the declaration.

## Read a small complete program

This is a complete C11 program for a computer, using a target that provides the exact-width integer types. The headers make library declarations and type names available; they do not initialise a microcontroller. `main` is this hosted program's entry function. The braces enclose a function's statements.

```c
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

bool above_limit(uint16_t sample) {
    const uint16_t limit = 300u;
    return sample > limit;
}

int main(void) {
    uint16_t reading = 320u;
    bool high = above_limit(reading);
    // Print false as 0, true as 1.
    printf("%u\n", (unsigned)high);
    return 0;
}
```

It prints `1`. The function accepts one function argument, named `sample` inside the function. `return` sends the comparison result to the caller. `bool` represents false or true; `<stdbool.h>` supplies the convenient C11 names. The `u` suffix makes a literal unsigned. The cast `(unsigned)` gives `printf` the argument type its `%u` conversion expects. A function call does not automatically share a caller's local variable: here the value is passed into the function parameter.

## Size and meaning are separate

An **unsigned integer** represents non-negative integers. `<stdint.h>` provides names such as `uint16_t` when the implementation supports the corresponding exact-width type. `uint16_t` has exactly 16 value bits and no padding; it can represent 0 through 65,535. These exact-width names are optional in C11, so check the target toolchain. Plain `int` is not guaranteed to be 32 bits.

`const` means this declaration does not permit modifying `limit` through that name. It does not promise storage in flash. A type also does not encode a measurement unit: a count in milliseconds and a count in microseconds may have the same C type. Put the unit in the name and document the range.

> [!analogy] Real-world analogy: choosing a labelled measuring jar
> A labelled jar tells you what belongs inside and how much it can hold. Choosing a bigger jar does not tell you whether its contents are flour or sugar.
>
> **How it maps:** An integer type defines a representable range; a name and contract explain what that value means. Choose both before using the value in control decisions.
>
> **Where it stops:** C does not enforce a physical unit just because a name includes it. Conversions and arithmetic still follow language rules and can lose information.

## Do not treat narrowing as validation

Converting 256 to `uint8_t`, where that type exists, produces 0 under C's unsigned conversion rules. It does not report an invalid input. A **cast** requests a conversion; it is not a range check. Check a value's allowed range before storing it in a narrower type. Signed overflow is a different case and must not be assumed to wrap.

## Key takeaways
- Declarations name a type and an object; function parameters receive argument values.
- Exact-width unsigned types make a chosen representation explicit when the target provides them.
- Keep units and valid ranges in the program's names and contracts; casts do not validate input.

## Further reading
- [C11 draft: declarations, functions and integer types](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
