---
id: proc-process-address-example
sourceLesson: proc-process-abstraction
title: "Pointers, literals and randomised addresses"
level: basic
minutes: 2
summary: "An initialised pointer and the string literal it points at are different objects."
---

An initialised pointer and the string literal it points at are different objects. This lesson focuses on pointers, literals and randomised addresses.

## Seeing it for yourself


```c
#include <stdio.h>
#include <stdlib.h>

int g_init = 42;      /* data   */
int g_zero;           /* BSS    */
const char *s = "hi"; /* pointer: data */

int main(void) {
    int local = 1;               /* stack */
    int *h = malloc(16);         /* heap  */
    /* Print locations, not stored */
    /* values. */
    printf("text  %p\n", (void *)main);
    printf("data  %p\n", (void *)&g_init);
    printf("bss   %p\n", (void *)&g_zero);
    printf("heap  %p\n", (void *)h);
    printf("stack %p\n", (void *)&local);
    /* Release the allocation after */
    /* viewing. */
    free(h);
    return 0;
}
```

This illustrates one conventional executable layout; exact ordering and locations depend on the ABI, linker, allocator and ASLR settings. ASLR does not promise a different value on every run. `cat /proc/<pid>/maps` lists every region of a live process with its permissions and backing file.

> [!note] `s` versus `*s`
> In the example, the pointer variable `s` is an initialised global, so it lives in **data segment**. The string `"hi"` it points to lives in **rodata**. Writing through this `const char *` is rejected without a cast; modifying the literal through a writable-typed pointer is undefined behaviour and commonly faults. Reassigning `s = "yo"` is valid.

## Key takeaways
- An initialised pointer and the string literal it points at are different objects.
- Address observations depend on build options, allocator behaviour and ASLR.

## Further reading
- [The Abstraction: The Process — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-intro.pdf)
- [The Abstraction: Address Spaces — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-intro.pdf)
- [proc(5) — Linux manual page](https://man7.org/linux/man-pages/man5/proc.5.html)
- [Process control block — Wikipedia](https://en.wikipedia.org/wiki/Process_control_block)
- [Process state — Wikipedia](https://en.wikipedia.org/wiki/Process_state)
- [Address space layout randomization — Wikipedia](https://en.wikipedia.org/wiki/Address_space_layout_randomization)
