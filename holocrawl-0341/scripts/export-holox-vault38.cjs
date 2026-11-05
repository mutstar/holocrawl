const fs=require('fs'),path=require('path');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
(async()=>{const b=await chromium.launch({headless:true,executablePath});try{
 const p=await b.newPage();await p.goto(previewURL+'/city-batch22/');await p.waitForFunction(()=>window.ready);
 const root=path.resolve(__dirname,'../preview/holox-vault38'),assets=[];
 for(const name of ['laplus','lui','koyori','chloe','iroha']){
  const result=await p.evaluate(async name=>{
   const im=await new Promise((r,j)=>{const i=new Image();i.onload=()=>r(i);i.onerror=j;i.src='/holox-vault38/assets/'+name+'-original.png'});
   const source=PixelReducer.read(im),bounds=PixelReducer.bounds(source,200),scale=Math.min(24/bounds.w,25/bounds.h),w=Math.max(1,Math.round(bounds.w*scale)),h=Math.max(1,Math.round(bounds.h*scale));
   const art=PixelReducer.canvas(PixelReducer.quantize(PixelReducer.area(source,w,h,bounds),12,170)),c=document.createElement('canvas');c.width=32;c.height=32;c.getContext('2d').drawImage(art,Math.floor((32-w)/2),32-h);
   return {png:c.toDataURL().split(',')[1],bounds,native:[32,32],visible:[w,h]};
  },name);
  fs.writeFileSync(path.join(root,'assets',name+'-32.png'),Buffer.from(result.png,'base64'));delete result.png;assets.push({name,...result});
 }
 fs.writeFileSync(path.join(root,'art-manifest.json'),JSON.stringify({mode:'built-in image_gen',assets,promptFile:'../../design/holox-vault38-prompts.json',reduction:'Existing PixelReducer: preserve alpha,12 colors,24x25 visible max in32x32',entrance:'../facility-wall33/assets/holox-native.png',actorSprites:'../city-layout07/assets'},null,2));
 console.log(JSON.stringify(assets));
}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
