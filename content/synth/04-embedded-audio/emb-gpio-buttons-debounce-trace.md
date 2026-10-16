---
id: emb-gpio-buttons-debounce-trace
sourceLesson: emb-gpio-buttons
title: "Compare debouncers on one trace"
level: basic
minutes: 3
summary: "The same raw trace can produce different debounce delays with the same final edges."
---

These four debouncers receive one already-inverted reading each millisecond: 1 means pressed. The helper `edges` reports sample indices at which a resulting state changes.

## Comparing them on one bouncy trace

This Python simulation feeds the same 35 ms trace (1 sample per ms, 1 = pressed) to each algorithm and prints the times of the debounced edges.

```python
# One sample per ms; 1 means pressed.
raw = [0,0,1,0,1,1,0,1,1,1,1,1,1,1,1,
       1,1,1,1,1,0,1,0,0,1,0,0,0,0,0,
       0,0,0,0,0]

def edges(seq):
    return [t for t in range(1, len(seq))
            if seq[t] != seq[t - 1]]

# First edge wins; ignore subsequent noise.
def lockout(xs, hold):
    out, state, until = [], 0, 0
    for t, s in enumerate(xs):
        if t >= until and s != state:
            state, until = s, t + hold
        out.append(state)
    return out

# A return to the held state resets count.
def stable_for(xs, n):
    out, state, count = [], 0, 0
    for s in xs:
        if s != state:
            count += 1
        else:
            count = 0
        if count >= n:
            state, count = s, 0
        out.append(state)
    return out

# Opposite readings reduce accumulated
# votes.
def integrator(xs, top):
    out, acc, state = [], 0, 0
    for s in xs:
        acc = min(acc + 1, top) if s \
            else max(acc - 1, 0)
        if acc == top:
            state = 1
        elif acc == 0:
            state = 0
        out.append(state)
    return out

# Preserve the most recent eight readings.
def shift_edges(xs):
    reg, found = 0, []
    for t, s in enumerate(xs):
        reg = ((reg << 1) | s) & 0xFF
        if reg == 0x7F:
            found.append(("press", t))
        if reg == 0x80:
            found.append(("release", t))
    return found

# Report transitions, not held-state
# duration.
print("raw edges:", len(edges(raw)))
print("stable5:", edges(stable_for(raw, 5)))
print("integ4:", edges(integrator(raw, 4)))
print("shift:", shift_edges(raw))
print("lockout10:", edges(lockout(raw, 10)))
```

Output:

```output
raw edges: 10
stable5: [11, 29]
integ4: [9, 27]
shift: [('press', 13), ('release', 31)]
lockout10: [2, 20]
```

Ten raw transitions become exactly one press and one release with every method. The difference is latency: lockout responds at 2 ms (on the very first bounce), the integrator debouncer at 9 ms, stable-for-5 at 11 ms, the shift register at 13 ms. Lockout is fastest because it trusts the first edge, which is also why a glitch can fool it.

The windows here (4–10 ms) are short so the trace fits on screen. On real hardware, start nearer Ganssle's 20 ms and adjust after testing your actual switches.

### Hardware debouncing

An RC filter (resistor plus capacitor) followed by a Schmitt-trigger input smooths bounce in hardware. Ganssle's second article walks through the maths. On an MCU with spare cycles, software debouncing is cheaper and adjustable, so it is the usual first choice.

## Key takeaways
- The same raw trace can produce different debounce delays with the same final edges.
- A finite simulation checks this trace; test real switches and noise before choosing a window.

## Further reading
- [A Guide to Debouncing, part 1 — Jack Ganssle](https://www.ganssle.com/debouncing.htm)
- [A Guide to Debouncing, part 2 — Jack Ganssle](https://www.ganssle.com/debouncing-pt2.htm)
- [Teensy 4.1 digital pins and limits — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Bounce library — PJRC](https://www.pjrc.com/teensy/td_libs_Bounce.html)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Pull-up resistor — Wikipedia](https://en.wikipedia.org/wiki/Pull-up_resistor)
- [Teensy 4 core: pinMode pad settings (digital.c) — PJRC](https://github.com/PaulStoffregen/cores/blob/master/teensy4/digital.c)
