---
id: esr-test-without-board
title: Test decision logic without a board
level: basic
minutes: 4
summary: Separate deterministic decisions from hardware access and test boundary inputs on a computer.
---

A sensor driver has electrical and timing dependencies. The rule deciding whether its decoded value should light an indicator often does not. Put that decision in a small function with explicit inputs and outputs, then test it without a board.

## Give the logic a narrow contract

Our fictional sensor reports whole numbers from 0 to 100. For this learning project, values below 70 mean normal, values from 70 to 100 mean alert, and values outside the range are invalid. These are invented application requirements, not a real sensor's units or accuracy specification.

This complete C11 host program implements that rule. A comparison in C produces integer zero or one; `assert` checks that the expected expression is true and stops a test that fails. Build these tests with assertions enabled, without defining `NDEBUG`. Assertions are test checks here, not the production policy for handling a failed device.

```c
#include <assert.h>
#include <stdio.h>

static int classify(int sample) {
    if (sample < 0 || sample > 100)
        return -1;
    return sample >= 70;
}

int main(void) {
    assert(classify(-1) == -1);
    assert(classify(0) == 0);
    assert(classify(69) == 0);
    assert(classify(70) == 1);
    assert(classify(100) == 1);
    assert(classify(101) == -1);
    puts("logic checks passed");
    return 0;
}
```

It prints `logic checks passed`. The cases on both sides of 70 distinguish “greater than” from “greater than or equal”, while the range endpoints expose an incorrect validity check.

> [!analogy] Real-world analogy: rehearsing with prepared cue cards
> An actor can rehearse responses using prepared cue cards before the rest of the production is ready.
>
> **How it maps:** Controlled readings replace unpredictable live inputs, letting a test repeat the same decision and check its result.
>
> **Where it stops:** Prepared inputs cannot prove that a physical sensor, driver, clock or electrical connection works. Hardware integration still needs its own observations.

## Introduce controlled failures too

Keep acquisition outside this function: the driver returns a decoded sample or an explicit failure. A **fake** supplies chosen results for tests, including an unavailable sample or a timeout. Do not silently substitute an in-range reading for failure; that would make the logic mistake “nothing was read” for “the reading was normal”.

Use host tests for boundary cases and state transitions. Later, compare a known device input with the reported driver result on the real board. Compiling on a computer does not check the target's register access, interrupt behaviour or timing budget. Keep both kinds of evidence.

## Key takeaways
- Make application decisions deterministic and independent of hardware access.
- Test endpoints, threshold neighbours and explicit failures.
- Host tests complement rather than replace hardware integration checks.

## Further reading
- [C11 draft: expressions, assertions and test behaviour](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [GCC warning options](https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html)
