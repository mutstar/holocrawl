const {chromium}=require('C:/Users/071staff/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const path=require('path');
(async()=>{const b=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});const p=await b.newPage({viewport:{width:1440,height:1050}});const errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto('http://127.0.0.1:8796/?v=spiral-stairs06#start');await p.waitForFunction(()=>window.previewReady);const d=path.resolve(__dirname,'../analysis/previews/street-stairs06');await p.locator('#mapPanel').screenshot({path:path.join(d,'upstairs-field.png')});console.log({errors,state:await p.evaluate(()=>previewApp.getState())});await b.close();})();



