---
id: est-isr-sharing
title: Share events with an interrupt safely
level: intermediate
minutes: 5
summary: Protect a read-and-clear operation under explicit single-core interrupt assumptions.
---

An ISR can update a value between two instructions in the main loop. Correctness depends on the whole operation being performed, not just whether each individual access fits in one machine instruction.

## Volatile is one part of the contract

A **volatile** access tells the compiler that the access has observable behaviour according to its implementation's rules. It is commonly part of an SDK's contract for hardware registers and interrupt-shared state. It does not make a multi-step update indivisible, synchronise ordinary threads, or order unrelated memory as a memory barrier would.

A flag answers a yes/no question such as “has work arrived?”. Setting it three times before the foreground reads it still leaves one true flag. If every event matters, use a suitable counter or bounded queue and an explicit overflow policy; hardware may already merge events before the ISR runs.

## How a read-and-clear loses an event

Suppose a counter contains three. The main loop copies three into a local variable. An ISR increments the shared counter to four. The main loop then clears it to zero. It processes three events and forgets the fourth. Declaring the counter volatile does not prevent this sequence.

A short **critical section** can exclude the specific ISR during the copy-and-clear. This is a Pico SDK fragment illustrating a single-core execution design on RP2040, not a portable host program. Include the SDK headers, install and acknowledge the device-specific handler separately, and assume no other core, DMA engine or non-maskable handler accesses this counter. Assume it cannot overflow between drains.

```c
#include <stdint.h>
#include "hardware/sync.h"

static volatile uint32_t pending;

void on_event(void) {
    /* Device acknowledgement omitted. */
    ++pending;
}

uint32_t take_events(void) {
    uint32_t state =
        save_and_disable_interrupts();
    uint32_t n = pending;
    pending = 0;
    restore_interrupts(state);
    return n;
}
```

The SDK functions save the previous interrupt state, disable interrupts on the calling core, and later restore that saved state. Do not unconditionally enable interrupts on exit: the caller may already have disabled them. The handler comment is a placeholder for the peripheral's required acknowledgement, not a complete ISR implementation.

> [!analogy] Real-world analogy: collecting order slips
> A clerk briefly closes a collection hatch, takes the accumulated order slips and restores the hatch to its previous state.
>
> **How it maps:** The brief pause represents excluding the relevant interrupt while shared work is taken and cleared. Processing the collected work happens after the pause ends. A hatch that was already closed stays closed, just as a previously disabled interrupt state stays disabled.
>
> **Where it stops:** Masking interrupts on one core does not stop other cores or every hardware actor. A counter also has finite capacity and cannot reconstruct events that the device never retained.

Keep the protected work short; process the copied count afterwards. If the no-overflow assumption cannot be justified, choose and test a policy such as counter saturation with an overflow indicator. Language atomics are another tool, but their availability, lock-free implementation and suitability inside an ISR must be checked for the actual target and SDK.

## Key takeaways
- Volatile does not make read-and-clear indivisible or a flag count events.
- A critical section must exclude every competing actor relevant to its data.
- Restore the previous interrupt state and plan for overflow.

## Further reading
- [GCC: what volatile does and does not guarantee](https://gcc.gnu.org/onlinedocs/gcc/Volatiles.html)
- [Pico SDK interrupt state helpers](https://raw.githubusercontent.com/raspberrypi/pico-sdk/master/src/rp2_common/hardware_sync/include/hardware/sync.h)
- [Pico SDK calling-core interrupt scope](https://raw.githubusercontent.com/raspberrypi/pico-sdk/master/src/rp2_common/hardware_irq/include/hardware/irq.h)
