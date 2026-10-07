import { linkTerms } from './glossary.js';
import { findDiagram, renderDiagram } from './diagrams.js';
// Small Markdown renderer for the subset described in CONTENT_SPEC.md.
// Content is authored by us, but we still escape everything and only emit known tags.

const esc = (s) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const safeUrl = (u) => (/^(https?:|mailto:|#)/i.test(u) ? u : '#');

export function inline(text, options = {}) {
  // Pull code spans out first so their contents aren't formatted.
  const codes = [];
  let s = text.replace(/`([^`]+)`/g, (_, c) => {
    codes.push(c);
    return `\u0000${codes.length - 1}\u0000`;
  });
  s = esc(s);
  s = s.replace(/\[([^\]]+)\]\(((?:[^()\s]|\([^()\s]*\))+)\)/g, (_, t, u) =>
    `<a href="${esc(safeUrl(u.replace(/&amp;/g, '&')))}" target="_blank" rel="noopener">${t}</a>`);
  s = s.replace(/\*\*((?:[^*]|\*(?!\*))+)\*\*/g, '<strong>$1</strong>'); // may contain *italic*
  s = s.replace(/(^|[^*\w])\*([^*\s][^*]*?)\*(?!\w)/g, '$1<em>$2</em>');
  s = s.replace(/\u0000(\d+)\u0000/g, (_, i) => `<code>${esc(codes[i])}</code>`);
  return linkTerms(s, options);
}

const LIST_RE = /^(\s*)([-*+]|\d+[.)])\s+(.*)$/;
const CALLOUTS = { note: 'Note', tip: 'Tip', warning: 'Warning', example: 'Example' };

function renderList(lines, options) {
  // lines: [{indent, ordered, text}]
  let html = '';
  const stack = []; // {indent, tag}
  const open = (indent, ordered) => {
    const tag = ordered ? 'ol' : 'ul';
    stack.push({ indent, tag });
    html += `<${tag}><li>`;
  };
  for (const item of lines) {
    const top = stack[stack.length - 1];
    if (!top) open(item.indent, item.ordered);
    else if (item.indent > top.indent) open(item.indent, item.ordered);
    else {
      while (stack.length > 1 && item.indent < stack[stack.length - 1].indent) {
        html += `</li></${stack.pop().tag}>`;
      }
      html += '</li><li>';
    }
    html += inline(item.text, options);
  }
  while (stack.length) html += `</li></${stack.pop().tag}>`;
  return html;
}

function splitRow(line) {
  // Split on unescaped pipes so cells can contain a literal \| (e.g. bitwise OR).
  return line.trim().replace(/^\|/, '').replace(/(?<!\\)\|$/, '')
    .split(/(?<!\\)\|/).map((c) => c.trim().replace(/\\\|/g, '|'));
}

// Compiled illustrations use SVG shapes and connectors. Original text is kept
// only in the copy source and text alternative, never used as the visual drawing.
export function renderExample(source, language = '', { interactive = true } = {}) {
  const definition = findDiagram(source, language);
  const label = definition?.title || (language ? `${language.toUpperCase()} example` : 'Worked example');
  const visual = definition ? renderDiagram(definition) : `<pre><code>${esc(source)}</code></pre>`;
  return `<figure class="example-block ${definition ? 'is-diagram' : 'is-code'}"><figcaption><span class="example-label">${esc(label)}</span>${interactive ? '<span class="example-actions"><button type="button" data-example="copy" aria-label="Copy example">Copy</button><button type="button" data-example="expand" aria-label="Expand example">Expand ↗</button></span>' : ''}</figcaption>${definition && interactive ? `<div class="diagram-hint">${definition.type === 'sequence' ? 'Follow the numbered arrows from top to bottom. ' : ''}${['sequence','graph','memory','matrix'].includes(definition.type) ? 'Scroll sideways or expand to see more.' : 'Expand to zoom. Original text below.'}</div>` : ''}<div class="example-content"${interactive ? ' tabindex="0" role="region" aria-label="Scrollable example"' : ''}>${visual}</div><template class="example-source">${esc(source)}</template>${definition && interactive ? `<details class="example-text"><summary>Text version</summary><pre><code>${esc(source)}</code></pre></details>` : ''}</figure>`;
}

export function render(md, options = {}) {
  if (!md) return '';
  const lines = md.replace(/\r\n?/g, '\n').split('\n');
  let out = '';
  let i = 0;
  let para = [];
  const flush = () => {
    if (para.length) out += `<p>${inline(para.join(' '), options)}</p>`;
    para = [];
  };

  while (i < lines.length) {
    const line = lines[i];

    if (/^\s*```/.test(line)) {
      flush();
      const language = line.trim().slice(3).trim().toLowerCase();
      const body = [];
      i++;
      while (i < lines.length && !/^\s*```/.test(lines[i])) body.push(lines[i++]);
      i++;
      out += renderExample(body.join('\n'), language, options);
      continue;
    }

    const h = line.match(/^(#{2,4})\s+(.*)$/);
    if (h) {
      flush();
      const level = Math.min(h[1].length, 4);
      out += `<h${level}>${inline(h[2], options)}</h${level}>`;
      i++;
      continue;
    }

    if (/^\s*\|/.test(line) && i + 1 < lines.length && /^\s*\|?\s*:?-{2,}/.test(lines[i + 1])) {
      flush();
      const head = splitRow(line);
      i += 2;
      const rows = [];
      while (i < lines.length && /^\s*\|/.test(lines[i])) rows.push(splitRow(lines[i++]));
      out += `<div class="table-wrap"${options.interactive === false ? '' : ' tabindex="0" role="region" aria-label="Scrollable table"'}><table><thead><tr>` +
        head.map((c) => `<th>${inline(c, options)}</th>`).join('') + '</tr></thead><tbody>' +
        rows.map((r) => '<tr>' + r.map((c) => `<td>${inline(c, options)}</td>`).join('') + '</tr>').join('') +
        '</tbody></table></div>';
      continue;
    }

    if (/^\s*>/.test(line)) {
      flush();
      const body = [];
      while (i < lines.length && /^\s*>/.test(lines[i])) body.push(lines[i++].replace(/^\s*>\s?/, ''));
      const tag = body[0]?.match(/^\[!(\w+)\]\s*(.*)$/);
      let kind = 'quote';
      let title = '';
      if (tag && CALLOUTS[tag[1].toLowerCase()]) {
        kind = tag[1].toLowerCase();
        title = tag[2] || CALLOUTS[kind];
        body.shift();
      }
      out += `<aside class="callout callout-${kind}">` +
        (title ? `<div class="callout-title">${inline(title, options)}</div>` : '') +
        render(body.join('\n'), options) + '</aside>';
      continue;
    }

    if (LIST_RE.test(line)) {
      flush();
      const items = [];
      while (i < lines.length) {
        const m = lines[i].match(LIST_RE);
        if (m) {
          items.push({ indent: m[1].replace(/\t/g, '  ').length, ordered: /\d/.test(m[2]), text: m[3] });
          i++;
        } else if (/^\s{2,}\S/.test(lines[i]) && items.length) {
          items[items.length - 1].text += ' ' + lines[i].trim(); // continuation line
          i++;
        } else break;
      }
      out += renderList(items, options);
      continue;
    }

    if (/^\s*$/.test(line)) {
      flush();
      i++;
      continue;
    }
    if (/^\s*(---|\*\*\*)\s*$/.test(line)) {
      flush();
      out += '<hr>';
      i++;
      continue;
    }
    para.push(line.trim());
    i++;
  }
  flush();
  return out;
}

export function plainText(md) {
  return (md || '')
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/^\s*(#+|>|[-*+]|\d+[.)])\s+/gm, '')
    .replace(/\[!\w+\]/g, '')
    .replace(/[*`|]+/g, '')
    .replace(/\s+([,.;:!?])/g, '$1')
    .replace(/\s+/g, ' ');
}
