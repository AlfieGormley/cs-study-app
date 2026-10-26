---
id: df-iir-feedback
title: A smoother that remembers its output
level: intermediate
minutes: 4
summary: Trace a one-pole feedback smoother and distinguish stored state from an FIR's finite history.
---

**Feedforward paths** use present or previous inputs. **Feedback paths** use previous outputs. With feedback, an input's influence can be passed forward repeatedly rather than ending after a fixed number of taps. An **infinite impulse response**, or **IIR**, filter can therefore have a theoretically endless impulse-response tail, even when that tail becomes extremely small.

## Mix a new reading with the old result

A **one-pole smoother** keeps one previous output. Each update takes a share of the new reading and a share of that remembered output, with positive shares that add to one. The result becomes the remembered value for the next update. Unlike a moving average's fixed window, an older input fades gradually through repeated updates instead of leaving after a fixed number of samples.

Here the coefficient names follow an explicit convention: the memory weight is on the previous output, and the complementary weight is on the current input. With equal shares, a sudden sustained change makes the output move halfway towards the new level at each update. More weight on the old output means a slower response and longer retention; more on the new input means a faster response and less smoothing.

The optional recurrence records that convention precisely.

```formula reference
y[n] = (1 − a)x[n] + ay[n − 1]
0 < a < 1
where
y: the output sequence, with dimensionless sample values here; its value at index minus one is initially zero
x: the input sequence, with dimensionless sample values
n: the integer sample index, starting at zero
a: the dimensionless memory weight on the previous output; larger values in this range retain history longer
In words: mix the new reading with the previous output using positive weights that add to one; a larger share of the old output retains history longer.
```

With equal shares, the output approaches a sustained new level but does not reach it in a finite number of updates in exact arithmetic. This is different from a three-sample moving average, whose window eventually contains only the new level. Choose between them by considering both noise reduction and how promptly useful changes must be seen.

After an isolated pulse, equal shares make the remaining output halve at each zero input. The decreasing tail explains the IIR name. A real computer eventually rounds very small changes away or encounters its representation limits; “infinite” describes the mathematical response, not an infinite array stored in memory.

> [!analogy] Real-world analogy: a slowly updated estimate
> A person revises an estimate halfway towards each new observation rather than replacing it immediately.
>
> **How it maps:** The old estimate maps to the previous output; the new observation maps to the current input. Repeated partial updates retain past information with decreasing influence.
>
> **Where it stops:** A person may change their judgement rules. This filter uses fixed numerical weights, and its state is exactly specified.

## Check the convention before implementing

The previous output is the whole persistent state for this particular implementation. Resetting it at each input destroys the feedback history. Initialising it differently changes startup behaviour, so state must be part of the specification.

SciPy's `lfilter` uses denominator coefficients with a subtraction convention. This same smoother is represented by numerator `[0.5]` and denominator `[1.0, -0.5]`. Copying a positive memory weight into the denominator without changing its sign gives a different filter. Other authors may call the current-input weight “alpha”; compare the recurrence, not just the name.

This smoother needs little state, but its phase delay generally varies with frequency. Choosing IIR over a symmetric FIR changes more than coefficient count. Stability and numerical precision need separate attention next.

## Key takeaways
- Feedback reuses earlier outputs; a decaying influence can continue indefinitely.
- Name which weight multiplies which value before comparing coefficients.
- Resetting the remembered output changes the signal being computed.

## Further reading
- [Julius O. Smith: the one-pole filter](https://www.dsprelated.com/freebooks/filters/One_Pole.html)
- [SciPy: lfilter coefficient and state conventions](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lfilter.html)
