// Render the remaining thirteen floor objects at the same scale as the player.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const{chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
const out=path.resolve(__dirname,'../preview/market-rest116');fs.mkdirSync(out,{recursive:true});
(async()=>{const browser=await chromium.launch({executablePath,headless:true});try{
 const p=await browser.newPage();await p.goto(`${previewURL}/city-market115/`);await p.waitForFunction(()=>window.previewReady);
 const groups=[{id:'merchandise',ids:['shirt-stack','hoodie-rack','plush-basket','poster-rolls','keychain-hooks','badge-trays','shopping-bags']},{id:'delivery-street',ids:['open-carton','delivery-cart','folding-crates','trash-bags','paper-rubbish','recycling-bins']}];
 for(const group of groups){
  const result=await p.evaluate(({ids})=>{
   const canvas=document.createElement('canvas');canvas.width=960;canvas.height=Math.ceil(ids.length/2)*216;const g=canvas.getContext('2d');g.imageSmoothingEnabled=false;g.fillStyle='#152128';g.fillRect(0,0,canvas.width,canvas.height);
   const rows=[];ids.forEach((type,i)=>{
    const[fw,fh]=MarketGen.footprints[type],x=i%2*480,y=Math.floor(i/2)*216,meta=MerchCatalog.find(m=>m.id===type);
    const plate=document.createElement('canvas');plate.width=112;plate.height=48;const a=plate.getContext('2d');a.imageSmoothingEnabled=false;
    for(let yy=0;yy<2;yy++)for(let xx=0;xx<4;xx++)a.drawImage(floorVariants[(xx+yy*3)%16],xx*32,yy*32);
    const ox=Math.floor((112-(fw*32+8+32))/2);a.save();a.translate(ox,8);Scene115.draw(a,{x:0,y:0,type,footW:fw,footH:fh},{seed:'REST116',floorNumber:4},images,32,0);a.restore();
    // Exactly the same32px player layers; the whole review plate gets3x.
    for(const part of['body','boots','armour','helmet','sword'])a.drawImage(images[part],ox+fw*32+8,4,32,32);
    g.fillStyle='#213039';g.fillRect(x+4,y+4,472,208);g.drawImage(plate,x+72,y+28,336,144);
    g.textAlign='center';g.fillStyle='#aec0ca';g.font='14px "Malgun Gothic",sans-serif';g.fillText(`${fw}×${fh}칸 · 캐릭터와 같은 배율`,x+240,y+21);
    g.fillStyle='#e4ecef';g.font='17px "Malgun Gothic",sans-serif';g.fillText(meta.name,x+240,y+197);
    const d=Scene115.design(type,fw,fh);rows.push({id:type,name:meta.name,footprint:[fw,fh],art:[d.w,d.h],playerTile:[32,32]});
   });return{data:canvas.toDataURL(),rows,width:canvas.width,height:canvas.height};
  },{ids:group.ids});
  assert.equal(result.rows.length,group.ids.length);fs.writeFileSync(path.join(out,group.id+'.png'),Buffer.from(result.data.split(',')[1],'base64'));delete result.data;group.export=result;
 }
 assert.equal(new Set(groups.flatMap(g=>g.ids)).size,13);
 fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify({revision:116,sourceArtRevision:115,objects:13,scale:3,playerAndPropsSameScale:true,originalAssetsModified:false,groups},null,2)+'\n');
 console.log(JSON.stringify({status:'passed',remaining:13,groups:2,scale:3}));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
