---
id: df-iir-feedback
title: A smoother that remembers its output
level: intermediate
minutes: 4
summary: Trace a one-pole feedback smoother and distinguish stored state from an FIR's finite history.
---

**Feedforward paths** use present or previous inputs. **Feedback paths** use previous outputs. With feedback, an input's influence can be passed forward repeatedly rather than ending after a fixed number of taps. An **infinite impulse response**, or **IIR**, filter can therefore have a theoretically endless impulse-response tail, even when that tail becomes extremely small.

## Mix a new reading with the old result

A **one-pole smoother** keeps one previous output. Here the coefficient names follow an explicit convention: the memory weight is on the previous output, and the complementary weight is on the current input.

```formula
y[n] = (1 − a)x[n] + ay[n − 1]
0 < a < 1
where
y: the output sequence, with dimensionless sample values here; its value at index minus one is initially zero
x: the input sequence, with dimensionless sample values
n: the integer sample index, starting at zero
a: the dimensionless memory weight on the previous output; larger values in this range retain history longer
In words: take part of the new reading and part of the previous output, with weights that add to one.
```

With a memory weight of 0.5, a step from zero to 1 produces 0.5, 0.75, 0.875 and 0.9375. Each output closes half the remaining gap. It approaches 1 but does not reach it in a finite number of steps in exact arithmetic. A memory weight of 0.9 responds more slowly than 0.5; its first output is only 0.1 from zero state.

For an isolated unit impulse and memory weight 0.5, the outputs are 0.5, 0.25, 0.125 and so on. The decreasing tail explains the IIR name. A real computer eventually rounds very small changes away or encounters its representation limits; “infinite” describes the mathematical response, not an infinite array stored in memory.

> [!analogy] Real-world analogy: a slowly updated estimate
> A person revises an estimate halfway towards each new observation rather than replacing it immediately.
>
> **How it maps:** The old estimate maps to the previous output; the new observation maps to the current input. Repeated partial updates retain past information with decreasing influence.
>
> **Where it stops:** A person may change their judgement rules. This filter uses fixed numerical weights, and its state is exactly specified.

## Implement the remembered value

Complete Python example: `state` holds the previous output and is updated after every input. This is the whole persistent state for this particular implementation.

```python
x = [1.0, 1.0, 1.0, 1.0]
a = 0.5
state = 0.0
y = []
for sample in x:
    state = (1-a)*sample + a*state
    y.append(state)
print(y)
# [0.5, 0.75, 0.875, 0.9375]
```

SciPy's `lfilter` uses denominator coefficients with a subtraction convention. This same smoother is represented by numerator `[0.5]` and denominator `[1.0, -0.5]`. Copying a positive memory weight into the denominator without changing its sign gives a different filter. Other authors may call the current-input weight “alpha”; compare the recurrence, not just the name.

This smoother needs little state, but its phase delay generally varies with frequency. Choosing IIR over a symmetric FIR changes more than coefficient count. Stability and numerical precision need separate attention next.

## Key takeaways
- Feedback reuses earlier outputs; a decaying influence can continue indefinitely.
- Name which weight multiplies which value before comparing coefficients.
- Resetting the remembered output changes the signal being computed.

## Further reading
- [Julius O. Smith: the one-pole filter](https://www.dsprelated.com/freebooks/filters/One_Pole.html)
- [SciPy: lfilter coefficient and state conventions](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lfilter.html)
