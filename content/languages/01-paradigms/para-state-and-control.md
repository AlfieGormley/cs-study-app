---
id: para-state-and-control
title: State and explicit control
level: basic
minutes: 3
sourceLesson: para-imperative-declarative
summary: Imperative code exposes state-changing steps.
---

A **programming paradigm** is a style of organising programs: what the basic building blocks are and how you combine them. It is not the same thing as a language. Most languages support several paradigms, and the same problem can be written in very different styles in one language.

The most fundamental split is between **imperative** and **declarative** programming.

- **Imperative**: you give the computer a sequence of commands that change its state, step by step. You describe *how*.
- **Declarative**: you describe the result you want, and something else works out the steps. You describe *what*.

> [!example] Two ways to get a coffee
> Imperative: "Walk to the counter, take a cup, put it under the spout, press the button, wait 30 seconds, add 20 ml of milk."
> Declarative: "A flat white, please." The barista decides the steps, and may do them in a better order than you would.

## Imperative programming

Imperative programming mirrors how the hardware works. The architectural view of a CPU exposes instructions operating on registers and memory. Modern processors can overlap and reorder execution internally while preserving the required observable behavior. The stored-program **von Neumann** model is a useful historical connection, rather than a complete description of every modern microarchitecture. Assembly language makes explicit instructions particularly visible.

The core ingredients are:

- State: variables whose values change over time.
- **Assignment**: `x = x + 1` is a command, not an equation.
- Sequence: statement two runs after statement one, and order matters.
- **Control flow**: `if`, loops and jumps decide which statement runs next.

**Procedural programming** (C, Pascal, early Python scripts) is imperative code organised into procedures. **Structured programming**, pushed by Edsger Dijkstra's 1968 letter *Go To Statement Considered Harmful*, restricts control flow to sequence, selection (`if`) and iteration (loops). The Böhm–Jacopini theorem (1966) showed that flowchart computations can be represented with those control structures, allowing additional state variables. This is an expressiveness result, not a promise that every rewrite is equally clear or fast.

Here is an imperative solution to a small task: *sum the squares of the even numbers in a list*.

```python
# Keep only evens; add each square.
nums = [3, 4, 7, 10, 1]
total = 0
for n in nums:
    if n % 2 == 0:
        total = total + n * n
print(total)   # 16 + 100 = 116
```

To understand it you mentally run it: `total` starts at 0, becomes 16, then 116. The program's meaning lives in the changing state.

## Key takeaways
- Imperative code exposes state-changing steps.
- Structured control flow can replace arbitrary jumps.

## Further reading
- [Dijkstra: Go To Statement Considered Harmful](https://www.cs.utexas.edu/~EWD/transcriptions/EWD02xx/EWD215.html)
- [Böhm and Jacopini: structured control flow](https://www.cs.unibo.it/~martini/PP/bohm-jac.pdf)
