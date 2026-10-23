---
id: esr-project-workflow
title: Take the first project from tests to a board
level: basic
minutes: 4
summary: Use concrete acceptance cases and a documented board adapter to complete the learning project.
---

Finish the sensor-and-indicator project in two stages: first make its application rules repeatable on a computer, then check a specific board adapter. Keep a record of the source revision, build settings, board identity and expected observations so a later change can be compared with the same baseline.

## Run the portable program first

Save the complete program from the preceding lesson as `project.c`. With a C11-capable compiler supporting these warning options, this command builds the host test. The backslash continues the shell command onto the next line; `-o` names its output file.

```sh
cc -std=c11 -Wall -Wextra -Werror \
  project.c -o project
./project
```

Expect `project checks passed`. Keep assertions enabled for this test build. A warning-free compilation and passing examples are useful evidence, not proof of every input or of target timing. Add more cases before changing the project rules.

| Acceptance case | Expected application result |
|---|---|
| Fresh valid 50 | NORMAL |
| Fresh valid 70 | ALERT |
| Invalid 101 | FAULT |
| Valid 20 after a latched fault | Still FAULT |
| Explicit recovery | WAITING |
| Acquisition timeout | FAULT |

## Add a board adapter deliberately

Choose an existing supported low-voltage development board and use its official setup and example for the exact variant. Confirm the board's schematic, SDK pin functions, power method and signal limits before connecting a sensor. Start with its onboard indicator; do not connect motors, relays, mains or other loads directly to MCU pins.

The following is integration pseudocode, not a universal SDK or a second runnable program:

```text
if a sample is due and no read is active:
    start the device read with a deadline
if a read is active:
    if completion or deadline is observed:
        choose one outcome using the
        documented driver/deadline rule
        deliver SAMPLE, FAILED or TIMEOUT
        end that attempt exactly once
apply the returned indicator/status state
continue the other bounded loop work
```

Give an attempt one terminal outcome. If completion and deadline are both observed in one pass, use a documented rule based on the driver's result and timing contract; do not dispatch a successful sample and then a stale timeout for the same attempt. A failed read must not retry forever and prevent the cooperative loop from continuing.

## Observe and recover

Flash using the official workflow for that board and inspect the expected startup state. Exercise valid readings, threshold neighbours, invalid results and a deliberately controlled timeout. Use a host fake for faults that cannot be injected safely or reliably on the board. Check the expected indicator/status path and return to a known state after each case.

> [!analogy] Real-world analogy: a rehearsal followed by a venue check
> Rehearsal checks the sequence of actions; a venue check confirms that the real equipment and controls work together.
>
> **How it maps:** Host tests check repeatable application logic, while board checks establish the chosen adapter's actual behaviour under the tested conditions.
>
> **Where it stops:** A successful demonstration covers only the exercised inputs and conditions. It does not establish production reliability, all timing bounds or suitability for a safety-critical use.

Keep a recovery path: the official flash or debug connection, a known-good image and a record of reset causes. Once the baseline is repeatable, change one requirement at a time and rerun the same acceptance cases. More advanced bootloaders, updates and power characterisation belong after this introductory project.

## Key takeaways
- Make the host acceptance cases pass before adding physical integration.
- Bind each acquisition attempt to one valid result or explicit failure outcome.
- Keep a documented flash, observation and recovery workflow for the actual board.

## Further reading
- [GCC warning options and their limits](https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html)
- [Official Pico SDK board configuration and build workflow](https://raw.githubusercontent.com/raspberrypi/pico-sdk/master/README.md)
- [Official Pico examples](https://github.com/raspberrypi/pico-examples)
