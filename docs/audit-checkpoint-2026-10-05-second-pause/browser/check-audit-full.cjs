const {chromium}=require('playwright');
const fs=require('node:fs');const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const context=await browser.newContext({viewport:{width:390,height:844}});
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://localhost:8000/');await page.locator('.subject-tile').first().waitFor();
 await page.evaluate(async()=>{await navigator.serviceWorker.ready;if(!navigator.serviceWorker.controller)await new Promise(r=>navigator.serviceWorker.addEventListener('controllerchange',r,{once:true}));await import('./diagrams.js').then(m=>m.loadDiagrams());});
 const index=await page.evaluate(()=>fetch('./data/index.json').then(r=>r.json()));
 const result={date:new Date().toISOString(),viewport:390,lessons:0,questions:0,issues:[],errors};
 for(const s of index.subjects)for(const m of s.modules){
  const r=await page.evaluate(async({s,m})=>{
   const {render}=await import('./markdown.js');const mod=await fetch(`./data/${s}/${m}.json`).then(r=>r.json());
   const view=document.querySelector('#view');const issues=[];let questions=0;
   function inspect(id){
    if(document.documentElement.scrollWidth>390)issues.push({id,kind:'horizontal overflow',width:document.documentElement.scrollWidth});
    if(view.querySelector('button button'))issues.push({id,kind:'nested button'});
    for(const el of view.querySelectorAll('p,h2,h3,h4,li')){
     if(el.closest('pre,code,svg'))continue;
     // Fences and callout markers must be consumed by the renderer.
     if(/```|\[!(?:note|tip|warning|example)\]/i.test(el.textContent))issues.push({id,kind:'stray markdown marker',text:el.textContent.slice(0,160)});
    }
   }
   for(const l of mod.lessons){
    if(!l.body)throw new Error(`Missing body: ${l.id}`);
    view.innerHTML=`<article class="prose">${render(l.body)}</article>`;inspect(l.id);
    for(const q of l.questions){questions++;
     view.innerHTML=`<div class="quiz-prompt prose">${render(q.prompt)}</div><div class="options">${q.options.map(o=>`<div class="answer-card"><button class="option"><span class="key">A</span><span class="opt-body"><span class="opt-text prose">${render(o.text,{interactive:false})}</span></span></button><div class="opt-why prose">${render(o.explanation)}</div></div>`).join('')}</div><div class="card worked prose">${render(q.workedExample)}</div>`;inspect(q.id);
    }
   }
   return{lessons:mod.lessons.length,questions,issues};
  },{s:s.id,m:m.id});
  result.lessons+=r.lessons;result.questions+=r.questions;result.issues.push(...r.issues);
  console.log(`${s.id}/${m.id}: ${r.lessons} lessons, ${r.questions} questions, ${r.issues.length} rendering issues`);
 }
 // Exercise real routes, popover, expanded diagram and offline reload after exhaustive rendering.
 await page.goto('http://localhost:8000/#/dictionary?q=Redis');await page.locator('.dictionary-entry').first().waitFor();
 await page.goto('http://localhost:8000/#/l/databases/postgresql/postgresql-in-practice');await page.locator('#practise').waitFor();
 const term=page.locator('[data-term]').first();await term.click();await page.locator('#term-popover').waitFor({state:'visible'});await page.keyboard.press('Escape');
 await page.locator('[data-example="expand"]').first().click();await page.keyboard.press('Escape');
 await page.screenshot({path:'/tmp/cs-study-ui-tools/audit-postgres-final.png'});
 await context.setOffline(true);await page.reload();await page.locator('#practise').waitFor();
 await page.goto('http://localhost:8000/#/dictionary?q=Redis');await page.locator('.dictionary-entry').first().waitFor();
 result.offline='PostgreSQL lesson reload and Redis dictionary navigation passed';
 fs.writeFileSync('/tmp/cs-study-ui-tools/audit-render-results.json',JSON.stringify(result,null,2));
 await browser.close();assert.deepEqual(errors,[]);assert.deepEqual(result.issues,[]);console.log(`PASS ${result.lessons} lessons/${result.questions} questions at390px, UI interactions and offline checks.`);
})().catch(e=>{console.error(e);process.exit(1)});
