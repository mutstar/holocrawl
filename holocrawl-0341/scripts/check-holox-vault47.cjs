const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
(async()=>{const b=await chromium.launch({headless:true,executablePath});try{
 const p=await b.newPage({viewport:{width:1280,height:1100}}),errors=[];
 p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)errors.push(r.url())});
 await p.goto(previewURL+'/holox-vault47/');await p.waitForFunction(()=>window.ready);
 const root=path.resolve(__dirname,'../preview/holox-vault47');
 const lab=await p.evaluate(()=>{const f=vaultReview;return{customMaterials:!!f.materials,brightness:f.materials.objectBrightness,counterBlocked:f.vault.fixtures.every(a=>{for(let x=a.x;x<a.x+a.w;x++)if(f.pass(f.layout.origin.x+x,f.layout.origin.y+a.y))return false;return true})}});assert(lab.customMaterials&&lab.counterBlocked);
 const walls=await p.evaluate(async()=>{
  const f=vaultReview,a=f.materials,plaque=await new Promise((r,j)=>{const i=new Image();i.onload=()=>r(i);i.onerror=j;i.src='assets/lui-panel-64x12.png'}),image=await new Promise((r,j)=>{const i=new Image();i.onload=()=>r(i);i.onerror=j;i.src='assets/iron-wall-32.png'});
  const masks=new Set();for(let y=0;y<f.vault.height;y++)for(let x=0;x<f.vault.width;x++)if(f.vault.rows[y][x]==='#')masks.add(a.mask(f.layout.map,x+f.layout.origin.x,y+f.layout.origin.y));
  const test=document.createElement('canvas');test.width=768;test.height=640;a.draw(test.getContext('2d'),f.layout.origin,f.vault,{labWall:image,luiPanel:plaque},f.layout.map);const pixels=test.getContext('2d').getImageData(0,0,768,640).data;let floorUntouched=true;
  for(let y=0;y<f.vault.height;y++)for(let x=0;x<f.vault.width;x++)if(f.vault.rows[y][x]!=='#')for(let py=0;py<32;py++)for(let px=0;px<32;px++)if(pixels[(((f.layout.origin.y+y)*32+py)*768+(f.layout.origin.x+x)*32+px)*4+3]!==0)floorUntouched=false;
  const atlas=document.createElement('canvas');atlas.width=atlas.height=512;const g=atlas.getContext('2d');
  for(let mask=0;mask<256;mask++){const tile=a.sprite(image,mask);g.drawImage(tile,(mask%16)*32,Math.floor(mask/16)*32)}
  const unique=new Set();for(let mask=0;mask<16;mask++)unique.add(a.sprite(image,mask).toDataURL());
  return {floorUntouched,actualMasks:[...masks],primaryShapes:unique.size,all256Generated:a.cache.size===256,png:atlas.toDataURL().split(',')[1]};
 });
 assert(walls.floorUntouched&&walls.primaryShapes===16&&walls.all256Generated&&walls.actualMasks.length>5);
 fs.writeFileSync(path.join(root,'assets/wall-autotiles-256.png'),Buffer.from(walls.png,'base64'));delete walls.png;
 const interior=await p.evaluate(()=>{
 const f=vaultReview,v=f.vault,o=f.layout.origin;
 const blocked=v.interiorFeatures.every(a=>!f.pass(o.x+a.x,o.y+a.y));
 const glass=v.interiorFeatures.find(a=>a.cell==='G'),source={x:o.x+glass.x-1,y:o.y+glass.y};
 const visibility=CrawlVisibility.compute(f.layout.map.w,f.layout.map.h,source,(x,y)=>['#','F','+'].includes(f.layout.map.rows[y]?.[x])?2:0,7);
 return {blocked,glassTransparent:!!visibility[(o.y+glass.y)*f.layout.map.w+o.x+glass.x+1],features:v.interiorFeatures.length,twoTableThemes:new Set(v.fixtures.map(a=>a.theme)).size===2};
 });assert(interior.blocked&&interior.glassTransparent&&interior.features===3&&interior.twoTableThemes);
 const mounting=await p.evaluate(()=>{const f=vaultReview,v=f.vault;const k=v.stations.find(s=>s.id==='koyori');return{noDoors:!v.rows.some(r=>r.includes('+'))&&f.layout.patches.length===0,noDoorUI:!document.querySelector('#closeDoor'),noSmallKoyori:k.sprite===false&&k.kind==='wall-counter',countersInWalls:v.fixtures.every(a=>a.mount==='wall'&&Array.from({length:a.w},(_,i)=>v.rows[a.y][a.x+i]).every(c=>c==='#')),pinkBelowOldKoyori:v.fixtures[0].x===4&&v.fixtures[0].y===4,oldKoyoriOpen:v.rows[3][4]==='.',oldCounterOpen:v.rows[3][6]==='.'&&v.rows[3][7]==='.'}});assert(Object.values(mounting).every(Boolean));
 const inset=await p.evaluate(async()=>{
  const f=vaultReview,a=f.materials,plaque=await new Promise((r,j)=>{const i=new Image();i.onload=()=>r(i);i.onerror=j;i.src='assets/lui-panel-64x12.png'}),image=await new Promise((r,j)=>{const i=new Image();i.onload=()=>r(i);i.onerror=j;i.src='assets/iron-wall-32.png'}),sheet=document.createElement('canvas');sheet.width=192;sheet.height=32;const g=sheet.getContext('2d');let capUnchanged=true,onlyInsideFace=true;let i=0;
  for(const fixture of f.vault.fixtures)for(let part=0;part<2;part++){
   const mask=a.mask(f.layout.map,f.layout.origin.x+fixture.x+part,f.layout.origin.y+fixture.y),base=a.sprite(image,mask).getContext('2d').getImageData(0,0,32,32).data,tile=fixture.render==='wall-plaque'?a.plaqueWall(image,mask,part,plaque):a.insetWall(image,mask,fixture.theme,part),pixels=tile.getContext('2d').getImageData(0,0,32,32).data;
   for(let y=0;y<32;y++)for(let x=0;x<32;x++)for(let k=0;k<4;k++)if(base[(y*32+x)*4+k]!==pixels[(y*32+x)*4+k]){if(y<16)capUnchanged=false;if(y<17||y>=30||(!(mask&2)&&x>=28))onlyInsideFace=false}
   g.drawImage(tile,i++*32,0);
  }
  return {capUnchanged,onlyInsideFace,tiles:i,png:sheet.toDataURL().split(',')[1]};
 });assert(inset.capUnchanged&&inset.onlyInsideFace&&inset.tiles===6);fs.writeFileSync(path.join(root,'assets/inset-counter-walls-47.png'),Buffer.from(inset.png,'base64'));delete inset.png;
 const zones=await p.evaluate(()=>{const f=vaultReview,v=f.vault;return{wideFloorZones:v.stations.filter(s=>s.sprite!==false&&s.w>1).length,wallCommand:v.stations.find(s=>s.id==='lui').sprite===false,oldLuiFloorOpen:v.rows[1][6]==='.',noSoloMemberFurniture:v.stations.every(s=>s.w>1)}});assert(zones.wideFloorZones===3&&zones.wallCommand&&zones.oldLuiFloorOpen&&zones.noSoloMemberFurniture);
 const geometry=await p.evaluate(()=>{
  const f=vaultReview,{vault:v,layout:l}=f,o=l.origin,walk=[];
  for(let y=0;y<v.height;y++)for(let x=0;x<v.width;x++)if(f.pass(o.x+x,o.y+y))walk.push({x:o.x+x,y:o.y+y});
  const allConnected=walk.every(t=>f.route(t).length>0),rewardsReachable=Object.values(v.rewardOptions).flat().every(a=>f.route({x:o.x+a.x,y:o.y+a.y}).length>0);
  const stations=v.stations.map(s=>{const cells=[];for(let y=0;y<s.h;y++)for(let x=0;x<s.w;x++)cells.push({x:o.x+s.x+x,y:o.y+s.y+y});return {id:s.id,blocked:cells.every(t=>!f.pass(t.x,t.y)),approachable:cells.some(t=>[[0,1],[0,-1],[-1,0],[1,0]].some(([dx,dy])=>f.route({x:t.x+dx,y:t.y+dy}).length>0))}});
  return {nineByNine:v.rows.length===9&&v.rows.every(r=>r.length===9),fiveMembers:v.stations.length===5&&new Set(v.stations.map(s=>s.id)).size===5,allConnected,rewardsReachable,stations,encounterSlotsReachable:v.encounterSlots.every(a=>f.route({x:o.x+a.x,y:o.y+a.y}).length>0)};
 });
 console.log(JSON.stringify({geometry}));
 assert(geometry.nineByNine&&geometry.fiveMembers&&geometry.allConnected&&geometry.rewardsReachable&&geometry.encounterSlotsReachable);assert(geometry.stations.every(s=>s.blocked&&s.approachable));
 await p.locator('#field').screenshot({path:path.join(root,'field47.png')});await p.locator('#closeup').screenshot({path:path.join(root,'lab47.png')});
 await p.keyboard.press('ArrowUp');await p.keyboard.press('ArrowUp');let state=await p.evaluate(()=>vaultReview.getState());assert.deepStrictEqual(state.player,{x:14,y:11});assert(state.turns===2&&state.opened.length===0);
 await p.keyboard.press('ArrowUp');state=await p.evaluate(()=>vaultReview.getState());assert.deepStrictEqual(state.player,{x:14,y:10});
 const loot=await p.evaluate(()=>{const f=vaultReview;for(const target of f.rewards()){let guard=0;while(f.route(target).length>1&&guard++<100){const n=f.route(target)[1],s=f.getState().player;f.move(n.x-s.x,n.y-s.y)}}const first=f.getState();for(const target of f.rewards()){let guard=0;while(f.route(target).length>1&&guard++<100){const n=f.route(target)[1],s=f.getState().player;f.move(n.x-s.x,n.y-s.y)}}return{first,second:f.getState()}});
 assert(loot.first.inventory.potion===2&&loot.first.inventory.scroll===1&&loot.first.taken.length===2);assert.deepStrictEqual(loot.first.inventory,loot.second.inventory);assert(loot.first.opened.length===0,'no door action may occur');
 await p.selectOption('#reward','reserve');assert.deepStrictEqual((await p.evaluate(()=>vaultReview.getState())).inventory,{});
 await p.evaluate(()=>vaultReview.walkTo(vaultReview.rewards()[0]));await p.waitForFunction(()=>vaultReview.getState().inventory.scroll===2);
 assert(await p.locator('#members button').count()===5);for(const name of ['라플라스','루이','코요리','클로에','이로하']){await p.locator('#members button').filter({hasText:name}).click();assert((await p.locator('#info').innerText()).includes(name));}
 await p.locator('#reset').click();await p.locator('#labels').click();await p.locator('#closeup').screenshot({path:path.join(root,'members47.png')});
 await p.locator('#markers').click();await p.locator('#closeup').screenshot({path:path.join(root,'planned47.png')});await p.locator('#markers').click();
 await p.locator('#fog').click();const fog=await p.evaluate(()=>{const f=vaultReview,s=f.getState();return{on:s.fog,openEntryVisible:!!s.visible[10*f.layout.map.w+14],wallHidesRoom:!s.visible[10*f.layout.map.w+12],hasMemory:s.explored.some(Boolean)}});assert(fog.on&&fog.openEntryVisible&&fog.wallHidesRoom&&fog.hasMemory);
 await p.setViewportSize({width:390,height:850});assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepStrictEqual(errors,[]);
 const result={status:'passed',zones,inset,mounting,interior,walls,lab,geometry,keyboardMovement:true,doorlessMovement:true,lootSinglePickup:true,alternateRewardReset:true,autoWalk:true,fiveMemberButtons:true,fog,mobileNoOverflow:true,errors};fs.writeFileSync(path.join(root,'validation.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
 }finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
