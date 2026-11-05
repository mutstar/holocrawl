const fs=require('fs'),path=require('path');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
(async()=>{const b=await chromium.launch({headless:true,executablePath});try{
 const p=await b.newPage();await p.goto(previewURL+'/city-batch22/');await p.waitForFunction(()=>window.ready);
 const root=path.resolve(__dirname,'../preview/holox-vault37'),assets=[];
 for(const name of ['laplus','lui','koyori','chloe','iroha']){
  const result=await p.evaluate(async name=>{
   const im=await new Promise((r,j)=>{const i=new Image();i.onload=()=>r(i);i.onerror=j;i.src='/holox-vault37/assets/'+name+'-original.png'});
   const source=PixelReducer.read(im),bounds=PixelReducer.bounds(source,200),scale=Math.min(60/bounds.w,29/bounds.h),w=Math.max(1,Math.round(bounds.w*scale)),h=Math.max(1,Math.round(bounds.h*scale));
   const art=PixelReducer.canvas(PixelReducer.quantize(PixelReducer.area(source,w,h,bounds),28,170)),c=document.createElement('canvas');c.width=64;c.height=32;c.getContext('2d').drawImage(art,Math.floor((64-w)/2),32-h);
   return {png:c.toDataURL().split(',')[1],bounds,native:[64,32],visible:[w,h]};
  },name);
  fs.writeFileSync(path.join(root,'assets',name+'-64x32.png'),Buffer.from(result.png,'base64'));delete result.png;assets.push({name,...result});
 }
 fs.writeFileSync(path.join(root,'art-manifest.json'),JSON.stringify({mode:'built-in image_gen',assets,promptFile:'../../design/holox-vault37-prompts.json',reduction:'Existing PixelReducer: preserve alpha,28 colors,60x29 visible max in64x32',entrance:'../facility-wall33/assets/holox-native.png',actorSprites:'../city-layout07/assets'},null,2));
 console.log(JSON.stringify(assets));
}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
