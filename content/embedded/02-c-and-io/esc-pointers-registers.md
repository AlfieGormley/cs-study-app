---
id: esc-pointers-registers
title: Pointers and memory mapped device registers
level: basic
minutes: 4
summary: Separate an address, the object it refers to and a hardware register access.
---

A **pointer** is a value that refers to an object or function. This lesson uses object pointers. Taking an object's address does not copy the object. Dereferencing the pointer accesses the referred-to object, provided that access is valid for its type, alignment and lifetime.

## Address and value are different

In a declaration, `uint32_t *p` means that `p` is a pointer to a `uint32_t` object. In an expression, `&status` obtains `status`'s address, while `*p` accesses the object referred to by `p`. The same `*` character has different jobs in a declaration and an expression.

This complete C11 host program deliberately uses an ordinary RAM object as a model. It does not touch a device or invent a peripheral address:

```c
#include <stdint.h>
#include <stdio.h>

int main(void) {
    volatile uint32_t status = 1u;
    volatile uint32_t *p = &status;
    uint32_t snapshot = *p;
    // Change the original object.
    *p = 2u;
    printf("%u %u\n", (unsigned)snapshot,
           (unsigned)status);
    return 0;
}
```

It prints `1 2` on the host used for this exercise. `snapshot` is an independent stored value; changing `status` through the pointer does not retroactively change the earlier snapshot. In these examples the printed values fit `unsigned`, so those output casts preserve them.

> [!analogy] Real-world analogy: a room number and the room's noticeboard
> A room number tells you where to go; a note copied from the room's noticeboard records what it said at the time you visited.
>
> **How it maps:** A pointer identifies an object to access, while a copied value is a snapshot. Keeping the pointer does not make an old snapshot update itself.
>
> **Where it stops:** A pointer must satisfy C's validity rules. A plausible-looking number is not permission to access memory, and real hardware accesses can have effects that reading a noticeboard does not.

## When an address belongs to hardware

With **memory-mapped I/O**, accesses to specified addresses communicate with peripheral registers. A **register** can expose status, accept a configuration or trigger an operation. The device manual defines its address, access width, permitted operations and effects. Reading one register might consume queued data; writing another might clear a reported event. It need not behave like normal RAM.

Use the vendor SDK's documented accessors or register definitions. A pointer fabricated from a number in a tutorial is not a portable way to locate a peripheral. Never run a raw device-address sketch on a host computer.

## What volatile contributes

Hardware register definitions often use `volatile` to express that accesses have externally observable significance under the implementation's rules. GCC documents its volatile-access behaviour and explains that non-volatile accesses are not ordered by a volatile object. `volatile` does not make a multi-step update atomic, protect shared state, validate a pointer or synchronise threads. Later timing lessons handle concurrent access explicitly.

## Key takeaways
- A pointer refers to an object; a copied value remains a separate snapshot.
- A device register is defined by its manual and can have effects when read or written.
- Volatile access is one part of a hardware interface, not a concurrency solution.

## Further reading
- [C11 draft: address, indirection and qualifiers](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [GCC: volatile accesses and ordering](https://gcc.gnu.org/onlinedocs/gcc/Volatiles.html)
- [RP2040 datasheet: register access and side effects](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
