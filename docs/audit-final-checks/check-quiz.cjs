const{chromium}=require('playwright');const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const page=await browser.newPage({viewport:{width:390,height:844}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8000/');await page.locator('.subject-tile').first().waitFor();
 assert.equal(await page.evaluate(()=>performance.getEntriesByType('resource').some(r=>r.name.endsWith('/diagram-catalog.js'))),false);
 await page.locator('[data-tab="practice"]').click();await page.locator('#go').waitFor();
 await page.locator('[data-g="n"][data-v="5"]').click();await page.locator('#go').click();
 for(let i=0;i<5;i++){
  await page.locator('.option').first().waitFor();await page.locator('.option').first().click();await page.locator('#check').click();
  await page.locator('.verdict').waitFor();assert.equal(await page.locator('button button').count(),0);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),390);
  await page.locator('#next').click();if(i<4)await page.locator('#check').waitFor();
 }
 await page.locator('.score-ring').waitFor();assert.deepEqual(errors,[]);
 console.log('Home does not load diagram catalogue; practice, five-question quiz, feedback and results pass with lazy loading.');await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
