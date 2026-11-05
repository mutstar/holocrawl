const fs=require('fs'),path=require('path');
const {chromium}=require('C:/Users/071staff/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const out=path.resolve(__dirname,'../preview/native-door10');
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{const p=await browser.newPage();await p.goto('http://127.0.0.1:8797/native-door10/native-maps.json');await p.addScriptTag({url:'http://127.0.0.1:8797/city-layout07/pixel-reducer.js'});
  const result=await p.evaluate(async()=>{const im=await new Promise((r,j)=>{const i=new Image();i.onload=()=>r(i);i.onerror=j;i.src='assets/concrete-wall-surface-original.png';});const raw=PixelReducer.read(im);let y0=raw.height,y1=-1;for(let y=0;y<raw.height;y++){let content=0;for(let x=0;x<raw.width;x++){const i=(y*raw.width+x)*4;if(raw.data[i]+raw.data[i+1]+raw.data[i+2]>90)content++;}if(content>raw.width*.8){y0=Math.min(y0,y);y1=y;}}if(y1<y0)throw Error('No opaque concrete band found');const bounds={x:0,y:y0,w:raw.width,h:y1-y0+1},surface=PixelReducer.quantize(PixelReducer.area(raw,256,32,bounds),18,128);return{png:PixelReducer.canvas(surface).toDataURL('image/png').split(',')[1],bounds,source:[raw.width,raw.height],target:[256,32],colors:18};});
  fs.writeFileSync(path.join(out,'assets/concrete-wall-surface256.png'),Buffer.from(result.png,'base64'));delete result.png;fs.writeFileSync(path.join(out,'wall-processing.json'),JSON.stringify(result,null,2)+'\n');console.log(result);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
