const {chromium}=require('playwright');const assert=require('node:assert/strict');
(async()=>{
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
const context=await browser.newContext({viewport:{width:390,height:844}});const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://localhost:8000/#/m/databases/postgresql');
await page.getByRole('link',{name:/PostgreSQL in practice/}).click();await page.locator('#practise').waitFor();
assert.equal(await page.locator('.vector-diagram').count(),2);assert.match(await page.locator('#practise').innerText(),/12/);
for(const width of [320,390,1440]){await page.setViewportSize({width,height:844});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width);}
await page.setViewportSize({width:390,height:844});await page.screenshot({path:'/tmp/cs-study-ui-tools/postgres-lesson.png'});
await page.locator('#practise').click();
for(let i=0;i<12;i++){
 await page.locator('.option').first().click();await page.locator('#check').click();await page.locator('.verdict').waitFor();
 assert.equal(await page.locator('button button').count(),0);await page.locator('#next').click();
}
await page.locator('.score-ring').waitFor();
await page.evaluate(async()=>{await navigator.serviceWorker.ready;if(!navigator.serviceWorker.controller)await new Promise(r=>navigator.serviceWorker.addEventListener('controllerchange',r,{once:true}));});
await context.setOffline(true);await page.goto('http://localhost:8000/#/l/databases/postgresql/postgresql-in-practice');await page.locator('#practise').waitFor();await page.reload();await page.locator('#practise').waitFor();
assert.equal(await page.locator('.vector-diagram').count(),2);assert.deepEqual(errors,[]);
console.log('PASS: module navigation, 2 vector diagrams, 3 widths, all 12 quiz questions and offline lesson reload.');await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
