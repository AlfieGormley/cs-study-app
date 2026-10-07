// Stable keys let lessons and questions share the same compiled illustration.
export function diagramKey(source, language = '') {
  let hash = 2166136261;
  for (const c of `${language}\n${source}`) {
    hash ^= c.codePointAt(0);
    hash = Math.imul(hash, 16777619);
  }
  return `d${(hash >>> 0).toString(16)}-${source.length}`;
}
