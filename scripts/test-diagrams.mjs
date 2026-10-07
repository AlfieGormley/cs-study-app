import test from 'node:test';
import assert from 'node:assert/strict';
import { compileDrawing, compileTree, validateDiagram, extractExamples, compileCatalogue } from './diagram-compiler.mjs';
import { findDiagram, renderDiagram } from '../diagrams.js';
import catalogue from '../diagram-catalog.js';
import fs from 'node:fs';

const overrides=JSON.parse(fs.readFileSync(new URL('../content/diagram-overrides.json',import.meta.url)));
test('DNS uses the right participants, referrals, answer and cache step',()=>{
 const d=overrides.find(o=>o.id==='dns-resolution').diagram;
 assert.deepEqual(d.messages.map(m=>[m.from,m.to]),[['app','resolver'],['resolver','root'],['root','resolver'],['resolver','tld'],['tld','resolver'],['resolver','auth'],['auth','resolver'],['resolver','resolver'],['resolver','app']]);
 assert.equal(d.messages[6].label,'A 192.0.2.10');
 const html=renderDiagram(d);
 assert.ok(html.includes('<path'));assert.ok(html.includes('<rect'));assert.ok(html.includes('<polygon'));
 assert.ok(!html.includes('App -&gt; Stub'));
});
test('ASCII geometry becomes paths and shapes, not connector text',()=>{
 const source='+-------+     +-------+\n| Cache |---->|  DB   |\n+-------+     +-------+';
 const d=compileDrawing(source);
 assert.equal(d.type,'layout');
 assert.equal(d.primitives.filter(p=>p.kind==='box').length,2);
 assert.equal(d.primitives.filter(p=>p.kind==='arrow'&&p.direction==='right').length,1);
 assert.deepEqual(d.labels.map(l=>l.text),['Cache','DB']);
 assert.ok(!renderDiagram(d).includes('-------'));
});
test('bidirectional, downward and Unicode arrows keep their directions',()=>{
 const d=compileDrawing('A <---> B\n    |\n    v\n    C ──▶ D');
 assert.ok(d.primitives.some(p=>p.kind==='arrow'&&p.direction==='left'));
 assert.ok(d.primitives.some(p=>p.kind==='arrow'&&p.direction==='right'));
 assert.ok(d.primitives.some(p=>p.kind==='arrow'&&p.direction==='down'));
});
test('pure trees retain topology and node identity, including duplicate labels',()=>{
 const source='    A\n   / \\\n  B   B\n /\nC';
 const d=compileTree(source);assert.equal(d.type,'tree');assert.equal(d.nodes.length,4);
 const labels=new Map(d.nodes.map(n=>[n.id,n.label]));
 assert.deepEqual(d.edges.map(e=>[labels.get(e.from),labels.get(e.to)]),[['A','B'],['A','B'],['B','C']]);
 assert.equal(new Set(d.nodes.map(n=>n.id)).size,4);
 assert.equal(compileTree('before       after\n A ---> B'),null);
});
test('code, equations, assembly and conflict markers are never diagrammed',()=>{
 for(const [source,language] of [['x = a -> b','python'],['θ ← θ − η·g',''],['n <= 2',''],['    ldr x0, [sp, #16]\n    mov x1, [sp, #32]',''],['<<<<<<< HEAD\nx = 2\n=======\nx = 3\n>>>>>>> branch','']]) assert.equal(compileDrawing(source,language),null,source);
});
test('code annotations inside a real box diagram do not hide the drawing',()=>{
 assert.ok(compileDrawing('let v = vec![1,2];\n+------+\n| ptr  |--> heap\n+------+'));
});
test('callout scanning matches renderer fences and does not strip > inside code',()=>{
 const blocks=[...extractExamples('> [!example]\n> ```diagram\n> A --> B\n> ```\n\n```\n> literal shell output\n```')];
 assert.deepEqual(blocks,[{language:'diagram',source:'A --> B'},{language:'',source:'> literal shell output'}]);
});
test('missing override sources and invalid references fail the build',()=>{
 assert.throws(()=>compileCatalogue({},[{id:'missing',source:'none',diagram:{}}]),/Unmatched/);
 assert.throws(()=>validateDiagram({type:'sequence',participants:[{id:'a'},{id:'b'}],messages:[{from:'a',to:'missing',label:'send'}]}),/Invalid sequence message/);
});
test('all compiled definitions validate and render without invalid coordinates',()=>{
 for(const [key,d]of Object.entries(catalogue)){
  validateDiagram(d);const html=renderDiagram(d);
  assert.ok(!/(?:x|y|width|height|viewBox|d)="[^"]*(?:NaN|undefined|Infinity)/.test(html),key);
  assert.ok(html.includes('<svg'),key);
  assert.ok(html.includes('<path')||html.includes('<rect')||html.includes('<circle')||html.includes('<polygon'),key);
  if(d.type==='layout') for(const label of d.labels)assert.ok(!/[┌┐└┘├┤│─┬┴]|-->|<--/.test(label.text),key+' connector left as text');
 }
});
test('rendered labels are escaped, and source lookup rejects unknown drawings',()=>{
 const html=renderDiagram({type:'flow',title:'<script>',steps:['<script>alert(1)</script>']});
 assert.ok(!html.includes('<script>'));assert.ok(html.includes('&lt;script&gt;'));
 assert.equal(findDiagram('not in the catalogue','diagram'),null);
});
