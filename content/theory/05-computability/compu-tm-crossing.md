---
id: compu-tm-crossing
title: Crossing off three equal blocks
level: intermediate
minutes: 3
summary: A TM can decide equal a, b and c blocks by marking one symbol from each block per pass.
sourceLesson: compu-turing-machines
---

## Example 2: aⁿbⁿcⁿ, beyond any PDA

The earlier CFL pumping proof established aⁿbⁿcⁿ is not context-free. A TM decides it easily by **crossing off**: on each pass, mark one a as X, one b as Y and one c as Z, then return to the left.

```
q0: a→X R q1 | Y→R q4 | _→accept
q1: skip a,Y right; b→Y R q2
q2: skip b,Z right; c→Z L q3
q3: skip a,b,Y,Z left; X→R q0
q4: skip Y,Z right; _→accept
anything else: reject
```

Trace on `aabbcc` (one pass shown):

```
aabbcc → Xabbcc → XaYbcc
→ XaYbZc  then back left to X
→ XXYYZc → XXYYZZ
q0 sees Y → q4 checks only Y,Z
→ blank: accept
```

Reuse the `run` simulator from the binary-increment unit; its implicit-rejection convention is used for every omitted rule.

```python
# One pass pairs an a, a b and a c.
ABC = {
 ("q0","a"):("X","R","q1"),
 ("q0","Y"):("Y","R","q4"),
 ("q0","_"):("_","R","acc"),
 ("q1","a"):("a","R","q1"),
 ("q1","Y"):("Y","R","q1"),
 ("q1","b"):("Y","R","q2"),
 ("q2","b"):("b","R","q2"),
 ("q2","Z"):("Z","R","q2"),
 ("q2","c"):("Z","L","q3"),
 ("q3","X"):("X","R","q0"),
 ("q4","Y"):("Y","R","q4"),
 ("q4","Z"):("Z","R","q4"),
 ("q4","_"):("_","R","acc"),
}
for sym in "abYZ":     # q3 sweeps left
    ABC[("q3", sym)] = (sym, "L", "q3")

for w in ["abc", "aabbcc", "aabbc",
          "abcabc", "aaabbbccc"]:
    r = run(ABC, w, "q0", {"acc"})
    print(w, r[0], r[1])
# abc acc 8
# aabbcc acc 23
# aabbc reject 13
# abcabc reject 7
# aaabbbccc acc 46
```

Each pass walks across the string and back, and there is one pass per a:

```formula
T(n) ≈ n(cn)
T(n) = O(n^2)
T(1) = 8    T(2) = 23    T(3) = 46
where
T(n): the number of steps the machine takes on the input a^n b^n c^n
n: the number of a's (the input has 3 × n symbols)
c: a fixed constant: each pass walks a distance proportional to n, there and back, so the cost of one pass is about c × n steps
≈: is approximately
O(…): big-O: grows no faster than the expression inside, up to a constant factor, for large n
In words: n passes of about n steps each make the running time grow with the square of n.
```

The measured counts are consistent with the scan analysis: increasing the block length from one to two adds 15 steps, and from two to three adds 23. Three measurements alone cannot establish an asymptotic bound; the pass-by-pass argument supplies that bound. Doubling n roughly quadruples the time for large n. A two-tape TM could do it in O(n): copy the a's to tape 2, then match them against the b's and c's.

## Key takeaways

- A TM can decide equal a, b and c blocks by marking one symbol from each block per pass.
- Order checks reject malformed blocks.
- Repeated full scans give quadratic time for this one-tape construction; two tapes permit a linear-time strategy.

## Further reading

- [Sipser: CFL pumping lemma and Turing machines](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec5-1/)
