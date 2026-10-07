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

Scrum is a framework for working in fixed-length iterations called **Sprints**. The official definition is the *Scrum Guide* by Ken Schwaber and Jeff Sutherland, last revised in 2020. It is short (under 15 pages) and much of what people call "Scrum" is not in it.

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

The numbers are WIP limits. With Dev full at 3, a developer who finishes C does not start F; they help clear Review first. This is **pull**, not push: work moves when there is capacity downstream. Stop starting, start finishing.

### Little's law

Why limit WIP? **Little's law** from queueing theory says, for a stable system over the long run:

```
avg WIP = throughput x avg cycle time
```

Rearranged: average cycle time = average WIP / average throughput, using the same workflow boundary and time units.

> [!example] Halving WIP
> In a stable workflow, average throughput is 4 items/week and average WIP is 12, so average cycle time is **3 weeks**. If average WIP becomes 6 while average throughput remains 4, average cycle time becomes **1.5 weeks**. A WIP cap is not the measured average, and this does not promise that every item finishes twice as fast.

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

Relative estimation is one technique for discussing size and uncertainty. **Story points** size work relative to a reference item ("this is about twice the login page"), often on a rough Fibonacci-like scale: 1, 2, 3, 5, 8, 13. The growing gaps express growing uncertainty: there is no meaningful difference between 14 and 15.

**Planning poker** uses simultaneous revelation to reduce anchoring on the first spoken estimate: everyone reveals a card at once. If one person says 2 and another 13, they discuss, and usually one of them knows something the other does not. That conversation is the most valuable part.

**Velocity** is points completed per Sprint, used to forecast how much the team can take on. It only works within one team: points are not comparable across teams.

### Ranges and three-point estimates

A single number hides uncertainty. A **three-point estimate** gives optimistic (O), most likely (M) and pessimistic (P) values. The PERT formula weights them:

```
expected = (O + 4M + P) / 6
O=2, M=4, P=12 days
(2 + 16 + 12) / 6 = 5 days
```

Under this PERT weighting model the estimated mean (5) is above the mode (4), reflecting the asymmetric inputs. Three inputs alone do not establish the true distribution, and not every duration distribution is right-skewed.

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

Average throughput is 30 / 8 = 3.75 items a week. The seeded example prints 11 weeks at the 50th percentile and 13 weeks at the 85th. These are model outputs, not guaranteed real-world probabilities. Resampling assumes this short history represents future throughput, weeks can be sampled independently, remaining items are comparable and the backlog stays fixed. Changes in scope, staffing or dependence can invalidate the forecast.

Some teams take this further with **#NoEstimates**: split work into small, similar-sized items and forecast purely from throughput.

## Brooks's law

Fred Brooks, in *The Mythical Man-Month* (1975): "Adding manpower to a late software project makes it later." New people need training from existing members, and the number of possible pairwise communication links grows as n(n−1)/2: a team of 5 has 10, a team of 10 has 45. These are possible links, not a claim that every pair communicates or that actual overhead must be quadratic. Adding people can help on separable work; evaluate onboarding and coordination costs.

## Pitfalls

- **Cargo-cult Scrum.** All the ceremonies, none of the feedback. Ignoring feedback that requires adaptation undermines the Review; it need not change the backlog on every occasion.
- **Velocity as a performance target.** Goodhart's law: once points are a measure of productivity, they inflate. Velocity is a planning tool for the team.
- **Converting points to hours.** It discards the reason for relative sizing.
- **Ignoring the retrospective.** A retro that picks no action, or never checks last time's action, is a wasted hour.
- **Single-number estimates treated as promises.** Give ranges with a confidence level, and re-forecast as you learn.

## Key takeaways
- Agile favours short feedback cycles over big upfront plans; it does not mean no planning or no docs.
- Scrum has three accountabilities, five timeboxed events and three artefacts, each with a commitment (Product Goal, Sprint Goal, Definition of Done).
- Kanban visualises flow and limits WIP; by Little's law, cycle time = WIP / throughput, so reducing average WIP reduces average cycle time if throughput stays fixed and the stable-system assumptions hold.
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
