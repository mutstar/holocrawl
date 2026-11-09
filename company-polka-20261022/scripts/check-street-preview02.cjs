const {chromium}=require('C:/Users/071staff/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
const path=require('path');
(async()=>{
const out=path.resolve(__dirname,'../analysis/previews/street-generator02');
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
const page=await browser.newPage({viewport:{width:1440,height:1050},deviceScaleFactor:1});
const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:8788/');await page.waitForFunction(()=>window.previewReady===true);
await page.screenshot({path:path.join(out,'preview-desktop.png'),fullPage:true});
await page.evaluate(()=>previewApp.setOverview(true));
for(let i=0;i<5;i++){await page.evaluate(n=>previewApp.setStage(n),i);await page.locator('#mapPanel').screenshot({path:path.join(out,`stage-${i}.png`)});}
const movement=await page.evaluate(()=>{previewApp.setStage(4);const m=StreetGen.generate('CITY-001'),route=StreetGen.route(m,m.start,m.exit);for(let i=1;i<route.length;i++)previewApp.move(route[i].x-route[i-1].x,route[i].y-route[i-1].y);let s=previewApp.getState();const reached=s.player.x===s.exit.x&&s.player.y===s.exit.y;for(let i=0;i<100;i++)previewApp.move(-1,0);s=previewApp.getState();return{reached,wallBlocked:s.player.x>0,position:s.player};});
await page.locator('#newMap').click();const changed=(await page.evaluate(()=>previewApp.getState().seed))!=='CITY-001';
await page.locator('#seed').fill('CITY-001');await page.locator('#apply').click();
const first=await page.locator('#map').evaluate(c=>c.toDataURL());await page.locator('#apply').click();const deterministic=first===await page.locator('#map').evaluate(c=>c.toDataURL());
await page.locator('#build').click();await page.waitForFunction(()=>previewApp.getState().stage===4);await page.screenshot({path:path.join(out,'preview-overview.png'),fullPage:true});
await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(out,'preview-mobile.png'),fullPage:true});const noOverflow=await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth);
const result={errors,movement,changed,deterministic,noOverflow};fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify(result,null,2));console.log(result);await browser.close();if(errors.length||!movement.reached||!movement.wallBlocked||!changed||!deterministic||!noOverflow)process.exitCode=1;
})();


