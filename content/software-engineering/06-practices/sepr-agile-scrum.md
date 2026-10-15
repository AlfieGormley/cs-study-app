---
id: sepr-agile-scrum
title: Agile values and Scrum’s feedback cycle
level: intermediate
minutes: 5
summary: Read the Agile values alongside Scrum accountabilities, events and quality commitments.
sourceLesson: sepr-agile-estimation
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
Scrum is a framework for working in fixed-length iterations called **Scrum Sprints**, usually just called Sprints. The official definition is the *Scrum Guide* by Ken Schwaber and Jeff Sutherland, in its November 2020 version. It is short (under 15 pages) and much of what people call "Scrum" is not in it.

### The Scrum Team

A small team, typically 10 or fewer people, with three accountabilities:

- **Product Owner**: maximises the value of the product; owns and orders the Product Backlog.
- **Scrum Master**: helps the team and organisation use Scrum effectively; causes the removal of impediments to team progress. This accountability is not a project-manager role.
- **Scrum Developers**: everyone doing the work of creating a usable Increment each Sprint, including testers and designers.

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

Scrum is founded on empiricism: make work transparent, inspect what happens and adapt. Product Backlog refinement means continually breaking down and clarifying work items; it is an ongoing activity, not a sixth Scrum event.

### Artefacts and commitments

| Artefact | Commitment |
|---|---|
| Product Backlog | Product Goal |
| Sprint Backlog | Sprint Goal |
| Increment | Definition of Done |

The **Definition of Done** is a shared, explicit quality bar (for example tested, reviewed and documented; exact criteria depend on the product and organisation). Work that does not meet it is not part of the Increment, however close it is.

> [!note] Not in the Scrum Guide
> Story points, velocity, user stories, burndown charts and planning poker are all common practices, but none is required by Scrum.

## Key takeaways
- Agile values feedback and working software while retaining value in plans, tools and documentation.
- Scrum defines three accountabilities, five events and three artefacts with commitments.
- The Definition of Done governs the Increment; popular estimation rituals are not required by Scrum.

## Further reading
- [Manifesto for Agile Software Development](https://agilemanifesto.org/)
- [The Scrum Guide (2020)](https://scrumguides.org/scrum-guide.html)
