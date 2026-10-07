#!/usr/bin/env node
// Records the current lesson hashes in a module's verification.json.
// Run ONLY at the end of an independent verification pass (docs/CONTENT_PROCESS.md, step 4).
//   node scripts/stamp-verification.mjs content/<subject>/<module-dir>
import fs from 'node:fs';
import path from 'node:path';
import { checkVerification, lessonHash } from './verification.mjs';

const dir = process.argv[2];
if (!dir) {
  console.error('usage: node scripts/stamp-verification.mjs content/<subject>/<module-dir>');
  process.exit(1);
}
const modulePath = path.resolve(dir);
const mod = JSON.parse(fs.readFileSync(path.join(modulePath, 'module.json'), 'utf8'));
const problems = checkVerification(modulePath, mod, { ignoreHashes: true });
if (problems.length) {
  console.error('✗ verification record incomplete, not stamping:\n  ' + problems.join('\n  '));
  process.exit(1);
}
const file = path.join(modulePath, 'verification.json');
const v = JSON.parse(fs.readFileSync(file, 'utf8'));
for (const id of mod.lessons) v.lessons[id].hash = lessonHash(modulePath, id);
fs.writeFileSync(file, JSON.stringify(v, null, 2) + '\n');
console.log(`✓ stamped ${mod.lessons.length} lesson(s) in ${path.relative(process.cwd(), file)}`);
