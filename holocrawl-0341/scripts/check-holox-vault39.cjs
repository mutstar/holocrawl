const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
(async()=>{const b=await chromium.launch({headless:true,executablePath});try{
 const p=await b.newPage({viewport:{width:1280,height:1100}}),errors=[];
 p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)errors.push(r.url())});
 await p.goto(previewURL+'/holox-vault39/');await p.waitForFunction(()=>window.ready);
 const root=path.resolve(__dirname,'../preview/holox-vault39');
 const architecture=await p.evaluate(()=>{
  const f=vaultReview,{vault:v,architecture:a}=f;
  return {brightness:a.objectBrightness,fixturesOnlyOnWalls:a.fixtures.every(d=>{for(let y=d.y;y<d.y+d.h;y++)for(let x=d.x;x<d.x+d.w;x++)if(v.rows[y]?.[x]!=='#')return false;return true}),fixtureCount:a.fixtures.length};
 });
 assert(architecture.brightness>1&&architecture.brightness<1.5&&architecture.fixturesOnlyOnWalls&&architecture.fixtureCount>=8);
 const geometry=await p.evaluate(()=>{
  const f=vaultReview,{vault:v,layout:l}=f,o=l.origin,walk=[];
  for(let y=0;y<v.height;y++)for(let x=0;x<v.width;x++)if(f.pass(o.x+x,o.y+y))walk.push({x:o.x+x,y:o.y+y});
  const allConnected=walk.every(t=>f.route(t).length>0),rewardsReachable=Object.values(v.rewardOptions).flat().every(a=>f.route({x:o.x+a.x,y:o.y+a.y}).length>0);
  const stations=v.stations.map(s=>{const cells=[];for(let y=0;y<s.h;y++)for(let x=0;x<s.w;x++)cells.push({x:o.x+s.x+x,y:o.y+s.y+y});return {id:s.id,blocked:cells.every(t=>!f.pass(t.x,t.y)),approachable:cells.some(t=>[[0,1],[0,-1],[-1,0],[1,0]].some(([dx,dy])=>f.route({x:t.x+dx,y:t.y+dy}).length>0))}});
  return {nineByNine:v.rows.length===9&&v.rows.every(r=>r.length===9),fiveMembers:v.stations.length===5&&new Set(v.stations.map(s=>s.id)).size===5,allConnected,rewardsReachable,stations,encounterSlotsReachable:v.encounterSlots.every(a=>f.route({x:o.x+a.x,y:o.y+a.y}).length>0)};
 });
 console.log(JSON.stringify({geometry}));
 assert(geometry.nineByNine&&geometry.fiveMembers&&geometry.allConnected&&geometry.rewardsReachable&&geometry.encounterSlotsReachable);assert(geometry.stations.every(s=>s.blocked&&s.approachable));
 await p.locator('#field').screenshot({path:path.join(root,'field39.png')});await p.locator('#closeup').screenshot({path:path.join(root,'lab39.png')});
 await p.keyboard.press('ArrowUp');await p.keyboard.press('ArrowUp');let state=await p.evaluate(()=>vaultReview.getState());assert.deepStrictEqual(state.player,{x:14,y:12});assert(state.turns===2&&state.opened.includes('14,11'));
 await p.keyboard.press('ArrowUp');state=await p.evaluate(()=>vaultReview.getState());assert.deepStrictEqual(state.player,{x:14,y:11});
 const loot=await p.evaluate(()=>{const f=vaultReview;for(const target of f.rewards()){let guard=0;while(f.route(target).length>1&&guard++<100){const n=f.route(target)[1],s=f.getState().player;f.move(n.x-s.x,n.y-s.y)}}const first=f.getState();for(const target of f.rewards()){let guard=0;while(f.route(target).length>1&&guard++<100){const n=f.route(target)[1],s=f.getState().player;f.move(n.x-s.x,n.y-s.y)}}return{first,second:f.getState()}});
 assert(loot.first.inventory.potion===2&&loot.first.inventory.scroll===1&&loot.first.taken.length===2);assert.deepStrictEqual(loot.first.inventory,loot.second.inventory);assert(loot.first.opened.includes('11,5'),'internal security door used');
 await p.selectOption('#reward','reserve');assert.deepStrictEqual((await p.evaluate(()=>vaultReview.getState())).inventory,{});
 await p.evaluate(()=>vaultReview.walkTo(vaultReview.rewards()[0]));await p.waitForFunction(()=>vaultReview.getState().inventory.scroll===2);
 assert(await p.locator('#members button').count()===5);for(const name of ['라플라스','루이','코요리','클로에','이로하']){await p.locator('#members button').filter({hasText:name}).click();assert((await p.locator('#info').innerText()).includes(name));}
 await p.locator('#reset').click();await p.locator('#labels').click();await p.locator('#closeup').screenshot({path:path.join(root,'members39.png')});
 await p.locator('#markers').click();await p.locator('#closeup').screenshot({path:path.join(root,'planned39.png')});await p.locator('#markers').click();
 await p.locator('#fog').click();const fog=await p.evaluate(()=>{const f=vaultReview,s=f.getState();return{on:s.fog,behindDoorHidden:!s.visible[10*f.layout.map.w+14],hasMemory:s.explored.some(Boolean)}});assert(fog.on&&fog.behindDoorHidden&&fog.hasMemory);
 await p.setViewportSize({width:390,height:850});assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepStrictEqual(errors,[]);
 const result={status:'passed',architecture,geometry,keyboardMovement:true,doorOpenCostsTurn:true,internalDoorUsed:true,lootSinglePickup:true,alternateRewardReset:true,autoWalkWithDoors:true,fiveMemberButtons:true,fog,mobileNoOverflow:true,errors};fs.writeFileSync(path.join(root,'validation.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
 }finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
