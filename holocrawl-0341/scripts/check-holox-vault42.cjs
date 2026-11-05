const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
(async()=>{const b=await chromium.launch({headless:true,executablePath});try{
 const p=await b.newPage({viewport:{width:1280,height:1100}}),errors=[];
 p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)errors.push(r.url())});
 await p.goto(previewURL+'/holox-vault42/');await p.waitForFunction(()=>window.ready);
 const root=path.resolve(__dirname,'../preview/holox-vault42');
 const lab=await p.evaluate(()=>{const f=vaultReview;return{customMaterials:!!f.materials,brightness:f.materials.objectBrightness,counterBlocked:f.vault.fixtures.every(a=>{for(let x=a.x;x<a.x+a.w;x++)if(f.pass(f.layout.origin.x+x,f.layout.origin.y+a.y))return false;return true})}});assert(lab.customMaterials&&lab.counterBlocked);
 const walls=await p.evaluate(async()=>{
  const f=vaultReview,a=f.materials,image=await new Promise((r,j)=>{const i=new Image();i.onload=()=>r(i);i.onerror=j;i.src='assets/lab-wall-32.png'});
  const masks=new Set();for(let y=0;y<f.vault.height;y++)for(let x=0;x<f.vault.width;x++)if(f.vault.rows[y][x]==='#')masks.add(a.mask(f.layout.map,x+f.layout.origin.x,y+f.layout.origin.y));
  const test=document.createElement('canvas');test.width=768;test.height=640;a.draw(test.getContext('2d'),f.layout.origin,f.vault,{labWall:image},f.layout.map);const pixels=test.getContext('2d').getImageData(0,0,768,640).data;let floorUntouched=true;
  for(let y=0;y<f.vault.height;y++)for(let x=0;x<f.vault.width;x++)if(f.vault.rows[y][x]!=='#')for(let py=0;py<32;py++)for(let px=0;px<32;px++)if(pixels[(((f.layout.origin.y+y)*32+py)*768+(f.layout.origin.x+x)*32+px)*4+3]!==0)floorUntouched=false;
  const atlas=document.createElement('canvas');atlas.width=atlas.height=512;const g=atlas.getContext('2d');
  for(let mask=0;mask<256;mask++){const tile=a.sprite(image,mask);g.drawImage(tile,(mask%16)*32,Math.floor(mask/16)*32)}
  const unique=new Set();for(let mask=0;mask<16;mask++)unique.add(a.sprite(image,mask).toDataURL());
  return {floorUntouched,actualMasks:[...masks],primaryShapes:unique.size,all256Generated:a.cache.size===256,png:atlas.toDataURL().split(',')[1]};
 });
 assert(walls.floorUntouched&&walls.primaryShapes===16&&walls.all256Generated&&walls.actualMasks.length>5);
 fs.writeFileSync(path.join(root,'assets/wall-autotiles-256.png'),Buffer.from(walls.png,'base64'));delete walls.png;
 const geometry=await p.evaluate(()=>{
  const f=vaultReview,{vault:v,layout:l}=f,o=l.origin,walk=[];
  for(let y=0;y<v.height;y++)for(let x=0;x<v.width;x++)if(f.pass(o.x+x,o.y+y))walk.push({x:o.x+x,y:o.y+y});
  const allConnected=walk.every(t=>f.route(t).length>0),rewardsReachable=Object.values(v.rewardOptions).flat().every(a=>f.route({x:o.x+a.x,y:o.y+a.y}).length>0);
  const stations=v.stations.map(s=>{const cells=[];for(let y=0;y<s.h;y++)for(let x=0;x<s.w;x++)cells.push({x:o.x+s.x+x,y:o.y+s.y+y});return {id:s.id,blocked:cells.every(t=>!f.pass(t.x,t.y)),approachable:cells.some(t=>[[0,1],[0,-1],[-1,0],[1,0]].some(([dx,dy])=>f.route({x:t.x+dx,y:t.y+dy}).length>0))}});
  return {nineByNine:v.rows.length===9&&v.rows.every(r=>r.length===9),fiveMembers:v.stations.length===5&&new Set(v.stations.map(s=>s.id)).size===5,allConnected,rewardsReachable,stations,encounterSlotsReachable:v.encounterSlots.every(a=>f.route({x:o.x+a.x,y:o.y+a.y}).length>0)};
 });
 console.log(JSON.stringify({geometry}));
 assert(geometry.nineByNine&&geometry.fiveMembers&&geometry.allConnected&&geometry.rewardsReachable&&geometry.encounterSlotsReachable);assert(geometry.stations.every(s=>s.blocked&&s.approachable));
 await p.locator('#field').screenshot({path:path.join(root,'field42.png')});await p.locator('#closeup').screenshot({path:path.join(root,'lab42.png')});
 await p.keyboard.press('ArrowUp');await p.keyboard.press('ArrowUp');let state=await p.evaluate(()=>vaultReview.getState());assert.deepStrictEqual(state.player,{x:14,y:12});assert(state.turns===2&&state.opened.includes('14,11'));
 await p.keyboard.press('ArrowUp');state=await p.evaluate(()=>vaultReview.getState());assert.deepStrictEqual(state.player,{x:14,y:11});
 const loot=await p.evaluate(()=>{const f=vaultReview;for(const target of f.rewards()){let guard=0;while(f.route(target).length>1&&guard++<100){const n=f.route(target)[1],s=f.getState().player;f.move(n.x-s.x,n.y-s.y)}}const first=f.getState();for(const target of f.rewards()){let guard=0;while(f.route(target).length>1&&guard++<100){const n=f.route(target)[1],s=f.getState().player;f.move(n.x-s.x,n.y-s.y)}}return{first,second:f.getState()}});
 assert(loot.first.inventory.potion===2&&loot.first.inventory.scroll===1&&loot.first.taken.length===2);assert.deepStrictEqual(loot.first.inventory,loot.second.inventory);assert(loot.first.opened.includes('11,5'),'internal security door used');
 await p.selectOption('#reward','reserve');assert.deepStrictEqual((await p.evaluate(()=>vaultReview.getState())).inventory,{});
 await p.evaluate(()=>vaultReview.walkTo(vaultReview.rewards()[0]));await p.waitForFunction(()=>vaultReview.getState().inventory.scroll===2);
 assert(await p.locator('#members button').count()===5);for(const name of ['라플라스','루이','코요리','클로에','이로하']){await p.locator('#members button').filter({hasText:name}).click();assert((await p.locator('#info').innerText()).includes(name));}
 await p.locator('#reset').click();await p.locator('#labels').click();await p.locator('#closeup').screenshot({path:path.join(root,'members42.png')});
 await p.locator('#markers').click();await p.locator('#closeup').screenshot({path:path.join(root,'planned42.png')});await p.locator('#markers').click();
 await p.locator('#fog').click();const fog=await p.evaluate(()=>{const f=vaultReview,s=f.getState();return{on:s.fog,behindDoorHidden:!s.visible[10*f.layout.map.w+14],hasMemory:s.explored.some(Boolean)}});assert(fog.on&&fog.behindDoorHidden&&fog.hasMemory);
 await p.setViewportSize({width:390,height:850});assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepStrictEqual(errors,[]);
 const result={status:'passed',walls,lab,geometry,keyboardMovement:true,doorOpenCostsTurn:true,internalDoorUsed:true,lootSinglePickup:true,alternateRewardReset:true,autoWalkWithDoors:true,fiveMemberButtons:true,fog,mobileNoOverflow:true,errors};fs.writeFileSync(path.join(root,'validation.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
 }finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
