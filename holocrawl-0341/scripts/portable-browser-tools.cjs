const fs=require('fs'),path=require('path');
let playwright;
try{playwright=require('playwright');}catch{}
if(!playwright){const home=process.env.USERPROFILE||process.env.HOME;const fallback=path.join(home,'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');if(fs.existsSync(fallback))playwright=require(fallback);}
if(!playwright)throw Error('Playwright not found: install playwright for Node.js or run from Codex.');
const candidates=[process.env.HOLOCRAWL_BROWSER_PATH,path.join(process.env.ProgramFiles||'C:/Program Files','Google/Chrome/Application/chrome.exe'),path.join(process.env['ProgramFiles(x86)']||'C:/Program Files (x86)','Microsoft/Edge/Application/msedge.exe')].filter(Boolean);
const executablePath=candidates.find(p=>fs.existsSync(p));
if(!executablePath)throw Error('Chrome/Edge not found; set HOLOCRAWL_BROWSER_PATH.');
module.exports={chromium:playwright.chromium,executablePath,previewURL:process.env.HOLOCRAWL_PREVIEW_URL||'http://127.0.0.1:8797'};
