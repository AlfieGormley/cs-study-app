---
id: est-timers-nonblocking
title: Measure elapsed time without blocking
level: intermediate
minutes: 5
summary: Use unsigned elapsed-time subtraction with an explicit counter width and observation bound.
---

A delay that stops the main loop can stop button checks and communication work too. A non-blocking timer instead asks whether enough time has elapsed, performs a small action when due, and lets the loop continue.

## A counter that eventually wraps

Assume an abstract time source supplies a `uint32_t` tick count, advancing once per millisecond. `uint32_t`, when provided by the C implementation, is an unsigned integer type with exactly 32 bits. The code below accepts the tick count as input; it does not configure a hardware timer.

A **wrapping counter** returns to zero after its largest representable value. Comparing `now >= start + interval` is unreliable when the addition wraps. Instead, subtract the saved starting count and convert the result to the counter's unsigned type.

This is valid when the actual elapsed time since the saved marker is less than one whole counter cycle. The counter alone cannot distinguish a short interval from the same interval plus one or more complete cycles. Arrange regular checks so a due timer is handled before that ambiguity arises. This example uses a 10 ms interval, with checks much more frequent than a full 32-bit millisecond cycle.

> [!analogy] Real-world analogy: a mileage display rolling over
> A limited-digit mileage display returns to zero after its highest reading. Two nearby readings can still reveal the distance travelled across that rollover.
>
> **How it maps:** Unsigned subtraction recovers a small elapsed count across one rollover of the displayed number. The saved reading is the timer's starting marker.
>
> **Where it stops:** The readings cannot reveal how many complete display cycles were missed. Firmware must also know the tick duration and how long it can go without observing the timer.

## Run a portable C example

This is a complete C11 host program. `bool` is a true/false type; `>=` compares values; `return` passes the result to the caller. The cast `(uint32_t)` converts the difference back to the counter's unsigned width.

```c
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

static bool due(uint32_t now,
                uint32_t start,
                uint32_t interval) {
    uint32_t elapsed =
        (uint32_t)(now - start);
    return elapsed >= interval;
}

int main(void) {
    uint32_t start = UINT32_MAX - 3u;
    printf("%d\n", due(6u, start, 10u));
    return 0;
}
```

It prints `1`: moving from four counts before zero to count six takes ten ticks. `UINT32_MAX` names the largest value of the type, and `u` marks an unsigned integer literal.

After an action, saving the current time starts a new interval from that observation; a late check shifts the schedule. Advancing a saved deadline by fixed periods is another policy, but then late work needs an explicit catch-up or skip policy. Neither policy makes execution occur at the exact intended instant. Check the time between counter increments and the longest loop delay.

## Key takeaways
- Ask whether time has elapsed instead of stopping the whole loop.
- Unsigned subtraction handles rollover only within a known observation bound.
- Decide whether late work shifts, catches up or skips the schedule.

## Further reading
- [C11 committee draft: unsigned arithmetic and exact-width types](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Raspberry Pi SDK time interfaces](https://raw.githubusercontent.com/raspberrypi/pico-sdk/master/src/common/pico_time/include/pico/time.h)
