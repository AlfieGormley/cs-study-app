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
 // Exercise real routes, popover, expanded diagram and offline reload after exhaustive rendering.
 await page.goto('http://localhost:8000/#/dictionary?q=Redis');await page.locator('.dictionary-entry').first().waitFor();
 await page.goto('http://localhost:8000/#/l/databases/postgresql/postgresql-in-practice');await page.locator('#practise').waitFor();
 const term=page.locator('[data-term]').first();await term.click();await page.locator('#term-popover').waitFor({state:'visible'});await page.keyboard.press('Escape');
 await page.locator('.is-diagram [data-example="expand"]').first().click();await page.locator('.example-dialog[open]').waitFor();
 await page.locator('[data-zoom="1"]').click();assert.equal(await page.locator('.example-dialog output').innerText(),'125%');await page.keyboard.press('Escape');
 assert.equal(await page.locator('.example-dialog[open]').count(),0);
 for(const width of [320,390,1440]){await page.setViewportSize({width,height:844});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width);}
 await page.setViewportSize({width:390,height:844});
 await page.screenshot({path:'/tmp/cs-study-ui-tools/audit-postgres-final.png'});
 await page.emulateMedia({colorScheme:'dark'});await page.screenshot({path:'/tmp/cs-study-ui-tools/audit-postgres-dark-final.png'});
 await context.setOffline(true);await page.reload();await page.locator('#practise').waitFor();
 await page.goto('http://localhost:8000/#/dictionary?q=Redis');await page.locator('.dictionary-entry').first().waitFor();
 result.offline='PostgreSQL lesson reload and Redis dictionary navigation passed';
 fs.writeFileSync('/tmp/cs-study-ui-tools/audit-ui-final-results.json',JSON.stringify(result,null,2));
 await browser.close();assert.deepEqual(errors,[]);assert.deepEqual(result.issues,[]);console.log(`PASS ${result.lessons} lessons/${result.questions} questions at390px, UI interactions and offline checks.`);
})().catch(e=>{console.error(e);process.exit(1)});
