---
id: sepr-relative-estimates
title: Use relative estimates without making false promises
level: intermediate
minutes: 5
summary: Separate estimates from targets and commitments, and understand team-local velocity and coordination costs.
sourceLesson: sepr-agile-estimation
---

Estimates exist to support decisions under uncertainty. This lesson covers what an estimate is (and is not), how relative sizing and velocity are used, and why adding people to a late project is a risky way to recover.

## Estimation
Every business needs some answer to "when will it be ready?" Estimation is hard for well-understood reasons.

- **Unknowns.** Much of software work is discovering what needs doing.
- **The cone of uncertainty.** Steve McConnell, building on Barry Boehm's work, shows that estimates made at the initial-concept stage by skilled estimators can be out by a factor of 4 either way (from a quarter to four times the actual). The cone shows the best accuracy skilled estimators achieve, not a statistical guarantee, and it narrows only as decisions remove sources of variability (what is in scope, what is not). Waiting alone does not narrow it.
- **The planning fallacy.** Kahneman and Tversky described the tendency to underestimate task durations despite contrary experience; later experiments found evidence for it. Hofstadter's tongue-in-cheek law is commonly quoted as: "It always takes longer than you expect, even when you take into account Hofstadter's law."

McConnell also separates three things that are often confused. An **engineering estimate** is a prediction ("probably 6–10 weeks"). A **delivery target** is a desirable business objective ("launch by the conference"); being desirable or even mandatory does not make it achievable. A **delivery commitment** is a promise to deliver. Conflating them turns honest estimates into negotiations.

### Relative estimation: story points

Relative estimation is one technique for discussing size and uncertainty. **Story points** size work relative to a reference item ("this is about twice the password-reset page"), often on a rough Fibonacci-like scale: 1, 2, 3, 5, 8, 13. The growing gaps express growing uncertainty: the scale deliberately avoids debating adjacent large values as if the estimates were precise.

**Planning poker** uses simultaneous revelation to reduce anchoring on the first spoken estimate: everyone reveals a card at once. If one person says 2 and another 13, they discuss, and usually one of them knows something the other does not. That conversation is the most valuable part.

A team's **velocity** (sprint velocity) is the number of story points it completes per Sprint, usually averaged over the last few Sprints. A rough forecast divides the remaining backlog by it: a team that has averaged about 21 points a Sprint, with 105 points left, needs roughly five more Sprints.

That single number hides what the forecast rests on. If recent Sprints ranged from 18 to 24 points, the same backlog takes between about 4.4 and 5.8 Sprints, so "5 or 6" is more honest than "5". It also assumes the backlog stops growing and the team stays the same; when either changes, re-forecast.

Velocity only works within one team: points are relative to that team's reference items, so they are not comparable across teams. Ranking teams by velocity rewards inflating point values rather than delivering value. Use it for local planning, not as a productivity target.

Like any Scrum feedback loop, estimates only help if the team acts on what it learns. Ignoring significant Review findings, or choosing retrospective actions nobody follows through, keeps the ritual and loses the point.

## Brooks's law
Fred Brooks, in *The Mythical Man-Month* (1975): "Adding manpower to a late software project makes it later." Two effects drive it. New people need training from existing members, who deliver less while they teach. And the number of possible pairwise communication links grows much faster than the team: 5 people have 10 possible pairs, but 10 people have 45.

```formula reference
C = n(n − 1) / 2
where
C: the number of possible pairwise communication links in the team
n: the number of people in the team
2: corrects for counting each pair twice (Ann–Bob and Bob–Ann)
In words: each person can pair with everyone else, so the possible links grow roughly with the square of team size: doubling a team from 5 to 10 people takes the possible pairs from 10 to 45.
```

These are possible links, not a claim that every pair talks; team structure and clear interfaces keep actual communication far lower. Some work also cannot be split at all: Brooks's example is that bearing a child takes nine months however many people are assigned.

The law is contested. In a 1999 essay, Steve McConnell reports that twenty years on, Brooks still called it "the best zeroth order approximation to the truth". McConnell himself argued that it applies mainly in a project's final phase, and that many "late" projects are much further from done than their managers think, so added staff have time to become productive. The practical question is how far from the end you really are, and whether the work can be split into independent pieces.

## Key takeaways
- An estimate predicts, a target expresses a desire and a commitment makes a promise.
- Story points and velocity are local planning tools; compare shared assumptions rather than ranking teams.
- Brooks's law warns that onboarding and coordination can make a late project later; how much depends on how near the end you are and how separable the work is.

## Further reading
- [The Purpose of Agile Planning — Mike Cohn](https://www.informit.com/articles/article.aspx?p=1374899)
- [Planning Poker — Mike Cohn](https://www.mountaingoatsoftware.com/agile/planning-poker)
- [Velocity — Mike Cohn](https://www.mountaingoatsoftware.com/agile/agile-leadership/dont-compare-team-velocities)
- [The Cone of Uncertainty — Construx](https://www.construx.com/books/the-cone-of-uncertainty/)
- [Brooks' Law Repealed? — Steve McConnell](https://stevemcconnell.com/articles/brooks-law-repealed/)
