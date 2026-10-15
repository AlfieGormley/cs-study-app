---
id: mem-fork-isolation
sourceLesson: mem-address-spaces
title: Why a forked child has its own values
level: basic
minutes: 3
summary: Relocation, isolation and sparse capacity motivate virtual memory.
---

## Before virtual memory

The earliest machines ran one program at a time, loaded at a fixed physical address. The program used physical addresses directly. That works until you want to run several programs at once (**multiprogramming**), and then three problems appear:

1. **Relocation.** Code containing fixed absolute addresses needs relocation or a translation mechanism when loaded elsewhere; position-independent code and relative addressing can reduce relocation work.
2. **Protection.** Nothing stops a buggy program writing over another program, or over the OS itself.
3. **Capacity.** Every program must fit in physical memory at once, and its size is limited by whatever contiguous space is free.

Virtual memory solves all three. In the framing of the OSTEP textbook, a good virtual memory system offers:

- **Virtual-memory transparency**: programs behave as if they have private memory and need no special code.
- **Translation efficiency**: translation must be fast (hardware does it) and the tables must not waste much space.
- **Memory protection and isolation**: a process cannot read or write memory outside its own address space, and it cannot touch the kernel's memory from user mode.

It also enables things the early designers did not have: sharing read-only library pages between processes, lazily allocating memory only when it is touched, and running programs whose memory is larger than RAM by spilling some to disk.

## Seeing it in C

This program forks a child. The child changes a global; the parent then prints the same variable.

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

int x = 1;

int main(void) {
    /* Child inherits the virtual layout. */
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return 1;
    }
    if (pid == 0) {             /* child */
        /* Parent x keeps its own value. */
        x = 2;
        printf("child  %p %d\n",
               (void *)&x, x);
        return 0;
    }
    wait(NULL);                 /* parent */
    printf("parent %p %d\n", (void *)&x, x);
    return 0;
}
```

Illustrative output (the address varies):

```
child  0x55e4c3a1b010 2
parent 0x55e4c3a1b010 1
```

The child is a copy of the parent, so `x` sits at the same *virtual* address in both. But they have separate address spaces, so the child's write lands in a different physical frame and the parent still sees 1. (The copy-on-write units explain how Linux makes this copy cheaply with copy-on-write.)

## Key takeaways
- Relocation, isolation and sparse capacity motivate virtual memory.
- A child can inherit the same virtual address while its writes remain isolated from the parent.

## Further reading
- [OSTEP: The Abstraction: Address Spaces (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-intro.pdf)
- [OSTEP: Address Translation (base and bounds) (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-mechanism.pdf)
- [OSTEP: Segmentation (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-segmentation.pdf)
- [Virtual memory — Wikipedia](https://en.wikipedia.org/wiki/Virtual_memory)
- [Memory segmentation — Wikipedia](https://en.wikipedia.org/wiki/Memory_segmentation)
- [Address space layout randomization — Wikipedia](https://en.wikipedia.org/wiki/Address_space_layout_randomization)
- [Kernel page-table isolation — Wikipedia](https://en.wikipedia.org/wiki/Kernel_page-table_isolation)
