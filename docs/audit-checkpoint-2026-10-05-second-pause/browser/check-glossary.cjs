const {chromium}=require('playwright');const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const context=await browser.newContext();const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 for(const width of [320,390,1440])for(const colorScheme of ['light','dark']){
  await page.setViewportSize({width,height:844});await page.emulateMedia({colorScheme});
  await page.goto('http://localhost:8000/#/l/system-design/caching/cache-fundamentals');
  const term=page.locator('.technical-term[data-term="redis"]').first();await term.waitFor();await term.click();
  const panel=page.locator('#term-popover');await panel.waitFor({state:'visible'});
  assert.equal(await panel.locator('h2').innerText(),'Redis');
  const box=await panel.boundingBox();assert.ok(box.x>=0&&box.x+box.width<=width&&box.y>=0&&box.y+box.height<=844);
  assert.equal(await page.locator('button button, a button').count(),0);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width);
  if(width===390&&colorScheme==='dark')await page.screenshot({path:'/tmp/cs-study-ui-tools/dictionary-popover.png'});
  await page.keyboard.press('Escape');assert.ok(await panel.isHidden());assert.ok(await term.evaluate(e=>e===document.activeElement));
  await page.keyboard.press('Enter');await panel.waitFor({state:'visible'});
  await panel.getByRole('link',{name:'Open dictionary'}).click();await page.locator('#dictionary-query').waitFor();assert.ok(await panel.isHidden());
  assert.ok(await page.locator('.dictionary-entry').count()>=1);
  await page.locator('#dictionary-query').fill('Postgres');assert.ok((await page.locator('#dictionary-results').innerText()).includes('PostgreSQL'));
  await page.locator('#dictionary-query').fill('xyzxyzxyz');assert.equal(await page.locator('.dictionary-entry').count(),0);
  await page.locator('#dictionary-query').fill('');assert.equal(await page.locator('.dictionary-entry').count(),166);
 }
 await page.evaluate(async()=>{await navigator.serviceWorker.ready;if(!navigator.serviceWorker.controller)await new Promise(r=>navigator.serviceWorker.addEventListener('controllerchange',r,{once:true}));});
 await context.setOffline(true);await page.reload();await page.locator('#dictionary-query').waitFor();
 await page.goto('http://localhost:8000/#/l/system-design/caching/cache-fundamentals');await page.locator('.technical-term[data-term="redis"]').first().click();await page.locator('#term-popover').waitFor({state:'visible'});
 assert.deepEqual(errors,[]);console.log('PASS: 6 viewport/theme combinations, keyboard, focus, links, search, layout and offline definitions.');await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
