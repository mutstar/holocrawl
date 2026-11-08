// Export the currently rendered108/110 fixtures at exact6x pixel scale.
// No sprite bitmap is repainted; use the same palette and stock renderer.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const out=path.resolve(__dirname,'../preview/market-props111');fs.mkdirSync(out,{recursive:true});
(async()=>{const browser=await chromium.launch({executablePath,headless:true});try{
 const p=await browser.newPage({viewport:{width:1100,height:1000}});
 await p.goto(`${previewURL}/city-market108/catalog.html`);await p.waitForFunction(()=>window.catalogReady);
 const groups=[{id:'wall-displays',start:0,end:5,cols:2,cell:448},{id:'merch-displays',start:5,end:13,cols:4,cell:224},{id:'delivery-details',start:13,end:20,cols:4,cell:224}];
 for(const group of groups){
  const value=await p.evaluate(({group})=>{
   const list=MerchCatalog.slice(group.start,group.end),canvas=document.createElement('canvas');canvas.width=group.cols*group.cell;canvas.height=Math.ceil(list.length/group.cols)*256;
   const g=canvas.getContext('2d');g.imageSmoothingEnabled=false;g.fillStyle='#152027';g.fillRect(0,0,canvas.width,canvas.height);
   list.forEach((meta,i)=>{const x=(i%group.cols)*group.cell,y=Math.floor(i/group.cols)*256;
    g.fillStyle='#30414a';g.fillRect(x+4,y+4,group.cell-8,248);g.strokeStyle='#536772';g.strokeRect(x+4.5,y+4.5,group.cell-9,247);
    const source=document.createElement('canvas');source.width=meta.width;source.height=32;
    const s=source.getContext('2d');s.imageSmoothingEnabled=false;MarketStock.draw(s,{x:0,y:0,type:meta.id},{seed:'CATALOG-'+(group.start+i),floorNumber:4},images,32,0);
    const px=x+(group.cell-source.width*6)/2;g.drawImage(source,px,y+16,source.width*6,192);
    g.font='16px "Malgun Gothic", sans-serif';g.fillStyle='#e3ebed';g.textAlign='center';g.fillText(meta.name,x+group.cell/2,y+235);
   });
   return {data:canvas.toDataURL(),ids:list.map(m=>m.id),width:canvas.width,height:canvas.height};
  },{group});
  fs.writeFileSync(path.join(out,group.id+'.png'),Buffer.from(value.data.split(',')[1],'base64'));delete value.data;
  assert.equal(value.ids.length,group.end-group.start);group.export=value;
 }
 fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify({revision:111,source:'city-market108 palette used by city-market110',scale:6,renderedFixtureCount:20,memberStock:'Same existing catalog samples, unchanged member colours',groups},null,2)+'\n');
 console.log(JSON.stringify({status:'passed',fixtures:20,scale:6,groups:groups.length}));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
