---
id: logic-kmap-hazards
title: Why minimal logic can glitch
level: intermediate
minutes: 3
sourceLesson: logic-karnaugh-maps
summary: Unequal physical delays can create a static-1 hazard despite Boolean equivalence.
---

## Static-1 hazard: when minimal is too minimal

A minimal circuit can produce a brief false output, a **glitch**, when an input changes. Take this function with B and C both held at 1:

```formula essential
F = A·B + A′·C
where
F: the circuit's output
A, B, C: inputs, each 0 or 1
A′: NOT A, produced by an inverter
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: With the other two inputs high, either the first input or its complement makes the output high. The truth table therefore requires a steady high output when only the first input changes.
```

The  NOT A  signal comes through an inverter, so it changes slightly later than A. When A falls from 1 to 0, unequal path delays can leave a moment when AB has dropped but A'C has not risen:

```
A     --------________________
AB    --------________________
A'    __________--------------
A'C   __________--------------
F     --------__--------------
              ^^
         both terms 0: glitch
```

This is a **static-1 hazard**. On the K-map, it shows up as two groups that touch but do not overlap: m7 (in AB) and m3 (in A'C) are adjacent, yet no single group contains both.

The fix is to add the redundant group that bridges them, the consensus term from Boolean-algebra lessons:

```formula essential
F = A·B + A′·C + B·C
where
F: the circuit's output, now hazard-free for this input change
A, B, C: inputs, each 0 or 1
A′: NOT A
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: the extra term B·C does not change the function (it is the redundant consensus term), but it does not depend on A at all.
```

B AND C stays 1 throughout the transition, holding F up. At ordinary synchronous data inputs, glitches outside setup/hold sampling windows need not affect the captured value when timing constraints are met. They can still increase power. They matter in asynchronous logic, in anything that drives a clock, reset or enable, and for power, since every glitch is a wasted switching event.

## Beyond four variables

K-maps work well up to four variables, are awkward at five or six (two or four stacked maps, with adjacency between layers), and are hopeless beyond. Tools use:

- **Quine–McCluskey**: the same prime-implicant method done in tables. Exact, but the number of primes can grow exponentially with the number of variables.
- **Espresso**: a heuristic two-level minimiser associated with Berkeley. It seeks compact covers without guaranteeing a globally minimal answer.
- **Multi-level synthesis**: real chips are not two-level. Synthesis tools factor logic into many levels and map it onto the gates in a cell library, trading depth for area.

K-maps help explain minimisation and remain handy for small pieces of control logic and for spotting glitches.

## Key takeaways
- Unequal physical delays can create a static-1 hazard despite Boolean equivalence.
- A bridging consensus term protects the illustrated one-input two-level transition.

## Further reading
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/combinational_logic/notes.html)
- [Karnaugh map — Wikipedia](https://en.wikipedia.org/wiki/Karnaugh_map)
- [Quine–McCluskey algorithm — Wikipedia](https://en.wikipedia.org/wiki/Quine%E2%80%93McCluskey_algorithm)
- [Espresso heuristic logic minimizer — Wikipedia](https://en.wikipedia.org/wiki/Espresso_heuristic_logic_minimizer)
- [Hazard (logic) — Wikipedia](https://en.wikipedia.org/wiki/Hazard_(logic))
- [Don't-care term — Wikipedia](https://en.wikipedia.org/wiki/Don%27t-care_term)
- [Gray code — Wikipedia](https://en.wikipedia.org/wiki/Gray_code)
