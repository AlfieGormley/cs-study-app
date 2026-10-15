---
id: par-language-publication
title: Publishing data with language atomics
level: intermediate
minutes: 3
sourceLesson: par-memory-models
summary: A release and an acquire that reads it can publish earlier ordinary data safely.
---

## Language memory models

You rarely write fences in assembly. C11/C++11, Java, Rust and Go define their own memory model, and the compiler emits whatever each CPU needs. The C/C++ model has two big rules:

1. A **data race** (potentially concurrent conflicting actions, at least one non-atomic, with neither happening before the other) is undefined behaviour.
2. **DRF-SC:** programs that use mutexes and seq_cst operations to prevent data races, and no other weaker synchronisation operations, behave as if sequentially consistent.

Weaker orderings trade simplicity for speed:

| Order | Guarantee |
|---|---|
| `relaxed` | Atomicity and per-object coherence; no publication of unrelated data |
| `release` (store) | Earlier accesses stay before it |
| `acquire` (load) | Later accesses stay after it |
| `seq_cst` | Appropriate acquire/release effects plus one order of seq_cst operations |

Here is one-shot message passing in C11. Assume exactly one producer call and one consumer call, objects initialised before the threads start, and no later concurrent modification or reuse of data. The snippet supplies the thread bodies, not thread creation. The release store "publishes" everything written before it; an acquire load that reads the published value "sees" all of it.

```c
#include <stdatomic.h>
#include <stdio.h>

int data;          /* plain variable */
atomic_int ready;  /* the flag */

void producer(void) {
  /* Initialise before publishing ready. */
  data = 42;
  atomic_store_explicit(&ready, 1,
      memory_order_release);
}

void consumer(void) {
  /* Acquire the published flag. */
  while (!atomic_load_explicit(&ready,
             memory_order_acquire))
    ;  /* spin */
  /* Seeing ready publishes data. */
  /* If reached: the value is 42. */
  printf("%d\n", data);
}
```

The printed value is 42 once the consumer observes the publication. This example does not guarantee scheduling fairness or a bound on the spin duration.

Illustrative compiler mappings for naturally aligned, lock-free 32-bit atomics on ordinary memory (compiler, target features and whether the result is used can change them):

| C11 operation | x86-64 | ARMv8 |
|---|---|---|
| load acquire | `mov` | `ldar` / `ldapr` |
| store release | `mov` | `stlr` |
| store seq_cst | `xchg` | `stlr` |
| seq_cst fetch_add, result used | `lock xadd` | `ldaddal` with LSE, or exclusive loop |

For such x86 loads/stores, acquire/release may need no extra hardware instruction beyond MOV, but still constrain compiler transformations and still incur ordinary memory-access costs. A common seq_cst-store mapping uses memory XCHG or MOV followed by MFENCE. AArch64 mappings using STLR followed by LDAR provide stronger ordering than the minimum language release/acquire requirement; this does not make all atomics cheap. LSE atomics require target support; other mappings use exclusive-load/store loops or library helpers.

## Key takeaways
- A release and an acquire that reads it can publish earlier ordinary data safely.
- Compiler mappings depend on target features and are separate from the language contract.

## Further reading
- [Lamport’s original sequential-consistency paper](https://lamport.azurewebsites.net/pubs/multi.pdf)
- [The x86-TSO model](https://www.cl.cam.ac.uk/~pes20/weakmemory/cacm.pdf)
- [The revised Arm multicopy-atomic model](https://www.cl.cam.ac.uk/~pes20/armv8-mca/armv8-mca-draft.pdf)
- [C++ draft: races](https://eel.is/c++draft/intro.races)
- [C++ draft: atomic ordering](https://eel.is/c++draft/atomics.order)
