---
id: esc-buttons-debounce
title: Debounce a button without stopping the loop
level: basic
minutes: 4
summary: Accept a new input state after repeated matching samples and report one stable transition.
---

A mechanical switch can make and break contact several times during a press or release. Software that treats every raw transition as an action may report several presses. **Debouncing** separates an unstable raw input from the stable state the application is allowed to use.

## State that survives each call

This example requires three consecutive matching samples. It is a teaching policy, not a claim that every real switch settles after three samples. A `struct` groups related fields. The `typedef` declaration gives the grouped type the name `Debounce`. A pointer to that structure lets the update function modify the same state on successive calls; `d->seen` accesses a field through that pointer.

This is a complete C11 host model. The update runs in one foreground context, takes bounded work per sample, and does not sleep:

```c
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>

typedef struct {
    bool candidate, stable;
    unsigned seen;
} Debounce;

bool update(Debounce *d, bool raw) {
    if (raw != d->candidate) {
        d->candidate = raw;
        d->seen = 1u;
    } else if (d->seen < 3u) {
        d->seen++;
    }
    if (d->seen == 3u &&
        d->stable != d->candidate) {
        d->stable = d->candidate;
        return true; // stable change
    }
    return false;
}

int main(void) {
    Debounce d = {false, false, 0u};
    bool raw[] = {false, true, false,
                  true, true, true};
    for (size_t i = 0; i < 6u; ++i) {
        if (update(&d, raw[i]))
            printf("%u\n", (unsigned)i);
    }
    return 0;
}
```

It prints `5`, the zero-based sample index at which the stable state changes to true. Here the raw values already represent "pressed", after active-low interpretation. The first attempted true run is interrupted by a false sample. The final three true samples form one accepted change. Further true samples produce no additional stable-change notification.

> [!analogy] Real-world analogy: waiting for a repeated answer
> When a noisy announcement keeps changing, you can wait for the same answer several times before acting on it.
>
> **How it maps:** The candidate records the latest possible answer, the count records consecutive agreement and the stable state is the accepted result. Reporting only a stable change avoids repeating the same action every sample.
>
> **Where it stops:** Agreement at sample instants does not prove the contact stayed steady between them. A real debounce interval must suit the switch, sampling schedule and how quickly the application must react.

## Sampling schedule is part of the policy

Three matching samples span two gaps between sample instants. Taking the same number of samples faster shortens the observed interval; taking them irregularly means the count no longer represents a fixed duration. Neither case proves that the contact stayed steady between samples.

The later timing module schedules calls using a timer. Do not poll this function as fast as the CPU allows and then treat its count as milliseconds. Measure the actual switch behaviour and choose a stable-time requirement. If the application wants only presses, additionally require that the new stable state is true; a release is also a stable change.

## Key takeaways
- Keep raw input, candidate state and accepted state distinct.
- Consecutive sample counts need an explicit sampling schedule.
- Emit an action on the desired stable transition rather than on every matching sample.

## Further reading
- [C11 draft: structures, pointers and iteration](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Microchip AN2805: how contact bounce creates multiple triggers](https://onlinedocs.microchip.com/oxy/GUID-7FD12F93-9B28-4EF0-B36F-3A147484BEA1-en-US-3/GUID-5B5C8194-1C66-43F0-A557-ADC76635525B.html)
