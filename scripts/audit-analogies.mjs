#!/usr/bin/env node
// Inventory active lessons only. Heuristics identify review leads, never certify teaching quality.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { lessonHash } from './verification.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CANDIDATE = /\banalog(?:y|ies)\b|\bthink of\b|\bimagine\b|\bpicture (?:a|an)\b|\blike (?:a|an|the|someone)\b|\bmetaphor\b/i;

const currentReview = (meta, entry, hash, stamp) => Boolean(meta?.ruleVersion === 1 && meta.author?.agent &&
  meta.verifier?.independent === true && meta.verifier.agent && meta.verifier.agent !== meta.author.agent &&
  Array.isArray(meta.verifier.sources) && meta.verifier.sources.length && entry?.rationale && entry.hash === hash && stamp === hash);

export function inspectAnalogies(markdown) {
  const lines = markdown.replace(/^---\n[\s\S]*?\n---\n?/, match => match.replace(/[^\n]/g, '')).split(/\r?\n/);
  const blocks = [];
  const candidates = [];
  let fence = false;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/^\s*```/.test(line)) { fence = !fence; continue; }
    if (fence) continue;
    const tag = line.match(/^\s*>\s*\[!analogy\]\s*(.*)$/i);
    if (tag) {
      const body = [];
      const start = i;
      while (i + 1 < lines.length && /^\s*>/.test(lines[i + 1])) body.push(lines[++i].replace(/^\s*>\s?/, ''));
      const text = body.join('\n');
      const problems = [];
      if (!tag[1].trim()) problems.push('Use a descriptive real-world analogy summary.');
      if (!/\*\*How it maps:\*\*\s*\S/i.test(text)) problems.push('Missing explicit How it maps paragraph.');
      if (!/\*\*Where it stops:\*\*\s*\S/i.test(text)) problems.push('Missing explicit Where it stops paragraph.');
      if (/```formula\b/.test(text)) problems.push('Keep required formulas outside optional analogies.');
      blocks.push({ line: start + 1, title: tag[1], problems });
    } else if (CANDIDATE.test(line)) {
      candidates.push({ line: i + 1, text: line.trim().slice(0, 240) });
    }
  }
  return { blocks, candidates };
}

export function auditAnalogies(root = ROOT) {
  const read = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
  const content = path.join(root, 'content');
  const subjects = [];
  for (const subjectDir of fs.readdirSync(content, { withFileTypes: true }).filter(d => d.isDirectory()).sort((a,b) => a.name.localeCompare(b.name))) {
    const subjectPath = path.join(content, subjectDir.name);
    if (!fs.existsSync(path.join(subjectPath, 'subject.json'))) continue;
    const subject = read(path.join(subjectPath, 'subject.json'));
    const modules = [];
    for (const moduleDir of fs.readdirSync(subjectPath, { withFileTypes: true }).filter(d => d.isDirectory()).sort((a,b) => a.name.localeCompare(b.name))) {
      const modulePath = path.join(subjectPath, moduleDir.name);
      if (!fs.existsSync(path.join(modulePath, 'module.json'))) continue;
      const mod = read(path.join(modulePath, 'module.json'));
      const verificationPath = path.join(modulePath, 'verification.json');
      const verification = fs.existsSync(verificationPath) ? read(verificationPath) : {};
      const lessons = mod.lessons.map(id => {
        const file = path.join(modulePath, `${id}.md`);
        const source = fs.readFileSync(file, 'utf8');
        const { blocks, candidates } = inspectAnalogies(source);
        const questionProblems = [];
        const questionCandidates = [];
        const questionFile = path.join(modulePath, `${id}.questions.json`);
        const questions = read(questionFile);
        for (const q of questions) {
          for (const [field, text] of [['prompt', q.prompt], ...q.options.map((o,i) => [`option ${i + 1}`, o.text])]) {
            const inspection = inspectAnalogies(text ?? '');
            if (inspection.blocks.length) questionProblems.push(`${q.id}: analogy disclosure in ${field}`);
            for (const candidate of inspection.candidates) questionCandidates.push({question:q.id, field, ...candidate});
          }
          for (const [field, text] of [['workedExample', q.workedExample], ...q.options.map((o,i) => [`option ${i + 1} explanation`, o.explanation])]) {
            const inspection = inspectAnalogies(text ?? '');
            for (const block of inspection.blocks) for (const problem of block.problems) questionProblems.push(`${q.id} ${field}: ${problem}`);
            for (const candidate of inspection.candidates) questionCandidates.push({question:q.id, field, ...candidate});
          }
        }
        const review = verification.analogyReview?.lessons?.[id];
        const reviewMeta = verification.analogyReview;
        const currentHash = lessonHash(modulePath, id);
        const reviewed = currentReview(reviewMeta, review, currentHash, verification.lessons?.[id]?.hash) &&
          ['added', 'converted', 'retained', 'not-needed'].includes(review.decision);
        const questionFeedback = Object.entries(verification.analogyFeedbackReview?.questions ?? {}).find(([, record]) => record.lesson === id);
        const feedback = verification.analogyFeedbackReview?.lessons?.[id] ??
          (questionFeedback ? { question: questionFeedback[0], ...questionFeedback[1] } : undefined);
        const feedbackReviewed = currentReview(verification.analogyFeedbackReview, feedback, currentHash, verification.lessons?.[id]?.hash);
        const issues = blocks.flatMap(b => b.problems.map(p => `Analogy line ${b.line}: ${p}`)).concat(questionProblems);
        if (reviewed && review.decision !== 'not-needed' && !blocks.length) issues.push('Reviewed as having an analogy but no analogy block exists.');
        if (reviewed && review.decision === 'not-needed' && blocks.length) issues.push('Reviewed as not needing an analogy but an analogy block exists.');
        return {
          id, file: path.relative(root, file), title: source.match(/^title:\s*(.+)$/m)?.[1] ?? id,
          status: reviewed ? 'independently-reviewed' : 'needs-semantic-review',
          ...(reviewed ? { review } : {}),
          feedbackReviewed, ...(feedbackReviewed ? { feedbackReview: feedback } : {}),
          analogyCount: blocks.length, visibleCandidates: candidates, questionCandidates, issues,
          priority: issues.length ? 'format-fix' : candidates.length ? 'review-visible-comparison' : !blocks.length && /^level: basic$/m.test(source) ? 'review-basic-concept' : 'review-concept',
          questions: questions.length,
          formulaBlocks: (source.match(/```formula\b/g) ?? []).length,
        };
      });
      const review = verification.analogyReview;
      const glossaryPath = path.join(modulePath, 'glossary.json');
      modules.push({
        id: mod.id, path: path.relative(root, modulePath), title: mod.title,
        totals: {
          lessons: lessons.length, reviewed: lessons.filter(l => l.status === 'independently-reviewed').length,
          feedbackOnlyReviewed: lessons.filter(l => l.feedbackReviewed && l.status !== 'independently-reviewed').length,
          withAnalogies: lessons.filter(l => l.analogyCount).length,
          questions: lessons.reduce((n,l) => n + l.questions, 0),
          formulaBlocks: lessons.reduce((n,l) => n + l.formulaBlocks, 0),
          glossaryTerms: fs.existsSync(glossaryPath) ? read(glossaryPath).length : 0,
        },
        ...(review ? { review: Object.fromEntries(Object.entries(review).filter(([k]) => k !== 'lessons')) } : {}),
        ...(verification.analogyFeedbackReview ? { feedbackReview: Object.fromEntries(Object.entries(verification.analogyFeedbackReview).filter(([k]) => k !== 'lessons')) } : {}),
        lessons,
      });
    }
    subjects.push({ id: subject.id, title: subject.title, modules });
  }
  const modules = subjects.flatMap(s => s.modules);
  const lessons = modules.flatMap(m => m.lessons);
  return {
    ruleVersion: 1,
    scope: 'All active lessons in module.json and their question fields; archived sources excluded.',
    limitation: 'Candidate detection is heuristic. A missing callout is a review lead, not proof an analogy is useful. Only current, stamped independent reviews count as semantic reviews.',
    totals: {
      subjects: subjects.length, modules: modules.length, lessons: lessons.length,
      questions: lessons.reduce((n,l) => n + l.questions, 0),
      lessonsWithAnalogies: lessons.filter(l => l.analogyCount).length,
      analogyBlocks: lessons.reduce((n,l) => n + l.analogyCount, 0),
      independentlyReviewed: lessons.filter(l => l.status === 'independently-reviewed').length,
      feedbackOnlyReviewed: lessons.filter(l => l.feedbackReviewed && l.status !== 'independently-reviewed').length,
      needsSemanticReview: lessons.filter(l => l.status !== 'independently-reviewed').length,
      visibleComparisonCandidates: lessons.filter(l => l.visibleCandidates.length).length,
      questionComparisonCandidates: lessons.reduce((n,l) => n + l.questionCandidates.length, 0),
      formatIssues: lessons.reduce((n,l) => n + l.issues.length, 0),
    },
    subjects,
  };
}

export function analogySummaryCsv(report) {
  const rows = [['Subject', 'Module', 'Active lessons', 'Questions', 'Lesson formula blocks', 'Glossary terms',
    'Independently reviewed lessons', 'Lessons with analogies', 'Claim groups checked', 'Errors corrected',
    'Feedback-only lessons reviewed', 'Feedback claim groups checked', 'Feedback errors corrected', 'Review gaps', 'New low-confidence areas']];
  for (const subject of report.subjects) for (const mod of subject.modules) {
    const summary = mod.review?.summary;
    rows.push([subject.title, mod.title, mod.totals.lessons, mod.totals.questions, mod.totals.formulaBlocks,
      mod.totals.glossaryTerms, mod.totals.reviewed, mod.totals.withAnalogies,
      summary?.claimsChecked ?? summary?.mappingAndLimitationChecks ?? '', summary?.errorsCorrected ?? '',
      mod.totals.feedbackOnlyReviewed, mod.feedbackReview?.summary?.claimsChecked ?? '', mod.feedbackReview?.summary?.errorsCorrected ?? '',
      [...(mod.review?.gaps ?? ['Semantic analogy review remains outstanding.']), ...(mod.feedbackReview?.gaps ?? [])].join(' | '),
      [...(mod.review?.lowConfidence ?? []), ...(mod.feedbackReview?.lowConfidence ?? [])].map(c => typeof c === 'string' ? c : `${c.lesson}: ${c.claim} (${c.confidence})`).join(' | ')]);
  }
  return rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')).join('\n') + '\n';
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  const report = auditAnalogies();
  const output = args.find(a => !a.startsWith('--'));
  if (output) fs.writeFileSync(path.resolve(output), JSON.stringify(report, null, 2) + '\n');
  if (args.includes('--csv')) process.stdout.write(analogySummaryCsv(report));
  else console.log(JSON.stringify(report.totals, null, 2));
  if (args.includes('--check') && report.totals.formatIssues) process.exitCode = 1;
}
