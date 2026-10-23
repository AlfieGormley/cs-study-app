Part of the mandatory procedure in `docs/CONTENT_PROCESS.md` (step 2). An independent agent will fact-check
everything you write.

# Brief: write a new module

You're writing one module of a personal iPhone study app that takes the reader from beginner to expert in
computer science. Project: /Users/alfiegormley/Github/cs-study-app

1. Read /Users/alfiegormley/Github/cs-study-app/CONTENT_SPEC.md first and follow it exactly.
2. For the house style and depth, look at one existing lesson and its questions, e.g.
   content/system-design/03-caching/cache-eviction.md and cache-eviction.questions.json.
3. Write ONLY inside your module directory (given in your task). The subject.json already exists; don't touch it,
   or anything else. Other authors are writing other modules at the same time.
4. Write module.json, then each lesson's .md and .questions.json.

Depth and quantity:
- Each lesson covers one coherent learning objective in roughly 3–5 minutes. Preserve depth by using
  several short lessons for a large topic. Use intuition, mechanics, real-world use, trade-offs, worked
  examples, code (Python unless the topic needs C/SQL/etc.), diagrams, tables and callouts as relevant.
- Aim for 2–4 focused questions per lesson. Use `multi` where useful. Favour applied questions:
  "what does this code output?", "what's the complexity of...?", "trace this
  algorithm", scenario and calculation questions. Every workedExample walks through the reasoning step by step.
  Every option explanation names the specific misconception.
- Lessons in a module go basic → advanced.
- Apply the real-world analogy rule in `CONTENT_SPEC.md`: use a concise `[!analogy]` callout where a familiar
  comparison improves understanding, with explicit **How it maps:** and **Where it stops:** paragraphs.
  Keep the main explanation complete while the analogy is collapsed. Do not force repetitive comparisons
  onto procedural or calculation-only lessons; report which lessons need none and why.

Formulas and glossary (mandatory, enforced by the build):
- Read and follow `.claude/skills/writing-formulas/SKILL.md`. Every equation, relation or calculation that uses a
  symbol goes in a ```formula block that defines **every** symbol, unit and function, plus an "In words:" line.
  Assume basic algebra; define symbols' roles and units, use conventional multiplication and make grouping
  explicit. Run `node scripts/lint-formulas.mjs content/<subject>/<module-dir>` and
  resolve every hit.
- Read and follow `.claude/skills/glossary-terms/SKILL.md`. Write `glossary.json` for the module with an entry for
  every acronym, bolded term, unit, named component/protocol/algorithm and piece of jargon a beginner could pause
  on. **Too many is better than too few.** Run `node scripts/glossary-coverage.mjs content/<subject>/<module-dir>`
  as the minimum list.

Accuracy: be correct above all. Check facts you're unsure of. Trace any code you write by hand and make sure
stated outputs and complexities are right.
Add useful comments explaining non-obvious operations and the meaning of shown outputs. Verify those outputs,
and keep comments within the code-width limits.

Links: verify every URL with curl (200 only) or `node scripts/check-links.mjs content/<subject>/<module-dir>`.
Use a scratch folder named after your module so you don't clash with other authors.

When finished, run `node scripts/build.mjs --check content/<subject>/<module-dir>` from the project root and fix
everything else until it passes. The build will report a missing `verification.json`. That's expected: the independent verifier writes it, so don't
create or stamp it yourself.

Your reply must list:
- the lesson ids and the question count;
- any topics in scope you left thin or out, and why;
- every claim you weren't fully confident in, so the verifier can check those first;
- the number of formula blocks and glossary terms written, and any lint hits you left in place with the reason.
