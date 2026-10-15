---
id: compu-universal-construction
title: Constructing a universal imperative simulator
level: intermediate
minutes: 3
summary: A writable unbounded tape, movable head, finite transition control and unrestricted repetition suffice.
sourceLesson: compu-church-turing
---

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
            # Match both loop ends.
            jump[i], jump[j] = j, i
    if stack:
        raise ValueError("extra [")
    if "," in code:
        raise ValueError("input omitted")
    # This loop has no termination
    # guarantee.
    while pc < len(code):
        c = code[pc]
        if c in "><":
            p += 1 if c == ">" else -1
            if not 0 <= p < len(tape):
                raise IndexError("bounds")
        # Byte arithmetic wraps at 256.
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

## Key takeaways

- A writable unbounded tape, movable head, finite transition control and unrestricted repetition suffice.
- Loops and some storage alone do not establish universality.
- The bounded Brainfuck interpreter prints A for the displayed program and deliberately rejects input instructions.

## Further reading

- [Sipser: TM variants and the Church–Turing thesis](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec6-1/)
