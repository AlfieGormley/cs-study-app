---
id: compu-church-turing
title: The Church–Turing thesis
level: intermediate
minutes: 12
summary: Why standard models of effective computation agree with the Turing machine, what Turing completeness really requires, and the universal machine behind every interpreter.
---

In 1936, two people independently answered the question "what does it mean for a function to be computable?" Alonzo Church used the **λ-calculus**, a system of anonymous functions. Alan Turing used his machines. Within a year, Turing proved the two definitions pick out exactly the same functions. Gödel and Herbrand's general recursive functions and Post's systems turned out to be equivalent too (Kleene proved the λ-calculus and recursive functions equal).

Four different-looking definitions, one answer. That convergence is the foundation of computer science.

## The thesis

> [!note] The Church–Turing thesis
> Every function that can be computed by an *effective procedure* (a finite, mechanical, step-by-step method that a careful clerk could follow without insight) can be computed by a Turing machine.

It is called a **thesis**, not a theorem, because "effective procedure" is an informal idea. You cannot prove that an informal notion equals a formal one. You can only gather evidence. The evidence is overwhelming:

- **Standard models of effective computation agree.** λ-calculus, μ-recursive functions, register (RAM) machines, two-counter Minsky machines, Post tag systems, Conway's Game of Life and the one-dimensional cellular automaton Rule 110 have universal variants or encodings. Rule 110 universality uses suitable repeating backgrounds; these results concern idealised unbounded resources. Oracle machines and proposed hypercomputers are different models, not counterexamples established as effective procedures.
- **General-purpose languages with suitable operations** can simulate a TM under unbounded-resource idealisation. Loops plus memory alone are not a proof: a PDA can loop and has an unbounded stack, but its restricted memory access limits its power.
- **Nobody has found a counterexample**: a function that is clearly computable by some mechanical method but not by any TM.

The thesis is what makes the theorems of this module matter. "No TM decides the halting problem" becomes "no effective procedure decides the halting problem for all programs and inputs in the unbounded model". Fixed finite hardware needs the separate qualification below.

## The λ-calculus in Python

Church's model has only three things: variables, function definition (λx. body) and function application. No numbers, no loops. Numbers can be encoded as functions: the **Church numeral** n means "apply f n times".

```python
zero = lambda f: lambda x: x
succ = lambda n: lambda f: lambda x: \
    f(n(f)(x))
add = lambda m: lambda n: \
    lambda f: lambda x: m(f)(n(f)(x))
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

## The universal Turing machine

Turing's most important idea was not the machine but the **universal machine** U. A TM's rules are a finite table, so they can be written as a string, written ⟨M⟩. U takes ⟨M⟩ and an input w on its tape and simulates M on w:

```
U(⟨M⟩, w) = accept  if M accepts w
            reject  if M rejects w
            loops   if M loops on w
```

U is a single fixed machine that can simulate any encoded TM. It demonstrates the programs-as-data idea behind interpreters. The previous lesson's Python simulator illustrates this, with `delta` as the encoded rules, but its step cap makes each call a bounded simulation. CPython and the JVM are practical interpreters with resource limits; a CPU decoder alone is not a universal machine. Universality concerns the whole effective computing system with unbounded storage and execution.

The idea that programs are data has a sharp consequence. A program can take *another program* as input and ask questions about it. Lesson 5 shows that some of those questions have no algorithmic answer.

## What Turing completeness needs

A system is **Turing complete** if it can simulate any TM (given unbounded memory). A sufficient imperative construction is a writable tape that can grow without bound, a movable head, finite control that reads/writes symbols and chooses transitions, and unrestricted repetition. Other models encode these abilities differently: λ-calculus and cellular automata need no explicit `if` instruction. A checklist of memory, branches and loops is not by itself a universality proof.

Brainfuck has eight one-character instructions. With a suitable unbounded tape it can simulate a TM; `[` and `]` supply iteration and the other operations manipulate cells. This intentionally bounded demonstration implements seven instructions and rejects input `,`:

```python
def bf(code):
    tape, p, pc, out = [0] * 30000, 0, 0, []
    jump, stack = {}, []
    for i, c in enumerate(code):
        if c == "[":
            stack.append(i)
        elif c == "]":
            if not stack:
                raise ValueError("extra ]")
            j = stack.pop()
            jump[i], jump[j] = j, i
    if stack:
        raise ValueError("extra [")
    if "," in code:
        raise ValueError("input omitted")
    while pc < len(code):
        c = code[pc]
        if c in "><":
            p += 1 if c == ">" else -1
            if not 0 <= p < len(tape):
                raise IndexError("bounds")
        elif c == "+":
            tape[p] = (tape[p] + 1) % 256
        elif c == "-":
            tape[p] = (tape[p] - 1) % 256
        elif c == ".":
            out.append(chr(tape[p]))
        elif c == "[" and tape[p] == 0:
            pc = jump[pc]
        elif c == "]" and tape[p] != 0:
            pc = jump[pc]
        pc += 1
    return "".join(out)

# 8 * 8 + 1 = 65 = "A"
print(bf("++++++++[>++++++++<-]>+."))  # A
```

(The finite 30,000-cell tape means this interpreter is not Turing complete. A negative pointer is rejected rather than accidentally indexing the end of a Python list. It still permits non-terminating programs such as `+[]`.)

### Accidental Turing completeness

Because the bar is so low, systems keep crossing it by accident:

- **C++ templates** can express universal computation when compiler resource and instantiation-depth limits are idealised away.
- **x86-style `mov` operations**, plus a final unconditional jump back to the start, simulate a TM in Stephen Dolan's 2013 construction. It assumes unbounded addressable memory; a finite straight-line sequence of `mov` instructions alone is not universal.
- **SQL with recursive CTEs and suitable data operations** can encode TM simulation when storage and value sizes are unbounded. PostgreSQL `WITH RECURSIVE` supplies iteration, but the keyword alone is not a proof and a real database has finite resource/type limits.
- **Magic: The Gathering** has a card combination that simulates a universal TM (Churchill, Biderman and Herrick, 2019).
- **Conway's Game of Life** and **Rule 110** have universal constructions with suitable initial configurations and unbounded space. Cook's Rule 110 simulation includes repeating backgrounds extending away from the encoded input.

### Deliberately not Turing complete

Turing completeness has a price: as lesson 6 shows, every non-trivial property of the recognised language is undecidable for arbitrary TMs. This does not make every useful question undecidable. So some designers avoid it on purpose:

| System | Restriction | Benefit |
|---|---|---|
| Formal regular expressions | finite automata | linear input scan for a fixed DFA |
| eBPF in Linux | verifier restricts accepted programs, including loop bounds | termination and safety checks under its model; not a guarantee against implementation bugs |
| Bitcoin Script | no loops | every script terminates |
| Starlark core | no recursion, finite iteration | core evaluation terminates; extensions and external build commands need separate analysis |
| Total fragments of Agda and Rocq; Dhall | termination restrictions | stronger evaluation guarantees; Agda/Rocq also have guarded coinduction and features requiring separate treatment |

Ethereum bounds transaction execution with **gas**. Continuing computation consumes the finite budget; some terminating instructions, including `STOP`, have zero base cost, so it is false that every instruction costs at least one gas. A transaction eventually stops normally, exceptionally or out of gas. This guarantees termination under EVM semantics, not successful completion or a wall-clock deadline. Calling the EVM Turing complete also idealises away its actual resource and fixed-width addressing limits.

## Real computers are finite

A closed deterministic computer with fixed finite RAM, registers, storage and other state has finitely many configurations. External inputs must also be fixed or modelled before state repetition implies a loop. We model it as a TM because its memory is big enough that the finite limit is rarely the interesting constraint, and because the program text does not depend on the memory size. When a program runs out of memory, we treat that as a resource failure, not a change in what the language can express.

## Versions of the thesis

- **The Church–Turing thesis** (above) is about what can be computed *at all*.
- The **physical Church–Turing thesis** claims that any function computable by a *physical* device is TM-computable. Proposed "hypercomputers" (machines that perform infinitely many steps in finite time, or use exact real numbers) appear to require physically unrealistic resources.
- The **extended (strong) Church–Turing thesis** is commonly stated using efficient simulation by a probabilistic classical TM, with only **polynomial** overhead. This one is in doubt. Shor's algorithm factors integers in polynomial time on a quantum computer, and no polynomial-time classical factoring algorithm is known.

Quantum computers do **not** threaten the original thesis. For the standard effective quantum circuit model, a classical computer can approximate amplitudes and outcome probabilities to a specified accuracy, generally using exponential resources. This assumes effectively specified gates; arbitrary exact real-number oracles are not part of that model. Their possible advantage concerns what is computable efficiently, a question for complexity theory; a general BQP-versus-BPP separation is not known.

## Pitfalls

- **"Turing complete" does not mean "useful" or "fast".** Brainfuck and Rule 110 are complete but hopeless for real work. Completeness is about what is possible, not practical.
- **Finite memory systems are not Turing complete in the strict sense.** All storage must be bounded, including the call stack and external storage. Fixed-width integers and no heap allocation alone do not establish this.
- **The thesis is not a theorem.** You can't prove it; you can cite it to justify replacing "algorithm" with "Turing machine" in a proof.

## Key takeaways
- The Church–Turing thesis: anything computable by an effective procedure is computable by a Turing machine. It is a well-supported thesis, not a theorem.
- Standard effective universal models agree on computability, under their appropriate unbounded-resource assumptions.
- The universal TM runs any encoded machine ⟨M⟩: the theoretical basis of interpreters and stored-program computers.
- Prove Turing completeness by simulation; loops and memory alone are not sufficient, and explicit branching syntax is not necessary.
- The extended thesis (polynomial simulation) is challenged by quantum computing; the original thesis is not.

## Further reading
- [The Church–Turing Thesis (Stanford Encyclopedia of Philosophy)](https://plato.stanford.edu/entries/church-turing/)
- [Church–Turing thesis (Wikipedia)](https://en.wikipedia.org/wiki/Church%E2%80%93Turing_thesis)
- [Turing completeness (Wikipedia)](https://en.wikipedia.org/wiki/Turing_completeness)
- [Lambda calculus (Wikipedia)](https://en.wikipedia.org/wiki/Lambda_calculus)
- [Universal Turing machine (Wikipedia)](https://en.wikipedia.org/wiki/Universal_Turing_machine)
- [Total functional programming (Wikipedia)](https://en.wikipedia.org/wiki/Total_functional_programming)

- [Dolan: mov is Turing-complete (construction and assumptions)](https://harrisonwl.github.io/assets/courses/malware/spring2017/papers/mov-is-turing-complete.pdf)
- [Cook: A Concrete View of Rule 110 Computation](https://arxiv.org/abs/0906.3248)
- [Ethereum opcode reference](https://ethereum.org/developers/docs/evm/opcodes/)
