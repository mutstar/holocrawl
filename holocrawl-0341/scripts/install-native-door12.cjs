const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require('C:/Users/071staff/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const states=process.argv.slice(2).length?process.argv.slice(2):['closed','open'],root=path.resolve(__dirname,'../preview/native-door12');
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{const p=await browser.newPage();await p.goto('http://127.0.0.1:8797/native-door12/native-maps.json');await p.addScriptTag({url:'http://127.0.0.1:8797/city-layout07/pixel-reducer.js'});
  for(const state of states){
   const result=await p.evaluate(async state=>{const im=await new Promise((r,j)=>{const i=new Image();i.onload=()=>r(i);i.onerror=j;i.src=`assets/fire-door-${state}-original.png`;});const raw=PixelReducer.read(im),bounds=PixelReducer.bounds(raw,200),reduced=PixelReducer.quantize(PixelReducer.area(raw,24,30,bounds),14,128),canvas=document.createElement('canvas');canvas.width=canvas.height=32;canvas.getContext('2d').drawImage(PixelReducer.canvas(reduced),4,1);let clear=0;for(let i=3;i<raw.data.length;i+=4)if(!raw.data[i])clear++;return{png:canvas.toDataURL('image/png').split(',')[1],bounds,sourceWidth:im.width,sourceHeight:im.height,transparentSourcePixels:clear,nativeCanvas:[32,32],visibleArtBox:[4,1,24,30],colors:14};},state);
   assert(result.transparentSourcePixels>0);fs.writeFileSync(path.join(root,`assets/fire-door-${state}32.png`),Buffer.from(result.png,'base64'));delete result.png;fs.writeFileSync(path.join(root,`processing-${state}.json`),JSON.stringify(result,null,2)+'\n');console.log(state,result);
  }
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
