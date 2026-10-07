// Compile drawings into actual vector primitives. Geometry is preserved rather
// than guessing new relationships from ambiguous ASCII layouts.
import { diagramKey } from '../diagram-key.js';
export { diagramKey };

const H = '-─━═=';
const V = '|│┃║';
const J = '+┌┐└┘├┤┬┴┼╭╮╰╯╔╗╚╝╠╣╦╩╬';
const h = (c) => !!c && H.includes(c);
const v = (c) => !!c && V.includes(c);
const j = (c) => !!c && J.includes(c);
const arrows = '→←↑↓▶◀▲▼►◄';
const isSpace = (c) => !c || /\s/.test(c);

// Promote unambiguous trees into connected nodes. Complex comparisons or
// annotated forests retain their exact vector layout instead of guessing.
export function compileTree(source) {
  const rows = source.split('\n');
  if (!rows.some((r) => /[/\\]/.test(r)) || rows.some((r) => !r.trim())) return null;
  const levels = new Map(), edgeRows = [];
  for (let r=0;r<rows.length;r++) {
    const line=rows[r];
    if (/^[\s/\\|]+$/.test(line)) {edgeRows.push(r);continue;}
    const tokens=[...line.matchAll(/\S+/g)];
    if (!tokens.length || tokens.some((t)=>!/^[-\w*+()."']{1,12}$/.test(t[0]))) return null;
    levels.set(r,tokens.map((t,i)=>({id:`r${r}n${i}`,label:t[0],center:t.index+t[0].length/2,row:r})));
  }
  const nodes=[...levels.values()].flat(), edges=[];
  if (!nodes.length || levels.get(0)?.length!==1 || !edgeRows.length) return null;
  const nearest=(list,target,direction)=>{
    const eligible=list.filter(n=>direction===0 || direction>0 && n.center>=target-.75 || direction<0 && n.center<=target+.75).sort((a,b)=>Math.abs(a.center-target)-Math.abs(b.center-target));
    if (!eligible.length || eligible.length>1 && Math.abs(Math.abs(eligible[0].center-target)-Math.abs(eligible[1].center-target))<.1) return null;
    return eligible[0];
  };
  for (const r of edgeRows) {
    const parents=levels.get(r-1),children=levels.get(r+1);
    if (!parents||!children) return null;
    for (const m of rows[r].matchAll(/[/\\|]/g)) {
      const dir=m[0]==='/'?1:m[0]==='\\'?-1:0;
      const parent=nearest(parents,m.index+.5,dir),child=nearest(children,m.index+.5,-dir);
      if (!parent||!child) return null;
      edges.push({from:parent.id,to:child.id,fromPort:'bottom',toPort:'top',directed:false});
    }
  }
  const childIds=new Set(edges.map(e=>e.to));
  if (edges.length!==nodes.length-1 || childIds.size!==edges.length || nodes.slice(1).some(n=>!childIds.has(n.id))) return null;
  const left=Math.min(...nodes.map(n=>n.center));
  return {type:'tree',title:'Tree diagram',nodes:nodes.map(n=>({id:n.id,label:n.label,x:28+(n.center-left)*28,y:28+n.row*58,width:Math.max(52,n.label.length*10+20),height:46})),edges};
}

export function compileDrawing(source, language = '') {
  if (language === 'flow') return { type: 'flow', title: 'Process flow', steps: source.trim().split('\n') };
  if (language && language !== 'diagram') return null;
  const lines = source.replace(/\t/g, '    ').split('\n').map((l) => [...l]);
  const at = (r, c) => lines[r]?.[c] || '';
  const count = Math.max(...lines.map((l) => l.length), 0);
  if (!count) return null;
  const structural = /[┌┐└┘├┤│─┬┴╭╮╰╯]|\+[-─]{2,}|(?:^|\n)\s*\|/.test(source);
  // Mixed drawings may contain code labels; only reject programs when there
  // is no actual box/connector structure. Assembly uses brackets as operands.
  if (!structural && language !== 'diagram' && /^(?:\s*)(?:def |class |if |for |while |return |SELECT |FROM |UPDATE |INSERT |const |let |#include|\$ |EXPLAIN |(?:Hash|Merge|Nested Loop) Join|Seq Scan|Index .*Scan|(?:mov|ldr|str|lea|xor|cmp|jmp|stp|ldp)\s+\w)/m.test(source)) return null;
  if (/^<<<<<<< |^>>>>>>> |^>>> /m.test(source)) return null;
  const tree = compileTree(source);
  if (tree) return tree;
  const diagonals = lines.filter((l) => /^\s*[\/\\](?:[\s\/\\]*[\/\\])?\s*$/.test(l.join(''))).length;
  const horizontalArrow = /(?:-{1,}|─+|═+)>|<[-─]+|[→←▶◀]/.test(source);
  if (!structural && !diagonals && language !== 'diagram' && /^[ \t]*(?:[\w.]+(?:\[[^\n]*\])?|[eθμσwv][·\w]*)\s+=/m.test(source)) return null;
  const bracketRows = lines.filter((l) => /\[[^\[\]]*\]/.test(l.join(''))).length >= 2;
  // Keep mathematical implication/assignment chains as equations unless they
  // also contain an explicit diagram structure.
  if (!structural && !diagonals && !bracketRows && language !== 'diagram') {
    if (!horizontalArrow || /[≡∧∨¬∀∃θμσ]|\b(?:Pr|log|sin|cos)\b|\d\s*(?:<=|>=|≤|≥)|(?:^|\n).*\s=\s/m.test(source)) return null;
  }
  if (!source.includes('\n')) {
    const chain = source.trim().split(/\s*(?:-->|->|→|─+▶)\s*/);
    if (chain.length > 1 && chain.length <= 8 && chain.every((n) => n && n.length <= 36 && !/[<>{};=]/.test(n))) {
      const vertical = chain.length > 4;
      return { type: 'graph', title: 'Flow diagram', nodes: chain.map((label,i) => ({id:String(i),label,x:vertical?28:28+i*212,y:vertical?28+i*112:28,width:160,height:68})), edges:chain.slice(1).map((_,i)=>({from:String(i),to:String(i+1)})) };
    }
  }
  const cw = 10, ch = 26, pad = 28;
  const used = lines.map((l) => l.map(() => false));
  const primitives = [];
  const labels = [];
  const x = (c) => pad + (c + .5) * cw;
  const y = (r) => pad + (r + .5) * ch;
  const use = (r, c) => { if (used[r]?.[c] !== undefined) used[r][c] = true; };
  const line = (x1, y1, x2, y2) => primitives.push({ kind: 'line', x1, y1, x2, y2 });
  const arrow = (r, c, direction) => {
    primitives.push({ kind: 'arrow', x: x(c), y: y(r), direction }); use(r, c);
  };
  // Closed boxes get a real surface. Borders remain faithful to the original
  // grid, including nested regions and boxes sharing an edge.
  for (let r = 0; r < lines.length; r++) {
    const row = lines[r].join('');
    for (const m of row.matchAll(/[+┌╭╔]([-─━═]{2,})[+┐╮╗]/g)) {
      const left = m.index, right = left + m[0].length - 1;
      for (let bottom = r + 2; bottom < lines.length; bottom++) {
        if (j(at(bottom, left)) && j(at(bottom, right)) && lines[bottom].slice(left + 1, right).every(h)) {
          if (Array.from({ length: bottom - r - 1 }, (_, n) => r + n + 1).every((rr) => (v(at(rr, left)) || j(at(rr, left))) && (v(at(rr, right)) || j(at(rr, right)))))
            primitives.push({ kind: 'box', x: x(left), y: y(r), width: (right - left) * cw, height: (bottom - r) * ch });
          break;
        }
      }
    }
  }
  // Bracketed slots are drawn as cells, not bracket glyphs. Preserve the labels
  // inside them, including ordering, counts, annotations and empty slots.
  for (let r = 0; r < lines.length; r++) {
    for (const m of lines[r].join('').matchAll(/\[([^\[\]\n]*)\]/g)) {
      if (m[1].includes('"') || /\b(?:i|j|idx)\b/.test(m[1]) && /\w\[/.test(lines[r].join(''))) continue;
      const left = m.index, right = left + m[0].length - 1;
      primitives.push({ kind: 'cell', x: x(left) - cw / 2 + 1, y: y(r) - 11, width: (right - left + 1) * cw - 2, height: 22 });
      use(r, left); use(r, right);
    }
  }
  for (let r = 0; r < lines.length; r++) for (let c = 0; c < lines[r].length; c++) {
    if (used[r][c]) continue;
    const char = at(r, c), left = at(r, c - 1), right = at(r, c + 1), up = at(r - 1, c), down = at(r + 1, c);
    if (h(char) && (char === '=' ? at(r,c+2) === '=' || at(r,c-2) === '=' : char !== '-' || h(left) || h(right) || j(left) || j(right) || '<←◀'.includes(left || ' ') || '>→▶'.includes(right || ' '))) {
      let end = c;
      while (h(at(r, end + 1))) end++;
      line(x(c) - cw / 2, y(r), x(end) + cw / 2, y(r));
      for (let cc = c; cc <= end; cc++) use(r, cc);
      c = end;
    } else if (v(char) && (structural || v(up) || v(down) || j(up) || j(down) || isSpace(left) && isSpace(right))) {
      // A pipe between text cells remains a divider, as in packet layouts.
      line(x(c), y(r) - ch / 2, x(c), y(r) + ch / 2); use(r, c);
    } else if (j(char)) {
      const L = h(left) || j(left), R = h(right) || j(right);
      const U = v(up) || j(up), D = v(down) || j(down);
      const ports = {
        '┌': [0,1,0,1], '╭': [0,1,0,1], '╔': [0,1,0,1], '┐': [1,0,0,1], '╮': [1,0,0,1], '╗': [1,0,0,1],
        '└': [0,1,1,0], '╰': [0,1,1,0], '╚': [0,1,1,0], '┘': [1,0,1,0], '╯': [1,0,1,0], '╝': [1,0,1,0],
        '├': [0,1,1,1], '┤': [1,0,1,1], '┬': [1,1,0,1], '┴': [1,1,1,0], '┼': [1,1,1,1],
      }[char] || [L,R,U,D];
      if (ports.some(Boolean)) {
        if (ports[0]) line(x(c) - cw / 2, y(r), x(c), y(r));
        if (ports[1]) line(x(c), y(r), x(c) + cw / 2, y(r));
        if (ports[2]) line(x(c), y(r) - ch / 2, x(c), y(r));
        if (ports[3]) line(x(c), y(r), x(c), y(r) + ch / 2);
        use(r,c);
      }
    } else if ((char === '>' && h(left)) || '→▶►'.includes(char)) {
      if ('→▶►'.includes(char)) line(x(c) - cw / 2, y(r), x(c), y(r));
      arrow(r,c,'right');
    } else if ((char === '<' && h(right)) || '←◀◄'.includes(char)) {
      if ('←◀◄'.includes(char)) line(x(c), y(r), x(c) + cw / 2, y(r));
      arrow(r,c,'left');
    } else if ('↓▼'.includes(char) || char === 'v' && isSpace(left) && isSpace(right) && (v(up) || j(up) || /^\s*v\s*$/.test(lines[r].join('')))) {
      line(x(c), y(r) - ch / 2, x(c), y(r)); arrow(r,c,'down');
    } else if ('↑▲'.includes(char) || char === '^' && (left === '^' || right === '^' || isSpace(left) && isSpace(right) && (v(down) || j(down) || v(up) || !lines[r].slice(0,c).join('').trim()))) {
      line(x(c), y(r), x(c), y(r) + ch / 2); arrow(r,c,'up');
    } else if ((char === '/' || char === '\\') && (isSpace(left) || left === '\\' || left === '/') && (isSpace(right) || right === '/' || right === '\\')) {
      const slope = char === '/' ? -1 : 1;
      line(x(c) - cw / 2, y(r) - slope * ch / 2, x(c) + cw / 2, y(r) + slope * ch / 2); use(r,c);
    } else if ('●○•'.includes(char)) {
      primitives.push({ kind: 'circle', x: x(c), y: y(r), r: char === '•' ? 2.8 : 4.5, open: char === '○' });use(r,c);
    }
  }
  const meaningful = primitives.filter((p) => p.kind !== 'box' && p.kind !== 'cell');
  if (!meaningful.length && !primitives.length) return null;
  // Text fragments contain labels only; the source's drawing characters have
  // been replaced with paths and shapes. No full-line ASCII SVG text is used.
  for (let r = 0; r < lines.length; r++) {
    let c = 0;
    while (c < lines[r].length) {
      if (used[r][c] || isSpace(at(r,c))) { c++; continue; }
      const start = c;
      while (c < lines[r].length && !used[r][c] && !(isSpace(at(r,c)) && isSpace(at(r,c+1)))) c++;
      const text = lines[r].slice(start,c).join('').trimEnd();
      if (text) labels.push({ x: pad + start * cw, y: y(r) + 5, text, row: r, column: start });
    }
  }
  return { type: 'layout', title: 'Diagram', width: count * cw + pad * 2, height: lines.length * ch + pad * 2, primitives, labels };
}

export function validateDiagram(d) {
  if (!d || !['layout','sequence','graph','tree','memory','flow','matrix'].includes(d.type)) throw new Error('Unknown diagram type');
  if (d.type === 'sequence') {
    const ids = new Set(d.participants.map((p) => p.id));
    if (ids.size !== d.participants.length || ids.size < 2) throw new Error('Invalid sequence participants');
    for (const m of d.messages) if (!ids.has(m.from) || !ids.has(m.to) || !m.label) throw new Error('Invalid sequence message');
  }
  if (d.type === 'graph' || d.type === 'tree') {
    const ids = new Set(d.nodes.map((n) => n.id));
    if (ids.size !== d.nodes.length || !ids.size) throw new Error('Invalid graph nodes');
    for (const n of d.nodes) if (!n.label || !Number.isFinite(n.x) || !Number.isFinite(n.y)) throw new Error('Invalid graph node');
    for (const e of d.edges) if (!ids.has(e.from) || !ids.has(e.to)) throw new Error('Invalid graph edge');
  }
  if (d.type === 'flow' && (!d.steps?.length || d.steps.some((s) => !s.trim()))) throw new Error('Invalid flow');
  if (d.type === 'layout') {
    if (d.width <= 0 || d.height <= 0 || !d.primitives.length) throw new Error('Empty layout');
    const kinds = new Set(['line','arrow','box','cell','circle']);
    for (const p of d.primitives) if (!kinds.has(p.kind)) throw new Error('Unknown primitive');
    for (const label of d.labels) if (!label.text || !Number.isFinite(label.x) || !Number.isFinite(label.y)) throw new Error('Invalid label');
  }
  if (d.type === 'memory' && !d.rows?.length) throw new Error('Empty memory layout');
  if (d.type === 'matrix' && (!d.rows?.length || d.cells.length !== d.rows.length || d.cells.some((r) => r.length !== d.columns.length))) throw new Error('Invalid matrix');
}

export function* extractExamples(text) {
  const lines=text.replace(/\r\n?/g,'\n').split('\n');
  let i=0;
  while(i<lines.length){
    if (/^\s*```/.test(lines[i])) {
      const language=lines[i].trim().slice(3).trim().toLowerCase(),body=[];i++;
      while(i<lines.length&&!/^\s*```/.test(lines[i]))body.push(lines[i++]);
      i++;yield {language,source:body.join('\n')};
    } else if (/^\s*>/.test(lines[i])) {
      const body=[];
      while(i<lines.length&&/^\s*>/.test(lines[i]))body.push(lines[i++].replace(/^\s*>\s?/,''));
      yield* extractExamples(body.join('\n'));
    } else i++;
  }
}

export function compileCatalogue(outputs, overrides = []) {
  const catalogue = {}, occurrences = [], seenOverrides = new Set();
  let scanned = 0;
  const bySource = new Map(overrides.map((o) => [o.source,o]));
  if (bySource.size !== overrides.length) throw new Error('Duplicate diagram override source');
  const visit = (text, location) => {
    let block = 0;
    for (const { language, source } of extractExamples(text)) {
      block++; scanned++;
      const override = bySource.get(source);
      if (override) seenOverrides.add(override.id);
      const diagram = override?.diagram || compileDrawing(source,override?.mode === 'layout' ? 'diagram' : language);
      if (!diagram) {
        if (language === 'diagram') throw new Error(`Uncompiled explicit diagram: ${location.lesson} ${location.field} block ${block}`);
        continue;
      }
      validateDiagram(diagram);
      const key = diagramKey(source,language);
      if (catalogue[key] && catalogue[key].source !== source) throw new Error(`Diagram key collision: ${key}`);
      catalogue[key] = { source, ...diagram, ...(override ? { title: override.title, reviewed: true } : {}) };
      occurrences.push({ key, type: diagram.type, ...location, block, reviewed: !!override });
    }
  };
  for (const [file, mod] of Object.entries(outputs)) {
    if (!mod.lessons) continue;
    for (const l of mod.lessons) {
      const location = { subject: mod.subject, module: mod.id, lesson: l.id };
      visit(l.body, { ...location, field: 'lesson' });
      for (const q of l.questions) {
        visit(q.prompt, { ...location, question: q.id, field: 'prompt' });
        visit(q.workedExample, { ...location, question: q.id, field: 'workedExample' });
        q.options.forEach((o,i) => { visit(o.text, { ...location, question:q.id, field:`options.${i}.text` }); visit(o.explanation, { ...location, question:q.id, field:`options.${i}.explanation` }); });
      }
    }
  }
  for (const o of overrides) if (!seenOverrides.has(o.id)) throw new Error(`Unmatched diagram override: ${o.id}`);
  return { catalogue, report: { version: 1, scanned, textExamples: scanned - occurrences.length, unique: Object.keys(catalogue).length, occurrences: occurrences.length, reviewed: occurrences.filter((o) => o.reviewed).length, byType: occurrences.reduce((a,o) => ({...a,[o.type]:(a[o.type]||0)+1}),{}), diagrams: occurrences } };
}
