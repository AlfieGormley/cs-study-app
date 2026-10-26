---
id: rep-overflow-failures
title: Counters and real overflow failures
level: basic
minutes: 3
summary: A finite counter needs an explicit range and rollover policy.
sourceLesson: rep-integers
---

Rollover is a system-design issue when a counter outlives assumptions made by its readers. Incident reports show why range and failure handling belong in the design.

## Design for the boundary

A fixed-width unsigned counter eventually returns to zero. Increasing its width delays that point; using finer time units makes it arrive sooner at the same width. Neither choice removes the need to define how consumers handle rollover.

For a counter using unsigned arithmetic at its specified width, subtracting the saved start value from the current value gives elapsed ticks across one rollover, provided the true elapsed interval is shorter than one complete counter period. A simple numerical comparison with a future deadline can fail when that deadline has wrapped. Longer intervals need additional state or a wider time source.

## Overflow in the real world

- **Ariane 5, 1996.** A conversion of the horizontal-bias alignment result (related to horizontal velocity) from 64-bit floating point to a 16-bit signed integer raised an exception. Both inertial reference systems failed through the same software path; the inquiry identified reuse of assumptions from Ariane 4 and inadequate protection/testing, not just a number being too large.
- **Boeing 787, 2015.** The US FAA warned that a counter in the generator control units would overflow after 248 days powered on without a restart, potentially losing all AC electrical power if the units entered failsafe together. The FAA directive states the counter-overflow interval; it does not specify a 32-bit centisecond representation. That implementation claim is omitted because it could not be verified from the directive.
> [!note] Evidence gap
> The YouTube/Gangnam Style migration anecdote is omitted: the original engineering account of counter type and migration timing was not available for reliable primary-source verification. A hypothetical signed 32-bit view counter still has the demonstrable limit 2,147,483,647.

- **The year 2038 problem.** A signed 32-bit `time_t` counting seconds from 1970 runs out at 03:14:07 UTC on 19 January 2038, and a wrapping interpretation of the next bit pattern corresponds to December 1901. Actual software may fail differently; signed overflow in C is not guaranteed to wrap. Common current 64-bit Unix ABIs use a 64-bit `time_t`, but embedded devices and old file formats remain at risk.

## Key takeaways
- A finite counter needs an explicit range and rollover policy.
- Failure reports establish causes more reliably than a plausible anecdote.

## Further reading
- [C working draft N3220](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf)
- [GCC implementation-defined integers](https://gcc.gnu.org/onlinedocs/gcc/Integers-implementation.html)
- [Two's complement — Wikipedia](https://en.wikipedia.org/wiki/Two%27s_complement)
- [Integer overflow — Wikipedia](https://en.wikipedia.org/wiki/Integer_overflow)
- [Arithmetic operators and overflow — cppreference (C)](https://en.cppreference.com/w/c/language/operator_arithmetic)
- [Standard library header stdckdint.h — cppreference](https://en.cppreference.com/w/c/header/stdckdint)
- [Year 2038 problem — Wikipedia](https://en.wikipedia.org/wiki/Year_2038_problem)
- [Ariane flight V88 — Wikipedia](https://en.wikipedia.org/wiki/Ariane_flight_V88)

- [FAA 2015 Boeing 787 directive](https://www.govinfo.gov/content/pkg/FR-2015-05-01/pdf/2015-10066.pdf)
- [GCC code generation options](https://gcc.gnu.org/onlinedocs/gcc/Code-Gen-Options.html)

- [Ariane 501 inquiry board report (university-hosted copy)](https://www-users.cse.umn.edu/~arnold/disasters/ariane5rep.html)
