import fs from 'node:fs';
import path from 'node:path';

const within = (file, directory) => file === directory || file.startsWith(directory + path.sep);

export function linkFiles(contentDirectory, prefix = contentDirectory, { activeOnly = false } = {}) {
  const content = path.resolve(contentDirectory);
  const scope = path.resolve(prefix);
  const candidates = fs.readdirSync(content, { recursive: true }).map(file => path.join(content, file));
  if (!activeOnly) return candidates.filter(file => within(file, scope)
    && /\.(md|json)$/.test(file) && fs.statSync(file).isFile()).sort();

  const files = new Set();
  for (const manifest of candidates.filter(file => path.basename(file) === 'module.json')) {
    const directory = path.dirname(manifest);
    if (!within(directory, scope) && !within(scope, directory)) continue;
    const module = JSON.parse(fs.readFileSync(manifest, 'utf8'));
    if (!Array.isArray(module.lessons)) throw new Error(`Missing lesson list: ${manifest}`);
    for (const id of module.lessons) {
      if (typeof id !== 'string' || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(id))
        throw new Error(`Invalid active lesson ID in ${manifest}`);
      for (const suffix of ['.md', '.questions.json']) {
        const file = path.join(directory, id + suffix);
        if (!within(file, scope)) continue;
        if (!fs.statSync(file).isFile()) throw new Error(`Active lesson file is not a file: ${file}`);
        files.add(file);
      }
    }
  }
  return [...files].sort();
}
