# React concepts: beginner to intermediate

Add a standalone React subject (`content/react`, id `react`, title `React`, order 14) for a reader who
knows basic JavaScript variables, functions, arrays and objects but has not used React. Explain any
additional JavaScript syntax immediately before using it. Teach current function components and Hooks,
using the React 19 documentation and tested React 19.3.1 examples. Avoid version trivia in questions.

The outcome is the ability to read a small React application, predict rendering and state updates,
choose where state belongs, and use effects only when synchronising with an external system. Finish
with a small searchable task-list design and concrete behaviour checks, rather than framework setup.

## Modules and stable lesson ids

1. `01-components`, id `react-components`, title **Components and JSX**, order 1:
   - `rc-components`: a component is a function describing a piece of UI; nesting and capitalised names.
   - `rc-javascript-jsx`: values, destructuring, arrow callbacks, imports/exports and JSX expressions.
   - `rc-jsx-rules`: JSX versus HTML, fragments, closed tags, className and styles.
   - `rc-props-composition`: read-only props, children and composing a reusable card.
   - `rc-conditional-ui`: conditional returns, ternaries, null and the numeric-zero && pitfall.
   - `rc-lists-keys`: map/filter, stable sibling keys, key is not a normal prop, and why indexes can fail.
   - `rc-render-purity`: render versus commit, pure render calculations, immutable props and local work.
   - `rc-events-state`: passing event handlers, useState and independent component instances.
2. `02-state`, id `react-state`, title **State and Interactive Forms**, order 2:
   - `rs-state-snapshots`: each render's state snapshot and event-handler closures.
   - `rs-queued-updates`: replacement versus functional updates, batching and pure updater functions.
   - `rs-object-updates`: immutable object updates, shallow spread and nested copies.
   - `rs-array-updates`: map/filter/spread updates and copying objects inside arrays.
   - `rs-controlled-inputs`: controlled text/checkbox inputs, labels and form submission.
   - `rs-lift-state`: one owner, callback props and controlled sibling components.
   - `rs-state-shape`: derive filtered values during render; avoid redundant and contradictory state.
   - `rs-state-identity`: position, type and keys preserve/reset state; avoid nested component definitions.
   - `rs-reducers`: useReducer, pure transitions, action objects and event-to-state traces.
3. `03-hooks`, id `react-hooks`, title **Hooks, Effects and Shared Logic**, order 3:
   - `rh-hook-rules`: ordinary Hooks at the top level, component/custom-hook boundaries and why order matters.
   - `rh-refs-dom`: useRef versus state, DOM focus and refs as an escape hatch, not render data.
   - `rh-effects-cleanup`: external synchronisation, setup/cleanup and development Strict Mode checks.
   - `rh-effect-dependencies`: reactive dependencies, stale closures and avoiding unnecessary effects.
   - `rh-fetch-lifecycle`: a labelled client-only teaching fetch, loading/error/empty states and stale-result cleanup.
   - `rh-custom-hooks`: reuse stateful logic without sharing state automatically; clear inputs and cleanup.
   - `rh-context`: context/provider/consumer, props first, nearest provider and context-update implications.
   - `rh-performance`: measure first; memo/useMemo/useCallback are optimisations, not correctness requirements;
     immutable values, component re-renders and React Compiler caveats.
   - `rh-practice-project`: integrate a searchable task list with minimal state, stable ids and useful behaviour checks.

Keep each lesson to one manageable objective, usually 3–5 minutes. Use substantive explanations and one
concrete trace or short worked example; no outlines or advanced API catalogues. Aim for 2–3 questions per
lesson, with at least some applied multi-select questions per module. Keep ids stable and vary correct
option positions. All required assessment facts must be visible while analogy disclosures are closed.

## Required process and files

Follow this worktree's `CLAUDE.md`, `CONTENT_SPEC.md`, `docs/CONTENT_PROCESS.md`, `docs/new-module.md`,
`docs/verify-brief.md`, `.claude/skills/writing-formulas/SKILL.md` and
`.claude/skills/glossary-terms/SKILL.md`. Every module has a distinct author and independent verifier;
authors never write verification records or stamp their own work. Use an independent verifier for any
later lesson or glossary corrections. Do not change other subjects, legacy exceptions or shared runtime.

Use a helpful, concise `[!analogy]` disclosure where it adds understanding, with explicit **How it maps:**
and **Where it stops:** paragraphs. Do not force one onto a straightforward procedure. Verifiers record
an `analogyReview` decision and rationale for every active lesson using the existing process and hashes.

Provide glossary entries for unfamiliar vocabulary and API names. Use unique `react-` id prefixes and
precise aliases: do not capture ordinary words or mix component state with unrelated meanings. Reuse
earlier modules' definitions. Components module owns general React/JSX/prop/event/state vocabulary;
state module owns new update/forms/reducer vocabulary; hooks module owns effects/refs/context/memoisation.
Inspect actual compiled dictionary links as well as the glossary inventory.

## Examples and executable checks

Use JavaScript and JSX, not Python or TypeScript. Keep fenced lines within 44 characters in lessons and
40 in questions. Label complete examples versus component functions, excerpts or intentionally wrong
examples. Explain imports and the assumed React-enabled environment. Never imply that a browser can
execute untransformed JSX, or recommend legacy Create React App setup. A labelled teaching excerpt
may rely on specified props/imports; supply those in the executable verification harness.

Run every code example, including question snippets, against actual React/React DOM where React behaviour
is claimed. Transpile JSX in a scratch harness; mount components in a DOM and exercise handlers for state,
forms, effects, refs and cleanup. Pure calculations/reducers can use Node assertions. Syntax-check intentional
counterexamples and verify their stated failure or pitfall without relying on exact render-call counts.
Do not claim that static server rendering tests effects or interactions. Do not install React into the study
app or rewrite the PWA: dependencies and harnesses belong under `/tmp/react-course-harness/`.

Use React 19.3.1 and matching React DOM for the scratch harness. Fetch/async tests must control response
order and cover stale responses; do not depend on an external service. Treat Strict Mode's development
checks separately from production. Do not present useMemo or memo as guarantees against re-rendering,
or useEffect as a generic response to every state change. Ordinary Hooks follow the usual rules; do not
claim that the distinct `use` API has identical ordering restrictions. Do not teach useEffectEvent, `use`,
Server Components, Actions or transition APIs as necessary beginner knowledge.

## Sources and scope boundaries

Context7 is unavailable in this session. Fetch actual current source passages from `https://react.dev/learn`,
`https://react.dev/reference/react` and individual official React pages. Use MDN for JavaScript/DOM/Fetch
semantics where needed. Prefer primary sources for every claim and glossary definition. Validate every
lesson/question reading URL. Recheck time-sensitive compiler/framework advice rather than assuming it.

Exclude routing-library APIs, Redux or other state libraries, Next.js, server rendering/hydration internals,
authentication, production data-cache architecture and a full JavaScript or CSS course. Explain a boundary
where relevant without filling beginner lessons with caveats. Fetch is explicitly a lifecycle teaching
example; official frameworks/data libraries may provide production data management.

Authors save `/tmp/react-course-<module>-author.json` with ids, counts, source URLs fetched, exact code
checks, analogy decisions, glossary/formula counts, scope gaps and every uncertain claim. Verifiers save
`/tmp/react-course-<module>-verified.json`, fix issues in place, write and stamp full `verification.json`,
record corrections/gaps/confidence and add current analogy-review hashes. Root integration must run
the full build, all existing tests, scoped links/lints and browser checks at 390 px and desktop, including
practice, dictionary, search, offline loading and preservation of existing progress.
