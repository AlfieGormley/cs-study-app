---
id: compu-effective-models
title: Effective computation and Church numerals
level: intermediate
minutes: 4
summary: The Church–Turing thesis relates an informal effective procedure to a formal machine.
sourceLesson: compu-church-turing
---

In 1936, two people independently answered the question "what does it mean for a function to be computable?" Alonzo Church used the **λ-calculus**, a system of anonymous functions. Alan Turing used his machines. Within a year, Turing proved the two definitions pick out exactly the same functions. Gödel and Herbrand's general recursive functions and Post's systems turned out to be equivalent too (Kleene proved the λ-calculus and general recursive functions equal).

Four different-looking definitions, one answer. That convergence is the foundation of computer science.

## The thesis

> [!note] The Church–Turing thesis
> Every function that can be computed by an *effective procedure* (a finite, mechanical, step-by-step method that a careful clerk could follow without insight) can be computed by a Turing machine.

It is called a **thesis**, not a theorem, because "effective procedure" is an informal idea. You cannot prove that an informal notion equals a formal one. You can only gather evidence. The evidence is overwhelming:

- **Standard models of effective computation agree.** λ-calculus, μ-recursive functions, register machines (random-access machines), two-counter Minsky machines, Post tag systems, Conway's Game of Life and the one-dimensional cellular automaton Rule 110 have universal variants or encodings. Rule 110 universality uses suitable repeating backgrounds; these results concern idealised unbounded resources. Oracle machines and proposed hypercomputers are different models, not counterexamples established as effective procedures.
- **General-purpose languages with suitable operations** can simulate a TM under unbounded-resource idealisation. Loops plus memory alone are not a proof: a PDA can loop and has an unbounded stack, but its restricted memory access limits its power.
- **Nobody has found a counterexample**: a function that is clearly computable by some mechanical method but not by any TM.

The thesis is what makes the theorems of this module matter. "No TM decides the halting problem" becomes "no effective procedure decides the halting problem for all programs and inputs in the unbounded model". Fixed finite hardware needs the separate qualification below.

## The λ-calculus in Python

Church's model has only three things: variables, function definition (λx. body, "the function that takes x and returns body") and function application. No numbers, no loops. Numbers can be encoded as functions: the **Church numeral** for n means "apply f n times".

```formula reference
c_0 = λf. λx. x
c_2 = λf. λx. f(f(x))
succ = λn. λf. λx. f(n(f)(x))
c_2(g)(0) = g(g(0)) = 2   with g(k) = k + 1
where
λ: lambda: λx. … defines an anonymous function whose input is called x and whose result is the expression after the dot
f: the function to be applied repeatedly
x: the starting value f is applied to
c_0, c_2: the Church numerals for 0 and 2: "apply f zero times" and "apply f twice"
succ: the successor function: turns the numeral for n into the numeral for n + 1 by applying f once more
n: a Church numeral (itself a function)
n(f)(x): apply n to f, then apply the result to x: "apply f n times to x"
g: an ordinary function that adds 1, used to decode a numeral back into a number
k: the input to g
In words: a number is represented by the act of doing something that many times; feeding it "add 1" and 0 turns it back into an ordinary number.
```

The Python below makes that behavioural encoding concrete. `zero` leaves its starting value alone; `succ` applies the supplied function once more. Addition performs one numeral's repetitions and then the other's. Multiplication repeats a repetition. `to_int` supplies “add one” and starts at zero to decode the result.

```python
zero = lambda f: lambda x: x
succ = lambda n: lambda f: lambda x: \
    f(n(f)(x))
# Compose repeated applications to add.
add = lambda m: lambda n: \
    lambda f: lambda x: m(f)(n(f)(x))
# Apply the n-fold function m times.
mul = lambda m: lambda n: \
    lambda f: m(n(f))

def to_int(n):          # decode for humans
    return n(lambda k: k + 1)(0)

two = succ(succ(zero))
three = succ(two)
print(to_int(add(two)(three)))  # 5
print(to_int(mul(two)(three)))  # 6
```

In the untyped λ-calculus, a **fixed-point combinator**, such as Y, supplies recursion without a function name. Evaluation strategy matters: a direct Y translation diverges under Python's eager evaluation; an eager-language version needs delayed evaluation, for example a Z combinator. The arithmetic examples above need neither. It survives as the theoretical core of Haskell, OCaml and Lisp, and every `lambda` in Python is a descendant.

## Key takeaways

- The Church–Turing thesis relates an informal effective procedure to a formal machine.
- Equivalence of specified formal models is proved; the thesis itself is not such a theorem.
- Church numerals encode a natural number by repeated function application.

## Further reading

- [The Church–Turing thesis — Stanford Encyclopedia](https://plato.stanford.edu/entries/church-turing/)
- [Cornell: Church numerals and lambda calculus](https://www.cs.cornell.edu/courses/cs312/2008sp/recitations/rec26.html)
