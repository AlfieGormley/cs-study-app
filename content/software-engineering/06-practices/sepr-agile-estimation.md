---
id: sepr-agile-estimation
title: Agile, Scrum, Kanban and estimation
level: intermediate
minutes: 14
summary: What the Agile Manifesto actually says, how Scrum and Kanban work and differ, Little's law for flow, and how to estimate and forecast honestly with story points, ranges and Monte Carlo simulation.
---

The label "Agile" is used for a variety of software processes. In practice that word covers everything from small, self-organising teams shipping daily to heavyweight processes with more meetings than releases. To work well in any of them, it helps to know what the ideas actually are and why they exist.

## The problem Agile was solving

The traditional **waterfall** model runs in phases: gather all requirements, design everything, build it, test it, release. Sequential planning is easier when requirements are stable, but safety-critical or contractual work does not by itself justify deferring integration, feedback or validation.

Software requirements can change or remain uncertain. Users only know what they want once they see something; markets move; technical unknowns surface mid-build. A waterfall project discovers these problems at the end, when changing course is most expensive. (Winston Royce's 1970 paper, often cited as the origin of waterfall, actually described the purely sequential version as risky and recommended iteration.)

## The Agile Manifesto

In 2001, seventeen practitioners met in Snowbird, Utah, and wrote the **Manifesto for Agile Software Development**. It is four lines:

- **Individuals and interactions** over processes and tools
- **Working software** over comprehensive documentation
- **Customer collaboration** over contract negotiation
- **Responding to change** over following a plan

It adds: "while there is value in the items on the right, we value the items on the left more." Agile does not mean no documentation or no plan. It means you deliver working software in short cycles, get feedback, and adjust, because that is cheaper than being wrong for a year.

Scrum and Kanban are two approaches used to organise work and feedback.

## Scrum

Scrum is a framework for working in fixed-length iterations called **Scrum Sprints**, usually just called Sprints. The official definition is the *Scrum Guide* by Ken Schwaber and Jeff Sutherland, last revised in 2020. It is short (under 15 pages) and much of what people call "Scrum" is not in it.

### The Scrum Team

A small team, typically 10 or fewer people, with three accountabilities:

- **Product Owner**: maximises the value of the product; owns and orders the Product Backlog.
- **Scrum Master**: helps the team and organisation use Scrum effectively; causes the removal of impediments to team progress. This accountability is not a project-manager role.
- **Developers**: everyone doing the work of creating a usable Increment each Sprint, including testers and designers.

### Events

| Event | Timebox (1-month Sprint) |
|---|---|
| Sprint | One month or less |
| Sprint Planning | Up to 8 hours |
| Daily Scrum | 15 minutes |
| Sprint Review | Up to 4 hours |
| Sprint Retrospective | Up to 3 hours |

For shorter Sprints, Planning, Review and Retrospective are usually shorter; the Daily Scrum remains a 15-minute event. The Guide does not prescribe a most-common Sprint length.

- **Sprint Planning** answers why this Sprint is valuable (the **Sprint Goal**), what can be done, and how.
- **Daily Scrum** is for the Developers to inspect progress towards the Sprint Goal and adapt the plan. The 2020 Guide dropped the old "three questions" format.
- **Sprint Review** shows stakeholders what was done and decides what to do next. It is a working session, not a demo for applause.
- **Sprint Retrospective** looks at how the team works and picks improvements.

### Artefacts and commitments

| Artefact | Commitment |
|---|---|
| Product Backlog | Product Goal |
| Sprint Backlog | Sprint Goal |
| Increment | Definition of Done |

The **Definition of Done** is a shared, explicit quality bar (for example tested, reviewed and documented; exact criteria depend on the product and organisation). Work that does not meet it is not part of the Increment, however close it is.

> [!note] Not in the Scrum Guide
> Story points, velocity, user stories, burndown charts and planning poker are all common practices, but none is required by Scrum.

## Kanban

Kanban comes from Toyota's production system, where cards ("kanban" means signboard) signalled when to produce more. David J. Anderson adapted it for software in the mid-2000s.

Kanban does not prescribe roles or iterations. Useful practices include:

1. **Visualise the workflow** on a board, with a column per stage.
2. **Control work in progress (WIP)** with explicit policies; limits may cover individual stages or a larger part of the workflow.
3. **Manage flow**: measure how work moves and remove blockages.
4. **Make policies explicit**, such as what "ready for review" means.
5. **Improve continuously** using data and feedback loops.

```
| To do | Dev (3) | Review (2) | Done |
|-------|---------|------------|------|
| F     | C       | A          | X    |
| G     | D       | B          | Y    |
| H     | E       |            |      |
```

The numbers are WIP limits. With Dev full at 3, a developer who finishes C does not start F; they help clear Review first. This is a **pull system**, not push: work moves when there is capacity downstream. Stop starting, start finishing.

### Little's law

Why limit WIP? **Little's law**, proved by John Little in 1961 for queueing systems, links three averages. It answers the question "if we keep this much work open, how long will each item take on average?" It holds for a stable system over the long run, meaning work leaves at about the rate it arrives, so the queue is not growing without limit:

```formula
L = λ × W
W = L / λ
where
L: the average WIP: how many items are in progress (started but not finished) at any moment, in items
λ: lambda, the average throughput: how many items the workflow finishes per unit of time, in items per week
W: the average cycle time: how long one item spends between starting and finishing, in weeks
In words: the average amount of open work equals the finishing rate times the average time each item spends in the system, so with the finishing rate fixed, less open work means each item gets through faster.
```

The second line is the same law rearranged. All three must use the same workflow boundary (say, "from Dev to Done") and the same time unit. The law says nothing about any single item, and it fails if the board is filling up or emptying.

> [!example] Halving WIP
> In a stable workflow, average throughput is 4 items a week and average WIP is 12. Then average WIP falls to 6 while throughput stays at 4. A WIP cap is not the measured average, and this does not promise that every item finishes twice as fast.

```formula
W = L / λ
W = 12 / 4 = 3 wk
W = 6 / 4 = 1.5 wk
where
W: the average cycle time, in weeks (wk)
L: the average WIP, in items: 12 before, 6 after
λ: lambda, the average throughput, in items per week; 4 in both cases
wk: weeks, the unit of time used here
In words: with the finishing rate unchanged, halving the average amount of open work halves the average time an item takes, from 3 weeks to 1.5 weeks.
```

Lower WIP may reduce context switching, but excessive restriction can starve stages and reduce throughput. Measure both flow and capacity.

### Scrum versus Kanban

| | Scrum | Kanban |
|---|---|---|
| Cadence | Fixed Sprints | Continuous flow |
| Roles | PO, SM, Developers | None required |
| Planning focus | Sprint Goal and evolving plan | Flow and WIP policies |
| Useful measures | Goal outcomes and product value | WIP, throughput, work-item age, cycle time |

Kanban suits work that arrives unpredictably (operations, support, platform teams). Scrum suits product development where a regular rhythm of planning and review helps. Kanban can also complement Scrum. Sprint scope may be clarified and renegotiated with the Product Owner as learning occurs without endangering the Sprint Goal.

## Estimation

Every business needs some answer to "when will it be ready?" Estimation is hard for well-understood reasons.

- **Unknowns.** Much of software work is discovering what needs doing.
- **The cone of uncertainty.** Steve McConnell, building on Barry Boehm's work, illustrates a possible early range of 0.25× to 4× in his cone model. It is not a universal statistical confidence interval. Reducing uncertainty requires decisions and learning; elapsed time alone does not narrow it.
- **The planning fallacy.** Kahneman and Tversky showed people systematically underestimate their own tasks, even when they know similar tasks overran. Hofstadter's law: "It always takes longer than you expect, even when you take into account Hofstadter's law."

McConnell also separates three things that are often confused. An **estimate** is a prediction ("probably 6–10 weeks"). A **target** is a desired outcome ("launch by the conference"). A **commitment** is a promise. Conflating them turns honest estimates into negotiations.

### Relative estimation: story points

Relative estimation is one technique for discussing size and uncertainty. **Story points** size work relative to a reference item ("this is about twice the password-reset page"), often on a rough Fibonacci-like scale: 1, 2, 3, 5, 8, 13. The growing gaps express growing uncertainty: there is no meaningful difference between 14 and 15.

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

This illustrative forecast assumes the backlog stays the same size and the team's capacity stays stable. Because the past Sprints varied from 18 to 24 points, a range (about 4.4 to 5.8 Sprints, so 5 or 6) is more honest than the single number. Velocity only works within one team: points are not comparable across teams.

### Ranges and three-point estimates

A single number hides uncertainty. A **three-point estimate** gives three values for one task: an optimistic one, a most likely one and a pessimistic one. **PERT** (the Program Evaluation and Review Technique, developed for the US Navy's Polaris programme in the late 1950s) combines them into a single expected duration by weighting the most likely value four times as heavily as either extreme:

```formula
E = (O + 4 × M + P) / 6
E = (2 + 4 × 4 + 12) / 6
E = (2 + 16 + 12) / 6
E = 30 / 6 = 5 d
where
E: the PERT expected (mean) duration of the task, in days (d)
O: the optimistic estimate, if most things go well, in days; here 2
M: the most likely estimate (the mode), in days; here 4
P: the pessimistic estimate, if most things go badly, in days; here 12
d: days, the unit of time used here
4: the weight given to the most likely value, so it counts four times as much as each extreme
6: the sum of the weights (1 + 4 + 1), which turns the weighted sum back into an average
In words: add the optimistic and pessimistic values to four times the most likely one and divide by six; a long pessimistic tail pulls the expected value above the most likely one.
```

The weights come from approximating each task's duration with a beta distribution, a smooth curve bounded by the optimistic and pessimistic values. Under this PERT weighting model the estimated mean (5) is above the mode (4), reflecting the asymmetric inputs. Three inputs alone do not establish the true distribution, and not every duration distribution is right-skewed.

### Forecasting from data: Monte Carlo

If the team tracks how many items it finishes each week, it can forecast without estimating individual items. Simulate the future by sampling from past throughput:

```python
import random
random.seed(42)

# items finished in each past week
history = [3, 5, 2, 6, 4, 4, 1, 5]

def weeks_to_finish(backlog):
    done, weeks = 0, 0
    while done < backlog:
        done += random.choice(history)
        weeks += 1
    return weeks

runs = sorted(weeks_to_finish(40)
              for _ in range(10_000))
print("50%:", runs[5_000])
print("85%:", runs[8_500])
```

For comparison, the simple average gives a single-number answer:

```formula
λ = (3 + 5 + 2 + 6 + 4 + 4 + 1 + 5) / 8
λ = 30 / 8 = 3.75 per wk
T ≈ B / λ
T ≈ 40 / 3.75 ≈ 10.7 wk
where
λ: lambda, the average throughput over the 8 recorded weeks, in items finished per week
8: the number of past weeks in the history
T: the naive forecast time to finish the backlog, in weeks
wk: weeks, the unit of time used here
B: the remaining backlog, here 40 items
≈: approximately equal to
In words: the team finished 30 items in 8 weeks, about 3.75 a week, so 40 items would take roughly 10.7 weeks at that average pace.
```

The average says nothing about how likely a miss is; the simulation does. The seeded example prints 11 weeks at the 50th percentile and 13 weeks at the 85th. These are model outputs, not guaranteed real-world probabilities. Resampling assumes this short history represents future throughput, weeks can be sampled independently, remaining items are comparable and the backlog stays fixed. Changes in scope, staffing or dependence can invalidate the forecast.

Some teams take this further with **#NoEstimates**: split work into small, similar-sized items and forecast purely from throughput.

## Brooks's law

Fred Brooks, in *The Mythical Man-Month* (1975): "Adding manpower to a late software project makes it later." New people need training from existing members, and the number of possible pairwise communication links grows much faster than the team. Each of the n people can pair with the n − 1 others, and that counts every pair twice (Ann–Bob and Bob–Ann), so divide by 2:

```formula
C = n × (n − 1) / 2
C = 5 × 4 / 2 = 10
C = 10 × 9 / 2 = 45
where
C: the number of possible one-to-one communication links in the team
n: the number of people in the team; here 5, then 10
2: corrects for counting each pair twice
In words: doubling a team from 5 to 10 people more than quadruples the possible pairs, from 10 to 45.
```

These are possible links, not a claim that every pair communicates or that actual overhead must be quadratic. Adding people can help on separable work; evaluate onboarding and coordination costs.

## Pitfalls

- **Cargo-cult Scrum.** All the ceremonies, none of the feedback. Ignoring feedback that requires adaptation undermines the Review; it need not change the backlog on every occasion.
- **Velocity as a performance target.** Goodhart's law: once points are a measure of productivity, they inflate. Velocity is a planning tool for the team.
- **Converting points to hours.** It discards the reason for relative sizing.
- **Ignoring the retrospective.** A retro that picks no action, or never checks last time's action, is a wasted hour.
- **Single-number estimates treated as promises.** Give ranges with a confidence level, and re-forecast as you learn.

## Key takeaways
- Agile favours short feedback cycles over big upfront plans; it does not mean no planning or no docs.
- Scrum has three accountabilities, five timeboxed events and three artefacts, each with a commitment (Product Goal, Sprint Goal, Definition of Done).
- Kanban visualises flow and limits WIP; by Little's law, average cycle time is average WIP divided by average throughput, so reducing average WIP reduces average cycle time if throughput stays fixed and the stable-system assumptions hold.
- Estimates are uncertain by nature: use relative sizing, ranges, three-point estimates or Monte Carlo forecasts from real throughput.
- Keep estimates, targets and commitments distinct, and remember Brooks's law when a project is late.

## Further reading
- [Manifesto for Agile Software Development](https://agilemanifesto.org/)
- [The Scrum Guide (2020)](https://scrumguides.org/scrum-guide.html)
- [Kanban (development) — Wikipedia](https://en.wikipedia.org/wiki/Kanban_(development))
- [Little's law — Wikipedia](https://en.wikipedia.org/wiki/Little%27s_law)
- [Planning poker — Wikipedia](https://en.wikipedia.org/wiki/Planning_poker)
- [Cone of Uncertainty — Wikipedia](https://en.wikipedia.org/wiki/Cone_of_Uncertainty)
- [Brooks's law — Wikipedia](https://en.wikipedia.org/wiki/Brooks%27s_law)
