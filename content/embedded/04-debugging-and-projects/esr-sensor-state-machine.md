---
id: esr-sensor-state-machine
title: Build a small sensor and indicator model
level: intermediate
minutes: 5
summary: Run a complete C model that validates samples, indicates a threshold and latches faults.
---

Now connect the pieces into a small project: accept a sensor result, validate it and choose an indicator state. The hardware adapter will supply events; the application rules will remain testable on a computer.

## Write the contract before the code

Use the fictional whole-number sensor from the previous testing lesson: valid values are 0 to 100 inclusive, and the alert threshold is 70. A SAMPLE event carries a decoded value. TIMEOUT means the acquisition did not finish within its chosen bound; FAILED means the driver reported an acquisition error. RESET is an explicit application recovery event; it is not an automatic C restart or a promise about a physical reset pin.

| Current state or event | Result |
|---|---|
| Reset event | WAITING for fresh data |
| Already FAULT, without reset | Remain FAULT |
| Timeout, failed read or invalid sample | Latch FAULT |
| Valid sample below 70 | NORMAL |
| Valid sample at least 70 | ALERT |

WAITING, NORMAL, ALERT and FAULT are application states, not electrical pin values. The later adapter must map each state to the chosen onboard indicator and reported status. It must not map missing data to a normal measurement.

## Run the complete host model

An `enum` gives names to alternatives. `enum mode` is a type; `current` and `event` are function inputs. The conditional expression `condition ? first : second` selects one result. Each call below performs only bounded comparisons and returns a state; it never waits for hardware.

```c
#include <assert.h>
#include <stdio.h>

enum mode { WAITING, NORMAL, ALERT, FAULT };
enum event { SAMPLE, TIMEOUT,
             FAILED, RESET };

static enum mode step(enum mode current,
                      enum event event,
                      int value) {
    /* Reset is the only fault-clearing
       event in this project. */
    if (event == RESET) return WAITING;
    if (current == FAULT) return FAULT;
    if (event == TIMEOUT || event == FAILED)
        return FAULT;
    if (event != SAMPLE) return FAULT;
    /* This project's fictional sensor
       reports integer values 0 to 100. */
    if (value < 0 || value > 100)
        return FAULT;
    return value >= 70 ? ALERT : NORMAL;
}

int main(void) {
    enum mode state = WAITING;
    state = step(state, SAMPLE, 50);
    assert(state == NORMAL);
    state = step(state, SAMPLE, 70);
    assert(state == ALERT);
    state = step(state, SAMPLE, 101);
    assert(state == FAULT);
    state = step(state, SAMPLE, 20);
    assert(state == FAULT);
    state = step(state, RESET, 0);
    assert(state == WAITING);
    state = step(state, TIMEOUT, 0);
    assert(state == FAULT);
    state = step(state, RESET, 0);
    assert(state == WAITING);
    state = step(state, SAMPLE, 0);
    assert(state == NORMAL);
    state = step(state, FAILED, 0);
    assert(state == FAULT);
    state = step(state, RESET, 0);
    assert(state == WAITING);
    state = step(state, SAMPLE, 100);
    assert(state == ALERT);
    puts("project checks passed");
    return 0;
}
```

With assertions enabled, it prints `project checks passed`. The test shows that a valid sample cannot silently clear a latched fault; explicit recovery returns to WAITING. Boundary values and a timeout are part of the normal test plan.

> [!analogy] Real-world analogy: a parcel inspection station
> A station waits for a parcel, inspects its label and selects a normal, alert or fault indicator. A fault remains recorded until an operator performs the defined reset action.
>
> **How it maps:** The event is an arriving result, validation checks the allowed input contract, and the resulting state selects the application's indication. Explicit recovery prevents a later arrival from silently erasing a fault.
>
> **Where it stops:** These states are software policy. The model does not validate a real sensor's electrical interface, measurement accuracy or timing, and it is not a safety-certified controller.

## Keep acquisition outside the model

A board adapter starts a read at the chosen sampling interval, bounds its wait using a deadline, and produces SAMPLE, TIMEOUT or FAILED as appropriate. The state function also rejects out-of-range decoded samples. The adapter applies the returned state to a documented onboard indicator and exposes the fault through status output.

This host model deliberately simulates those events. It is a complete executable model of the application rules, not complete firmware for an unspecified board. Its rules can be reused after adding and checking an adapter for a particular board and sensor.

## Key takeaways
- State the input range, threshold, timeout and recovery policy explicitly.
- Test invalid inputs and fault latching as well as normal readings.
- Keep device acquisition and output mapping outside the deterministic state function.

## Further reading
- [C11 draft: enum, selection statements and assertions](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Official Pico I2C timeout API contracts](https://raw.githubusercontent.com/raspberrypi/pico-sdk/master/src/rp2_common/hardware_i2c/include/hardware/i2c.h)
