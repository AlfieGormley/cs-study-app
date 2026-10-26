---
id: prob-outcomes-events
title: Count outcomes and events
level: basic
minutes: 3
sourceLesson: prob-basics
summary: Count ordered outcomes only when they are equally likely.
---

Probability describes uncertainty in a specified experiment. Before counting, decide what one outcome records. A request might succeed or fail; two dice produce a pair of face values, not just a total.

## Choose outcomes before counting

The **sample space** contains all possible outcomes. A **random event** is a set of outcomes we care about: for example, all dice pairs whose total is seven. A probability assigns an event a number between zero and one.

Counting gives a probability only in a finite nonempty space whose outcomes are equally likely. Otherwise each outcome needs its own weight. Two labels such as “success” and “failure” do not imply equal chances.

With two independent fair six-sided dice, there are 36 equally likely ordered pairs. Seven is a more likely total than two because six pairs make seven and only one makes two. The totals themselves are not equally likely.

```formula reference
P(A) = |A| / |Ω|
where
P: probability of measurable events, dimensionless and between zero and one
P(A): the probability of event A, a number from 0 to 1; probability zero need not mean an impossible outcome in an infinite model
A: the event we care about, written as the set of outcomes that count as "A happened"
Ω: omega, the sample space: the set of every possible outcome
|A|: the number of outcomes in A (vertical bars around a set mean "how many elements it has")
|Ω|: the total number of possible outcomes
In words: When every outcome is equally likely, an event’s probability is its share of all outcomes.
```

The formula is a counting shortcut after the model is justified. A loaded die needs different weights even though its face labels are unchanged.

## Do not merge unequal categories

First-die one and second-die six differs from first-die six and second-die one. Combining them into an unordered pair creates a category with two ways to occur; a double such as three and three has only one. Treating those categories as equally likely changes the model.

## Key takeaways
- Define the experiment and its outcomes before counting.
- Equal labels do not imply equal probabilities.
- Preserve order when the experiment distinguishes positions.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
