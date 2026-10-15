---
id: sepr-relative-estimates
title: Use relative estimates without making false promises
level: intermediate
minutes: 5
summary: Separate estimates from targets and commitments, and understand team-local velocity and coordination costs.
sourceLesson: sepr-agile-estimation
---

Forecasts support decisions under uncertainty. Relative sizing can expose different understandings, while staffing changes introduce their own uncertainty.

## Estimation
Every business needs some answer to "when will it be ready?" Estimation is hard for well-understood reasons.

- **Unknowns.** Much of software work is discovering what needs doing.
- **The cone of uncertainty.** Steve McConnell, building on Barry Boehm's work, illustrates a possible early range of 0.25× to 4× in his cone model. It is not a universal statistical confidence interval. Reducing uncertainty requires decisions and learning; elapsed time alone does not narrow it.
- **The planning fallacy.** Kahneman and Tversky described the tendency to underestimate task durations despite contrary experience; later experiments found evidence for it. Hofstadter's tongue-in-cheek law is commonly quoted as: "It always takes longer than you expect, even when you take into account Hofstadter's law."

McConnell also separates three things that are often confused. An **engineering estimate** is a prediction ("probably 6–10 weeks"). A **delivery target** is a desired outcome ("launch by the conference"). A **delivery commitment** is a promise. Conflating them turns honest estimates into negotiations.

### Relative estimation: story points

Relative estimation is one technique for discussing size and uncertainty. **Story points** size work relative to a reference item ("this is about twice the password-reset page"), often on a rough Fibonacci-like scale: 1, 2, 3, 5, 8, 13. The growing gaps express growing uncertainty: the scale deliberately avoids debating adjacent large values as if the estimates were precise.

**Planning poker** uses simultaneous revelation to reduce anchoring on the first spoken estimate: everyone reveals a card at once. If one person says 2 and another 13, they discuss, and usually one of them knows something the other does not. That conversation is the most valuable part.

A team's **velocity** (sprint velocity) is the number of story points it completes per Sprint, used to forecast how much the team can take on. It is usually averaged over the last few Sprints, and a rough forecast divides the remaining backlog by it:

```formula
v = (P_1 + P_2 + P_3) / 3
v = (21 + 18 + 24) / 3 = 21
N ≈ B / v
N ≈ 105 / 21 = 5
where
v: the team's velocity: the average number of story points it completed per Sprint
P_1: the story points actually completed (meeting the Definition of Done) in the oldest of the last three Sprints, here 21
P_2: the story points completed in the next Sprint, here 18
P_3: the story points completed in the most recent Sprint, here 24
3: the number of past Sprints averaged (an illustrative choice; teams often use the last few)
N: the forecast number of Sprints needed to finish the remaining work
B: the remaining backlog, in story points, sized by the same team
≈: approximately equal to; the forecast is a rough guide, not a promise
In words: a team that has averaged 21 points a Sprint, with 105 points of work left, will need roughly five more Sprints if nothing else changes.
```

This illustrative forecast assumes the backlog stays the same size and the team's capacity stays stable. Because the past Sprints varied from 18 to 24 points, a range (about 4.4 to 5.8 Sprints, so 5 or 6) is more honest than the single number. Velocity only works within one team: points are not comparable across teams. Ranking teams by velocity can reward inflated point assignments rather than delivered value; use it for local planning, not as a productivity target. Scrum’s feedback practices also require acting on significant Review findings and following through on retrospective improvements, as introduced earlier.

## Brooks's law
Fred Brooks, in *The Mythical Man-Month* (1975): "Adding manpower to a late software project makes it later." New people need training from existing members, and the number of possible pairwise communication links grows much faster than the team. Each person can pair with every other person, and that counts every pair twice (Ann–Bob and Bob–Ann), so divide by 2:

```formula
C = n × (n − 1) / 2
C = 5 × 4 / 2 = 10
C = 10 × 9 / 2 = 45
where
C: the number of possible pairwise communication links in the team
n: the number of people in the team; here 5, then 10
2: corrects for counting each pair twice
In words: doubling a team from 5 to 10 people more than quadruples the possible pairs, from 10 to 45.
```

These are possible links, not a claim that every pair communicates or that actual overhead must be quadratic. Adding people can help on separable work; evaluate onboarding and coordination costs.

## Key takeaways
- An estimate predicts, a target expresses a desire and a commitment makes a promise.
- Story points and velocity are local planning tools; compare shared assumptions rather than ranking teams.
- Possible communication pairs grow faster than team size, but actual overhead depends on the work.

## Further reading
- [The Purpose of Agile Planning — Mike Cohn](https://www.informit.com/articles/article.aspx?p=1374899)
- [Planning Poker — Mike Cohn](https://www.mountaingoatsoftware.com/agile/planning-poker)
- [Velocity — Mike Cohn](https://www.mountaingoatsoftware.com/agile/agile-leadership/dont-compare-team-velocities)
