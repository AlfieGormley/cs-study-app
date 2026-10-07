import { diagramKey } from './diagram-key.js';
let catalogue = {};
let cataloguePromise;
export function loadDiagrams() {
  return cataloguePromise ??= import('./diagram-catalog.js').then((module) => {
    catalogue = module.default;
  }).catch((error) => { cataloguePromise = null; throw error; });
}

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const number = (n) => Math.round(n * 100) / 100;
const wrap = (text, max = 24) => String(text).split('\n').flatMap((paragraph) => {
  const lines = []; let current = '';
  for (const word of paragraph.split(/\s+/)) {
    if (current && (current + ' ' + word).length > max) { lines.push(current); current = word; }
    else current += (current ? ' ' : '') + word;
  }
  return [...lines, current];
});
const text = (value, x, y, { width = 200, anchor = 'middle', cls = '', size = 14 } = {}) => {
  const lines = wrap(value, Math.max(8, Math.floor(width / (size * .55))));
  return `<text class="dv-label ${cls}" text-anchor="${anchor}" font-size="${size}" x="${number(x)}" y="${number(y - (lines.length - 1) * 10)}">${lines.map((l,i) => `<tspan x="${number(x)}" dy="${i ? 20 : 0}">${esc(l)}</tspan>`).join('')}</text>`;
};
const rect = (x,y,w,h,cls='dv-node',rx=12) => `<rect class="${cls}" x="${number(x)}" y="${number(y)}" width="${number(w)}" height="${number(h)}" rx="${rx}"/>`;
const line = (x1,y1,x2,y2,cls='dv-edge') => `<path class="${cls}" d="M${number(x1)},${number(y1)} L${number(x2)},${number(y2)}"/>`;
function arrowhead(x,y,direction) {
  const points = { right:[[x-7,y-4],[x+1,y],[x-7,y+4]], left:[[x+7,y-4],[x-1,y],[x+7,y+4]], down:[[x-4,y-7],[x,y+1],[x+4,y-7]], up:[[x-4,y+7],[x,y-1],[x+4,y+7]] }[direction];
  return `<polygon class="dv-arrow" points="${points.map((p)=>p.map(number).join(',')).join(' ')}"/>`;
}
function layout(d) {
  const backgrounds=[], strokes=[], heads=[];
  for (const p of d.primitives) {
    if (p.kind === 'box' || p.kind === 'cell') backgrounds.push(rect(p.x,p.y,p.width,p.height,p.kind === 'box' ? 'dv-area' : 'dv-cell',p.kind === 'box' ? 0 : 5));
    if (p.kind === 'line') strokes.push(line(p.x1,p.y1,p.x2,p.y2));
    if (p.kind === 'arrow') heads.push(arrowhead(p.x,p.y,p.direction));
    if (p.kind === 'circle') heads.push(`<circle class="${p.open ? 'dv-dot-open' : 'dv-dot'}" cx="${p.x}" cy="${p.y}" r="${p.r}"/>`);
  }
  const labels=d.labels.map((l) => `<text class="dv-grid-label" x="${l.x}" y="${l.y}" textLength="${[...l.text].length * 10}" lengthAdjust="spacingAndGlyphs">${esc(l.text)}</text>`).join('');
  return { width:d.width,height:d.height,body:backgrounds.join('')+strokes.join('')+heads.join('')+labels };
}
function flow(d) {
  const w=420, gap=102, top=24;
  const body=d.steps.map((step,i)=>{
    const y=top+i*gap;
    return (i ? line(w/2,y-30,w/2,y-8)+arrowhead(w/2,y-5,'down') : '') + rect(28,y,w-56,72) + rect(42,y+23,26,26,'dv-step',8)+text(String(i+1),55,y+41,{size:12})+text(step,84,y+40,{width:w-120,anchor:'start'});
  }).join('');
  return {width:w,height:top*2+gap*(d.steps.length-1)+72,body};
}
function sequence(d) {
  const gap=190, margin=100;
  const selfAtEnd=d.messages.some(m=>m.from===m.to&&m.from===d.participants.at(-1).id);
  const width=margin*2+gap*(d.participants.length-1)+(selfAtEnd?100:0);
  const headerY=26, headerH=64, messageTop=148, step=90;
  const positions=new Map(d.participants.map((p,i)=>[p.id,margin+i*gap]));
  const height=messageTop+step*d.messages.length+20;
  let body=d.participants.map((p)=>{
    const x=positions.get(p.id);
    return line(x,headerY+headerH,x,height-24,'dv-lifeline')+rect(x-80,headerY,160,headerH)+text(p.label,x,headerY+37,{width:144});
  }).join('');
  d.messages.forEach((m,i)=>{
    const x1=positions.get(m.from),x2=positions.get(m.to),y=messageTop+i*step;
    if (x1===x2) {
      body+=`<path class="dv-edge" d="M${x1},${y-16} h48 v30 h-48"/>`+arrowhead(x1,y+14,'left');
      body+=rect(x1+8,y-48,160,26,'dv-edge-label',6)+text(m.label,x1+16,y-30,{width:155,anchor:'start',size:12});
    } else {
      body+=line(x1,y,x2,y,m.kind==='return'?'dv-edge dv-return':'dv-edge')+arrowhead(x2,y,x2>x1?'right':'left');
      const labelWidth=Math.min(Math.abs(x2-x1)-16,Math.max(120,m.label.length*7));
      const labelLines=wrap(m.label,Math.floor(labelWidth/7));
      body+=rect((x1+x2-labelWidth)/2,y-14-labelLines.length*20,labelWidth,labelLines.length*20+4,'dv-edge-label',6);
      body+=text(m.label,(x1+x2)/2,y-4-labelLines.length*10,{width:labelWidth-8,size:12});
    }
    body+=`<circle class="dv-step" cx="28" cy="${y-2}" r="12"/>`+text(String(i+1),28,y+2,{size:11});
  });
  return {width,height,body};
}
function graph(d) {
  const nodes=d.nodes.map(n=>({...n,w:n.width||156,h:n.height||68}));
  const map=new Map(nodes.map(n=>[n.id,n]));
  const width=Math.max(...nodes.map(n=>n.x+n.w))+28;
  const height=Math.max(...nodes.map(n=>n.y+n.h))+28;
  let edges='';
  const port=(n,p)=>({top:[n.x+n.w/2,n.y],bottom:[n.x+n.w/2,n.y+n.h],left:[n.x,n.y+n.h/2],right:[n.x+n.w,n.y+n.h/2]})[p];
  for(const e of d.edges){
    const a=map.get(e.from),b=map.get(e.to);
    const dx=b.x-a.x,dy=b.y-a.y;
    const vertical=Math.abs(dy)>Math.abs(dx);
    const from=e.fromPort||(vertical?(dy>=0?'bottom':'top'):(dx>=0?'right':'left'));
    const to=e.toPort||(vertical?(dy>=0?'top':'bottom'):(dx>=0?'left':'right'));
    const start=port(a,from),end=port(b,to);
    let points=[start,...(e.via||[]),end];
    if(!e.via && d.type!=='tree' && start[0]!==end[0] && start[1]!==end[1]) {
      if(from==='top'||from==='bottom') {const y=(start[1]+end[1])/2;points=[start,[start[0],y],[end[0],y],end];}
      else {const x=(start[0]+end[0])/2;points=[start,[x,start[1]],[x,end[1]],end];}
    }
    edges+=`<path class="dv-edge${e.dashed?' dv-return':''}" d="${points.map((p,i)=>(i?'L':'M')+p.map(number).join(',')).join(' ')}"/>`;
    if(e.directed!==false) edges+=arrowhead(end[0],end[1],{left:'right',right:'left',top:'down',bottom:'up'}[to]);
    if(e.label){
      const x=e.labelX??(start[0]+end[0])/2,y=e.labelY??(start[1]+end[1])/2-8;
      const w=Math.min(170,e.label.length*7+16);
      edges+=rect(x-w/2,y-17,w,26,'dv-edge-label',5)+text(e.label,x,y,{width:w-8,size:12});
    }
  }
  const boxes=nodes.map(n=>rect(n.x,n.y,n.w,n.h,n.tone==='muted'?'dv-node dv-muted':'dv-node')+text(n.label,n.x+n.w/2,n.y+n.h/2+5,{width:n.w-22})).join('');
  return {width,height,body:edges+boxes};
}
function memory(d) {
  const width=d.width||640, labelWidth=120, top=24, gap=84;
  const body=d.rows.map((row,i)=>{
    const y=top+i*gap,available=width-labelWidth-48;
    const rowTotal=(r)=>r.cells.reduce((sum,c)=>sum+(c.weight||1),0)+(r.offset||0);
    const total=d.sharedScale?Math.max(...d.rows.map(rowTotal)):rowTotal(row);let x=labelWidth+24+available*(row.offset||0)/total;
    let out=text(row.label,24,y+34,{anchor:'start',width:labelWidth-12,size:13});
    for(const cell of row.cells){const w=available*(cell.weight||1)/total;out+=rect(x,y,w-3,60,`dv-node${cell.tone==='muted'?' dv-muted':''}`,8)+text(cell.label,x+(w-3)/2,y+34,{width:w-15,size:13});x+=w;}
    return out;
  }).join('');
  return {width,height:top*2+gap*d.rows.length-24,body};
}
function matrix(d) {
  const width=580,label=130,cw=(width-label-24)/d.columns.length,rh=104;
  let body=d.columns.map((c,i)=>text(c,label+cw*(i+.5),36,{width:cw-16,size:13})).join('');
  d.rows.forEach((row,r)=>{
    body+=text(row,20,100+r*rh,{anchor:'start',width:label-30,size:13});
    d.cells[r].forEach((cell,c)=>{body+=rect(label+c*cw,64+r*rh,cw-8,rh-10,'dv-node',10)+text(cell,label+cw*(c+.5)-4,113+r*rh,{width:cw-26});});
  });
  return {width,height:74+rh*d.rows.length,body};
}
function describe(d) {
  if (d.description) return d.description;
  if (d.type === 'sequence') {
    const names = new Map(d.participants.map(p => [p.id,p.label]));
    return d.messages.map((m,i) => `${i+1}. ${names.get(m.from)}${m.from===m.to?':':' to '+names.get(m.to)+':'} ${m.label}.`).join(' ');
  }
  if (d.type === 'graph' || d.type === 'tree') {
    const names = new Map(d.nodes.map(n => [n.id,n.label]));
    return d.edges.map(e => `${names.get(e.from)} ${e.directed===false?'connects to':'leads to'} ${names.get(e.to)}${e.label?' ('+e.label+')':''}.`).join(' ');
  }
  if (d.type === 'flow') return d.steps.map((s,i)=>`${i+1}. ${s}`).join('. ');
  if (d.type === 'memory') return d.rows.map(r=>`${r.label}: ${r.cells.map(c=>c.label).join(', ')}.`).join(' ');
  if (d.type === 'matrix') return d.rows.flatMap((r,i)=>d.columns.map((c,j)=>`${r}, ${c}: ${d.cells[i][j]}.`)).join(' ');
  return d.source || '';
}
export function renderDiagram(definition) {
  const result=({layout,flow,sequence,graph,tree:graph,memory,matrix})[definition.type](definition);
  const {width,height,body}=result;
  const id=definition.type;
  return `<svg class="vector-diagram dv-${id}" data-diagram-type="${id}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" style="--diagram-width:${width}px" role="img" aria-label="${esc(definition.title||'Diagram')}"><title>${esc(definition.title||'Diagram')}</title><desc>${esc(describe(definition))}</desc>${body}</svg>`;
}
export function findDiagram(source,language='') {
  const d=catalogue[diagramKey(source,language)];
  return d?.source===source ? d : language==='flow' ? {type:'flow',title:'Process flow',steps:source.trim().split('\n'),source} : null;
}
