const { chromium } = require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const context=await browser.newContext({viewport:{width:1440,height:1050},permissions:['clipboard-read','clipboard-write']});
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const go=async(route,selector='.vector-diagram')=>{await page.goto('http://127.0.0.1:8000/#'+route);await page.locator(selector).first().waitFor();await page.waitForTimeout(200);};
 await go('/l/system-design/networking/net-dns');
 const dns=page.locator('.example-block').filter({has:page.locator('.dv-sequence')}).first();
 await dns.scrollIntoViewIfNeeded();await page.screenshot({path:'/tmp/cs-dns-desktop.png'});
 await dns.locator('[data-example="expand"]').click();
 await page.screenshot({path:'/tmp/cs-dns-expanded.png'});
 assert.equal(await page.locator('dialog .dv-sequence').count(),1);
 await page.locator('[data-zoom="1"]').click();assert.equal(await page.locator('dialog output').textContent(),'125%');
 await page.keyboard.press('Escape');assert.equal(await page.evaluate(()=>document.activeElement.dataset.example),'expand');
 await dns.locator('[data-example="copy"]').click();assert.match(await page.evaluate(()=>navigator.clipboard.readText()),/App -> Stub -> Recursive resolver/);
 await page.setViewportSize({width:390,height:844});await page.emulateMedia({colorScheme:'dark'});await page.waitForTimeout(250);
 await dns.scrollIntoViewIfNeeded();await page.screenshot({path:'/tmp/cs-dns-mobile.png'});
 assert.ok(await dns.locator('.example-content').evaluate(e=>e.scrollWidth>e.clientWidth));
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),390);
 const cases=[['/l/system-design/fundamentals/fund-approach','graph'],['/l/languages/lang-compilers/comp-pipeline','tree'],['/l/networks/net-foundations/nf-layered-models','memory'],['/l/ml/ml-fundamentals/mlf-metrics','matrix'],['/l/software-engineering/se-architecture/sea-layered','flow'],['/l/os/os-memory/mem-address-spaces','layout']];
 for(const[route,type]of cases){await go(route);assert.ok(await page.locator('.dv-'+type).count());assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),390,route);}
 await page.setViewportSize({width:1440,height:1050});await page.emulateMedia({colorScheme:'light'});
 // Every vector label must stay within the SVG bounds. No console errors or
 // text diagrams hidden inside SVG; exported paths render in the actual browser.
 const geometry=await page.evaluate(async()=>{
  const {default:catalogue}=await import('./diagram-catalog.js');const {renderDiagram}=await import('./diagrams.js');
  const host=document.createElement('div');host.className='prose';host.style='position:absolute;left:0;top:0;width:1600px';document.body.append(host);
  const issues=[];let count=0;
  for(const[key,d]of Object.entries(catalogue)){
   host.innerHTML=renderDiagram(d);const svg=host.querySelector('svg'),vb=svg.viewBox.baseVal;
   for(const label of svg.querySelectorAll('text')){const b=label.getBBox();if(b.x< -1||b.y< -1||b.x+b.width>vb.width+1||b.y+b.height>vb.height+1)issues.push({key,type:d.type,text:label.textContent,box:[b.x,b.y,b.width,b.height],bounds:[vb.width,vb.height]});}
   count++;
  }
  host.remove();return{count,issues};
 });
 console.log('Geometry audit:',JSON.stringify(geometry));
 require('node:fs').writeFileSync('/tmp/cs-diagram-geometry.json',JSON.stringify(geometry,null,2));
 // Contact sheets across the full catalogue help inspect representative layouts.
 await page.evaluate(async()=>{
  const {default:catalogue}=await import('./diagram-catalog.js');const{renderDiagram}=await import('./diagrams.js');
  const entries=Object.entries(catalogue);const selected=[...entries.filter(([,d])=>d.reviewed),...entries.filter(([,d])=>d.type==='tree').slice(0,6),...entries.filter(([,d])=>d.type==='layout').filter((_,i)=>i%65===0)];
  document.body.innerHTML='<main id="gallery" style="padding:20px;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px"></main>';
  const host=document.querySelector('#gallery');host.innerHTML=selected.map(([key,d])=>`<section class="example-block prose" style="margin:0"><figcaption>${key}: ${d.title}</figcaption><div class="example-content">${renderDiagram(d)}</div></section>`).join('');
 });
 await page.screenshot({path:'/tmp/cs-diagram-gallery.png',fullPage:true});
 // New renderer and generated catalogue must also load from the offline cache.
 await page.goto('http://localhost:8000/');await page.locator('.subject-tile').first().waitFor();
 await page.evaluate(async()=>{await navigator.serviceWorker.ready;if(!navigator.serviceWorker.controller)await new Promise(resolve=>navigator.serviceWorker.addEventListener('controllerchange',resolve,{once:true}));});
 await context.setOffline(true);await page.reload();await page.locator('.subject-tile').first().waitFor();
 await page.goto('http://localhost:8000/#/l/system-design/networking/net-dns');await page.locator('.dv-sequence').waitFor();
 await page.locator('[data-example="expand"]').first().click();assert.equal(await page.locator('dialog .vector-diagram').count(),1);
 assert.deepEqual(errors,[]);console.log('Diagram routes, small-screen containment, source copy, zoom, focus and offline rendering passed.');
 await browser.close();
 if(geometry.issues.length)process.exitCode=2;
})().catch(e=>{console.error(e);process.exit(1)});
