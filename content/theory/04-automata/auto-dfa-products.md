---
id: auto-dfa-products
title: Combining DFAs with product states
level: basic
minutes: 4
sourceLesson: auto-dfa
summary: A product state records one state from each component.
---

## Combining DFAs

Languages recognised by DFAs are called **regular languages**. They are closed under the usual operations on sets, and the proofs are constructions you can actually run.

### Complement

To recognise everything a complete DFA rejects, swap accepting and non-accepting states. The DFA for "odd number of 1s" is the earlier parity DFA with O accepting instead of E.

> [!warning] Complete the DFA first
> Swapping only works if the transition function is total. In a partial DFA, strings that "fall off" are rejected both before and after the swap. Add the dead state explicitly, then swap, and the dead state becomes accepting.

### Intersection and union: the product construction

Take two complete DFAs over the same alphabet. To recognise the strings both of them accept, run the two machines **in parallel**. A state of the product machine is a pair: where the first machine is, and where the second machine is. This is the **product construction**:

For intersection, accept only when both component states accept. For union, accept when either does. Both use the same pairs and transitions; changing the final test changes the combined language.

The notation records this construction for reference:

```formula reference
Q = Q₁ × Q₂
δ((p, q), c) = (δ₁(p, c), δ₂(q, c))
q₀ = (q₁, q₂)
F_{∩} = { (p, q) : p ∈ F₁ and q ∈ F₂ }
F_{∪} = { (p, q) : p ∈ F₁ or q ∈ F₂ }
where
Q₁, Q₂: the sets of states of the first machine M₁ and the second machine M₂
Q: the set of states of the product machine
×: the Cartesian product: Q₁ × Q₂ is the set of all pairs (p, q) with p from Q₁ and q from Q₂
p: a state of the first machine
q: a state of the second machine
( , ): an ordered pair: first component from M₁, second from M₂
c: one input symbol
δ₁, δ₂: the transition functions of the two machines
δ: the transition function of the product: it moves both components at once on the same symbol
q₁, q₂: the start states of the two machines
q₀: the start state of the product, the pair of the two start states
F₁, F₂: the accepting-collections of states of the two machines
F_{∩}: the accepting states for intersection (strings both machines accept)
F_{∪}: the accepting states for union (strings at least one machine accepts)
∈: is an element of
{ (p, q) : … }: the set of all pairs that make the condition after the colon true
In words: the product machine tracks both machines at once. It moves each one on every symbol, and it accepts according to a rule: both accept for intersection, at least one accepts for union.
```

Pairing the two parity states with the three remainder states gives six possible pairs. Only reachable pairs need to be built, and equivalent pairs may merge later. The product size is an upper bound on the necessary machine, not a claim of minimality.

For the intersection, `1001` is accepted: it has an even number of 1s and represents nine, divisible by three. A pair with even parity but nonzero remainder fails the intersection and passes the union. Acceptance still happens only after the whole input.

Because the sizes multiply, intersecting k machines multiplies all k of their sizes together. This blow-up is real and shows up in model checking and in regex engines that support intersection.

## Key takeaways
- A product state records one state from each component.
- Intersection requires both components to accept; union requires at least one.

## Further reading
- [MIT: finite automata and regular expressions](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/lecture-1-introduction-finite-automata-regular-expressions/)
- [MIT: nondeterminism and closure properties](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec2-1/)
