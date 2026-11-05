const fs=require('fs'),path=require('path'),assert=require('assert');const{chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
(async()=>{const b=await chromium.launch({headless:true,executablePath});try{const root=path.resolve(__dirname,'../preview/holox-floor54'),results=[];
const assetPage=await b.newPage();await assetPage.goto(previewURL+'/');await assetPage.addScriptTag({url:previewURL+'/holox-floor54/materials.js'});
const audit=await assetPage.evaluate(async()=>{
 const m=LabMaterials,image=await new Promise((r,j)=>{const i=new Image();i.onload=()=>r(i);i.onerror=j;i.src='/holox-floor54/assets/entrance-64x32.png'}),atlas=document.createElement('canvas');atlas.width=atlas.height=512;const ag=atlas.getContext('2d');let opaque=true;
 for(let mask=0;mask<256;mask++){const c=m.sprite(image,mask);ag.drawImage(c,mask%16*32,Math.floor(mask/16)*32);const d=c.getContext('2d').getImageData(0,0,32,32).data;for(let i=3;i<d.length;i+=4)if(d[i]!==255)opaque=false}
 const primaryShapes=new Set(Array.from({length:16},(_,mask)=>m.sprite(image,mask).toDataURL())).size;
 const patterns=[['HORIZONTAL',['.....','.....','#####','.....']],['VERTICAL',['..#..','..#..','..#..','..#..']],['OUTER TURN',['.###.','.#...','.#...','.....']],['INNER TURN',['.###.','.#.#.','.#.#.','.....']],['T JUNCTION',['..#..','.###.','..#..','..#..']],['CROSS',['..#..','.###.','..#..','.....']]];
 const sheet=document.createElement('canvas');sheet.width=480;sheet.height=320;const g=sheet.getContext('2d');g.fillStyle='#343833';g.fillRect(0,0,480,320);g.imageSmoothingEnabled=false;
 patterns.forEach(([name,rows],i)=>{const ox=i%3*160,oy=Math.floor(i/3)*160,map={w:5,h:4,rows};for(let y=0;y<4;y++)for(let x=0;x<5;x++)if(rows[y][x]==='#')g.drawImage(m.sprite(image,m.mask(map,x,y),(x+y)%3!==0,m.sidesFor(map,x,y)),ox+x*32,oy+y*32);g.fillStyle='#d1c4e1';g.font='12px sans-serif';g.fillText(name,ox+8,oy+151)});
 let capSeams=true;const read=c=>c.getContext('2d').getImageData(0,0,32,32).data;
 // A continuous 3-cell beam has no repeated cap border at its joins.
 const hm={w:3,h:1,rows:['###']},tiles=[0,1,2].map(x=>read(m.sprite(image,m.mask(hm,x,0))));for(let k=0;k<2;k++)for(let y=4;y<14;y++)for(let c=0;c<3;c++)if(Math.abs(tiles[k][(y*32+31)*4+c]-tiles[k+1][y*32*4+c])>6)capSeams=false;
 const vm={w:1,h:3,rows:['#','#','#']},vt=[0,1,2].map(y=>read(m.sprite(image,m.mask(vm,0,y))));for(let k=0;k<2;k++)for(let x=4;x<24;x++)for(let c=0;c<3;c++)if(Math.abs(vt[k][(31*32+x)*4+c]-vt[k+1][x*4+c])>6)capSeams=false;
 const fixtureMap={w:9,h:9,rows:['#########','#FF#....#','#.......#','#..#....#','#F.###..#','#..G...F#','#FF#FF..#','#.......#','######.##']};
 const canvas=document.createElement('canvas');canvas.width=canvas.height=288;const ctx=canvas.getContext('2d'),v=await(await fetch('/holox-floor54/vault.json')).json(),lui=await new Promise((r,j)=>{const i=new Image();i.onload=()=>r(i);i.onerror=j;i.src='/holox-vault47/assets/lui-panel-64x12.png'});
 m.draw(ctx,{x:0,y:0},v,{labWall:image,entrance:image,luiPanel:lui},fixtureMap);const d=ctx.getImageData(0,0,288,288).data;let floorUntouched=true;for(let y=0;y<9;y++)for(let x=0;x<9;x++)if(v.rows[y][x]!=='#')for(let py=0;py<32;py++)for(let px=0;px<32;px++)if(d[((y*32+py)*288+x*32+px)*4+3])floorUntouched=false;
 let insetCapPreserved=true;for(const f of v.fixtures.filter(a=>a.render==='inset-wall-tile'))for(let part=0;part<f.w;part++){const mask=m.mask(fixtureMap,f.x+part,f.y),base=read(m.sprite(image,mask)),inset=read(m.insetWall(image,mask,f.theme,part));for(let y=0;y<16;y++)for(let x=0;x<32;x++)for(let c=0;c<4;c++)if(base[(y*32+x)*4+c]!==inset[(y*32+x)*4+c])insetCapPreserved=false}
 const leftSides=m.sidesFor(fixtureMap,0,3),rightSides=m.sidesFor(fixtureMap,8,3),leftTile=read(m.sprite(image,m.mask(fixtureMap,0,3),false,leftSides)),rightTile=read(m.sprite(image,m.mask(fixtureMap,8,3),false,rightSides));
 const gold=(d,x)=>Array.from({length:22},(_,i)=>{const j=((i+4)*32+x)*4;return d[j]>120&&d[j+1]>90&&d[j+2]<60}).filter(Boolean).length;
 const inwardStripes=leftSides==='e'&&rightSides==='w'&&gold(leftTile,29)>5&&gold(leftTile,1)===0&&gold(rightTile,2)>5&&gold(rightTile,30)===0;
 // The doorway no longer overlays a differently scaled raster wall; its upper half
 // exactly matches ordinary wall tiles, including through the two old join positions.
 const plain=document.createElement('canvas');plain.width=plain.height=288;const pg=plain.getContext('2d');for(let y=0;y<9;y++)for(let x=0;x<9;x++)if(v.rows[y][x]==='#')pg.drawImage(m.sprite(image,m.mask(fixtureMap,x,y),(x+y)%3!==0,m.sidesFor(fixtureMap,x,y)),x*32,y*32);
 const baseline=pg.getImageData(0,0,288,288).data;let entryUpperFaceContinuous=true;for(let x=3*32;x<9*32;x++)for(let y=8*32;y<8*32+16;y++)if(v.rows[8][Math.floor(x/32)]==='#')for(let c=0;c<4;c++)if(baseline[(y*288+x)*4+c]!==d[(y*288+x)*4+c])entryUpperFaceContinuous=false;
 return{inwardStripes,entryUpperFaceContinuous,opaque,primaryShapes,all256Generated:Array.from({length:256},(_,mask)=>m.cache.has(mask+':false:e')).every(Boolean),capSeams,floorUntouched,insetCapPreserved,atlas:atlas.toDataURL().split(',')[1],connections:sheet.toDataURL().split(',')[1]};
});
fs.writeFileSync(path.join(root,'assets/wall-autotiles-256.png'),Buffer.from(audit.atlas,'base64'));fs.writeFileSync(path.join(root,'assets/wall-connections.png'),Buffer.from(audit.connections,'base64'));delete audit.atlas;delete audit.connections;
assert(audit.inwardStripes&&audit.entryUpperFaceContinuous&&audit.all256Generated&&audit.opaque&&audit.primaryShapes===16&&audit.capSeams&&audit.floorUntouched&&audit.insetCapPreserved);await assetPage.close();
for(let n=0;n<3;n++){
 const p=await b.newPage({viewport:{width:1280,height:1080}}),errors=[];p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)errors.push(r.status()+' '+r.url())});
 await p.goto(previewURL+'/holox-floor54/?map='+n);await p.waitForFunction(()=>window.ready);
 assert(await p.locator('#placementInfo').innerText());
 const decor=await p.evaluate(()=>{const f=vaultReview,v=f.vault,d=v.entranceDecor,o=f.layout.origin;return {kind:d.kind,onWalls:d.wallCells.every(([x,y])=>v.rows[y][x]==='#'),openThreshold:f.pass(o.x+d.opening.x,o.y+d.opening.y),unchangedRows:JSON.stringify(v.rows),unchangedScenario:JSON.stringify(f.layout.map.rows)}});
 const previous=JSON.parse(fs.readFileSync(path.join(root,'../holox-floor48/vault.json'))),scenario=JSON.parse(fs.readFileSync(path.join(root,'../holox-floor48/scenario-'+n+'.json')));
 assert.strictEqual(decor.kind,'holodori-armored-entry');assert(decor.onWalls&&decor.openThreshold);
 assert.strictEqual(decor.unchangedRows,JSON.stringify(previous.rows));assert.strictEqual(decor.unchangedScenario,JSON.stringify(scenario.map.rows));
 await p.locator('#closeup').screenshot({path:path.join(root,'lab-'+n+'.png')});
 await p.locator('#field').screenshot({path:path.join(root,'approach-'+n+'.png')});
 await p.locator('#overview').click();await p.locator('#field').screenshot({path:path.join(root,'floor-'+n+'.png')});
 await p.locator('#labView').click();await p.locator('#stairsStart').click();
 const reach=await p.evaluate(()=>{const f=vaultReview,o=f.layout.origin,v=f.vault;return{atStairs:JSON.stringify(f.getState().player)===JSON.stringify(f.layout.stairsStart),allMembers:v.stations.every(s=>{for(let y=s.y;y<s.y+s.h;y++)for(let x=s.x;x<s.x+s.w;x++)for(const[dx,dy]of[[1,0],[-1,0],[0,1],[0,-1]])if(f.route({x:o.x+x+dx,y:o.y+y+dy}).length>0)return true;return false}),allRewards:Object.values(v.rewardOptions).flat().every(a=>f.route({x:o.x+a.x,y:o.y+a.y}).length>0),stairs:f.layout.placement.stairsPreserved.every(a=>f.route(a).length>0),size:[f.layout.map.w,f.layout.map.h],labDoors:v.rows.some(r=>r.includes('+'))}});
 assert(reach.atStairs&&reach.allMembers&&reach.allRewards&&reach.stairs&&!reach.labDoors);assert.deepStrictEqual(reach.size,[80,70]);
 await p.locator('#reset').click();await p.evaluate(()=>vaultReview.walkTo(vaultReview.rewards()[0]));await p.waitForFunction(()=>vaultReview.getState().taken.length===1,{timeout:20000});
 await p.locator('#fog').click();assert(await p.evaluate(()=>vaultReview.getState().fog));
 await p.locator('#stairsStart').click();assert(await p.evaluate(()=>vaultReview.getState().explored.reduce((a,b)=>a+b,0)<250));
 await p.setViewportSize({width:390,height:850});assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepStrictEqual(errors,[]);
 results.push({case:n,status:'passed',...reach,integratedEntry:true,unchangedCollision:true,autoEnterAndPickup:true,fogAtStairs:true,mobileNoOverflow:true,errors});await p.close();
}
fs.writeFileSync(path.join(root,'validation.json'),JSON.stringify({status:'passed',scope:'Connected armour wall replacement; browser preview only, not native engine integration',walls:audit,cases:results},null,2));console.log(JSON.stringify(results));
}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
