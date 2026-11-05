const {chromium}=require('C:/Users/071staff/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path');
(async()=>{
const dir=path.resolve(__dirname,'../preview/city-market03'),out=path.join(dir,'assets/props-clean');fs.mkdirSync(out,{recursive:true});const assets=JSON.parse(fs.readFileSync(path.join(dir,'art-manifest.json'),'utf8'));
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
try{
 const p=await browser.newPage();await p.goto('http://127.0.0.1:8797/street-floor-random01/');await p.addScriptTag({path:path.join(dir,'pixel-reducer.js')});
 for(const asset of assets){
   const result=await p.evaluate(async asset=>{
     const image=await new Promise((r,j)=>{const i=new Image;i.onload=()=>r(i);i.onerror=j;i.src='http://127.0.0.1:8797/city-market03/assets/props/'+asset.source;});
     const raw=PixelReducer.read(image),rect=PixelReducer.bounds(raw),size=asset.kind==='wall'?[64,32]:asset.id==='paper-rubbish'?[28,19]:asset.id==='acrylic-rack'?[28,28]:[26,26];
     const sprite=PixelReducer.canvas(PixelReducer.quantize(PixelReducer.contrast(PixelReducer.area(raw,...size,rect)),18,92));
     const canvas=document.createElement('canvas');canvas.width=asset.size[0];canvas.height=asset.size[1];canvas.getContext('2d').drawImage(sprite,(canvas.width-size[0])/2,canvas.height-size[1]);
     return canvas.toDataURL('image/png').split(',')[1];
   },asset);
   fs.writeFileSync(path.join(out,asset.id+'.png'),Buffer.from(result,'base64'));
 }
 fs.writeFileSync(path.join(dir,'pixel-cleanup.json'),JSON.stringify({status:'prepared',assets:assets.length,sourceArtUnchanged:true,logicalTileSize:32,wallWidth:64,method:'alpha-weighted area reduction,18-colour palette, hard alpha, no dithering; final display uses nearest-neighbour',memberMethod:'direct per-display-size reduction from64x112 source; no bright dilation outline; separate8x13/12x18/16x24 caches',nativeGameLaunched:false},null,2)+'\n');
 console.log('Prepared20 normalized sprites using browser renderer; original PNGs preserved.');
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
