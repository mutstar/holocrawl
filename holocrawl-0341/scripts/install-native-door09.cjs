const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require('C:/Users/071staff/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const states=process.argv.slice(2).length?process.argv.slice(2):['closed','open'],root=path.resolve(__dirname,'../preview/native-door09');
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{const p=await browser.newPage();await p.goto('http://127.0.0.1:8797/native-door09/native-maps.json');await p.addScriptTag({url:'http://127.0.0.1:8797/city-layout07/pixel-reducer.js'});
  for(const state of states){
   const result=await p.evaluate(async state=>{const im=await new Promise((r,j)=>{const i=new Image();i.onload=()=>r(i);i.onerror=j;i.src=`assets/fire-door-${state}-original.png`;});const raw=PixelReducer.read(im),bounds=PixelReducer.bounds(raw,200),reduced=PixelReducer.quantize(PixelReducer.area(raw,32,32,bounds),14,128),canvas=PixelReducer.canvas(reduced);let clear=0;for(let i=3;i<raw.data.length;i+=4)if(raw.data[i]===0)clear++;return{png:canvas.toDataURL('image/png').split(',')[1],bounds,sourceWidth:im.width,sourceHeight:im.height,transparentSourcePixels:clear};},state);
   assert(result.transparentSourcePixels>0,'Generated source must have real transparency');fs.writeFileSync(path.join(root,`assets/fire-door-${state}32.png`),Buffer.from(result.png,'base64'));delete result.png;console.log(state,result);
  }
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
