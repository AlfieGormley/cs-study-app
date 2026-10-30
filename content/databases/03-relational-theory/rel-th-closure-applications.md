---
id: rel-th-closure-applications
title: Applying attribute closure
level: intermediate
minutes: 2
sourceLesson: rel-th-functional-deps
summary: Using attribute closure to test implications and superkeys and to compare dependency sets.
---

## Three jobs for attribute closure

1. **Does a given FD follow from the rules?** Compute the attribute closure of its left side and check that its right side is inside it.
2. **Is a set of attributes a superkey?** Yes exactly when its attribute closure is the whole heading.
3. **Do two rule sets say the same thing?** Yes if every FD in each set follows from the other set.

```formula reference
F ⊨ X → Y iff Y ⊆ X⁺
X⁺ = R
F ≡ G iff F⁺ = G⁺
where
F, G: two sets of FDs over the same relation
X, Y: sets of attributes
→: functionally determines
⊨: logically implies: every relation state satisfying F also satisfies the FD on the right
⊆: is a subset of
X⁺: the attribute closure of X under F
R: the set of all attributes of the relation; X⁺ = R means X is a superkey
≡: equivalent: F and G imply exactly the same FDs
F⁺, G⁺: the FD closures of F and G: every FD each one implies
In words: a rule follows when everything on its right side is in the attribute closure of its left side; a set is a superkey when its attribute closure is the whole heading; and two rule sets are equivalent when they imply exactly the same rules.
```

## Using attribute closure on a real design

Take a reporting table `order_item(order_id, customer_id, customer_email, product_id, qty)` with three business rules: an order belongs to one customer, a customer has one email, and the quantity belongs to an order and product together.

- **Is `order_id` a key?** Its attribute closure is the order id, customer id and email. That is not the whole heading, so no: one order has several items.
- **Is the order and product pair a key?** Its attribute closure picks up the customer and email through the order, and the quantity through the pair: the whole heading. It is a superkey, and since neither half alone reaches everything, it is a candidate key.
- **Does "order determines email" follow?** The attribute closure of the order id contains the email, so yes. It is never stated directly, yet it holds: a fact worth knowing, because it means the email is repeated on every item of every order.

**Equivalence in practice.** Suppose a refactor deletes the stated rule "order determines email" from the documented rule set, keeping "order determines customer" and "customer determines email". Check each deleted rule against the remaining set: the attribute closure of the order id still reaches the email, so nothing was lost. Test equivalence rule by rule like this, in both directions, rather than ever listing every implied dependency.

## Key takeaways

- The attribute closure of a determinant tests both implication and superkeys.
- Two FD sets are equivalent exactly when each derives all dependencies of the other.

## Further reading

- [Silberschatz, Korth and Sudarshan: relational database design](https://www.db-book.com/slides-dir/PDF-dir/ch7.pdf)
- [Functional dependency (Wikipedia)](https://en.wikipedia.org/wiki/Functional_dependency)
