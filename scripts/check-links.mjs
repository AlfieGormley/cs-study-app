#!/usr/bin/env node
// Checks every URL in content/ still loads. Usage: node scripts/check-links.mjs [path-prefix] [json-report]
import fs from 'node:fs';
import path from 'node:path';
import { glossary } from '../glossary-data.js';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const prefix = path.resolve(process.argv[2] || path.join(root, 'content'));
const files = fs.readdirSync(path.join(root, 'content'), { recursive: true })
  .map((f) => path.join(root, 'content', f))
  .filter((f) => f.startsWith(prefix) && /\.(md|json)$/.test(f));

const urls = new Map(); // url -> [files]
for (const f of files) {
  // Only real links: Markdown [text](url) (one level of brackets allowed) and JSON "url" fields.
  const text = fs.readFileSync(f, 'utf8');
  const found = [
    ...[...text.matchAll(/\]\((https?:\/\/(?:[^()\s"]|\([^()\s"]*\))+)\)/g)].map((m) => m[1]),
    ...[...text.matchAll(/"url"\s*:\s*"(https?:\/\/[^"]+)"/g)].map((m) => m[1]),
  ];
  for (const u of found) {
    if (/^https?:\/\/([\w-]+\.)*(example\.(com|org|net)|localhost)\b/.test(u)) continue; // placeholders
    if (!urls.has(u)) urls.set(u, new Set());
    urls.get(u).add(path.relative(root, f));
  }
}

// The dictionary is another source of user-facing external reading links.
if (prefix === path.join(root, 'content')) {
  for (const entry of glossary) {
    if (!entry.source) continue;
    if (!urls.has(entry.source)) urls.set(entry.source, new Set());
    urls.get(entry.source).add('glossary-data.js');
  }
}

const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15';
async function check(u) {
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const r = await fetch(u, { redirect: 'follow', headers: { 'user-agent': UA }, signal: AbortSignal.timeout(20000) });
      if (r.ok) return r.status;
      if (![429, 500, 502, 503, 504].includes(r.status)) return r.status;
    } catch (e) {
      if (attempt === 2) return e.name;
    }
    await new Promise((res) => setTimeout(res, 2000 * (attempt + 1)));
  }
  return 'retries exhausted';
}

const list = [...urls.keys()];
const bad = [];
const results = [];
let next = 0;
await Promise.all(Array.from({ length: 6 }, async () => {
  while (next < list.length) {
    const u = list[next++];
    const status = await check(u);
    results.push({ url: u, status, files: [...urls.get(u)] });
    if (!(Number.isInteger(status) && status >= 200 && status < 300)) bad.push({ u, status });
  }
}));
if (process.argv[3]) fs.writeFileSync(path.resolve(process.argv[3]), JSON.stringify({
  checkedAt: new Date().toISOString(), scope: 'URL accessibility only; not factual corroboration',
  total: list.length, failures: bad.length,
  results: results.sort((a, b) => a.url.localeCompare(b.url)),
}, null, 2) + '\n');
console.log(`${list.length} unique URLs checked, ${bad.length} failing`);
for (const { u, status } of bad) console.log(`  ${status}  ${u}\n         in ${[...urls.get(u)].join(', ')}`);
process.exit(bad.length ? 1 : 0);
