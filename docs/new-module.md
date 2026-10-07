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
- Each lesson is substantial (roughly 1,000–1,800 words): intuition first, then mechanics, then real-world use,
  trade-offs and pitfalls. Use worked examples, code (Python unless the topic needs C/SQL/etc.), ASCII
  diagrams, tables and callouts.
- 10–12 questions per lesson, mixing levels (about 3 basic, 4–5 intermediate, 3–4 advanced) with at least two
  `multi`. Favour applied questions: "what does this code output?", "what's the complexity of...?", "trace this
  algorithm", scenario and calculation questions. Every workedExample walks through the reasoning step by step.
  Every option explanation names the specific misconception.
- Lessons in a module go basic → advanced.

Accuracy: be correct above all. Check facts you're unsure of. Trace any code you write by hand and make sure
stated outputs and complexities are right.

Links: verify every URL with curl (200 only) or `node scripts/check-links.mjs content/<subject>/<module-dir>`.
Use a scratch folder named after your module so you don't clash with other authors.

When finished, run `node scripts/build.mjs --check content/<subject>/<module-dir>` from the project root and fix
everything else until it passes. The build will report a missing `verification.json`. That's expected: the independent verifier writes it, so don't
create or stamp it yourself.

Your reply must list:
- the lesson ids and the question count;
- any topics in scope you left thin or out, and why;
- every claim you weren't fully confident in, so the verifier can check those first.
