# Brief: review, improve and extend an existing module

You're improving one module of a personal iPhone study app that teaches System Design from beginner to expert.
Project: /Users/alfiegormley/Github/cs-study-app

1. Read /Users/alfiegormley/Github/cs-study-app/CONTENT_SPEC.md first. It has been updated since this module was
   written: 10–12 questions per lesson, a 40-character code-line limit inside questions, and question-id rules.
2. Write ONLY inside your module directory. Other authors are editing other modules at the same time.

Your job, for every lesson in the module:

A. Fact-check and fix. Read every lesson and question critically, as a staff engineer and a strict reviewer would.
   Fix factual errors, outdated claims (e.g. defaults that changed in recent versions), wrong maths, wrong
   answer keys, and explanations that contradict the lesson. Where a specific figure can't be verified, soften it
   ("around", "typically") or remove it.

B. Improve the teaching. Tighten wordy passages, clarify confusing explanations, add a missing intuition or
   example where a section is thin, make sure each lesson builds logically, and fix any rendering problems
   (only the Markdown subset in the spec). Don't shorten lessons overall. Keep British English.

C. Add questions. Bring every lesson to 12 questions by adding new ones. Continue the id numbering
   (`<lessonId>-q8`, `-q9`, ...). NEVER change or reuse an existing question id, because user progress is stored
   against it. You may improve an existing question's wording, options and explanations as long as it still tests
   the same idea. The new questions should mostly be intermediate or advanced, applied or scenario based, and
   cover parts of the lesson the existing questions miss. Include at least two `multi` per lesson overall.

D. Fix any code line wider than 40 characters inside questions (the build reports them), and keep lesson code
   lines at 44 or fewer.

Verify every new or changed URL. Use `node scripts/check-links.mjs content/system-design/<module-dir>` and a
scratch folder named after your module.

When finished, run `node scripts/build.mjs --check content/system-design/<module-dir>` and fix everything until it
passes. Reply briefly: the corrections you made (especially factual ones), and the question count per lesson.
