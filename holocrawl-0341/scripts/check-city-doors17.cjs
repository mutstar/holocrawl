const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
(async()=>{const b=await chromium.launch({headless:true,executablePath});try{
 const p=await b.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.status()>=400)errors.push(r.url())});
 await p.goto(previewURL+'/city-doors17/?map=0&placement=5110501');await p.waitForFunction(()=>window.ready,{timeout:30000});
 const cases=[];for(let i=0;i<3;i++)for(let n=0;n<10;n++){
 const v=await p.evaluate(({i,n})=>{placementSeed=n+5110501;generate(i);startExploration(true);const eq=new Set(),pipes=[];
 for(let y=1;y<m.h-1;y++)for(let x=1;x<m.w-1;x++){if(!isWall(feature(m,x,y))||isWall(feature(m,x,y+1))||wallVolumeEnabled&&!thinWallShape(m,x,y).n)continue;const run=wallRun(m,x,y),kind=hash(m.seed,x+431,y)%4;
 if(x!==run.decor||isDoor(feature(m,x,y))||isDoor(feature(m,x-1,y))||isDoor(feature(m,x+1,y))||fixtures.some(p=>MerchCatalog.find(a=>a.id===p.type).kind==='wall'&&p.y===y&&x>=p.x&&x<p.x+2))continue;
 if(kind===1){const plan=wallPipeSpan09(m,x,y);if(plan&&(!wallVolumeEnabled||Array.from({length:plan.length},(_,j)=>thinWallShape(m,plan.start+j,y).n).every(Boolean))){eq.add(kind);pipes.push(plan.length)}}else eq.add(kind);}
 return{map:i,seed:placementSeed,...validation,equipment:[...eq],pipes,crateClear:fixtures.filter(p=>p.type==='delivery-boxes').every(p=>specials().every(s=>Math.max(Math.abs(s.x-p.x),Math.abs(s.y-p.y))>3)),fronts:fixtures.filter(p=>MerchCatalog.find(a=>a.id===p.type).kind==='wall'&&p.type.endsWith('window')).map(w=>({type:w.type,front:fixtures.find(f=>f.y===w.y+1&&(f.x===w.x||f.x===w.x+1))?.type}))};},{i,n});
 assert(v.stairsConnected&&v.terrainRowsUnchanged&&v.mainRoutesClear&&v.crateClear,JSON.stringify(v));assert.strictEqual(v.reachable,v.baselineReachable-v.blocked);
 for(const type of ['acrylic-window','shirt-window','closed-shutter','half-shutter','trash-bags'])assert.strictEqual(v.byType[type],1,JSON.stringify(v));
 assert(v.byType['delivery-boxes']>=2&&v.byType['delivery-boxes']<=3);assert(v.fenceTiles>=2&&v.fenceTiles<=3);assert(v.equipment.length>0,JSON.stringify(v));assert(v.pipes.every(n=>n>=3&&n<=5));
 assert(v.fronts.every(f=>f.type==='acrylic-window'?f.front==='shirt-stack':['acrylic-rack','hoodie-rack','keychain-hooks','badge-trays','plush-basket'].includes(f.front)));cases.push(v);
 }
 const fence=await p.evaluate(()=>{const f=fences.find(f=>dirs.some(([dx,dy])=>canWalk(f.x-dx,f.y-dy)));const d=dirs.find(([dx,dy])=>canWalk(f.x-dx,f.y-dy));player={x:f.x-d[0],y:f.y-d[1]};const before={...player},t=turns,result=move(...d);return{blocked:!result&&player.x===before.x&&player.y===before.y&&turns===t,transparent:opacity(f.x,f.y)===0}});assert(fence.blocked&&fence.transparent);
 assert.deepStrictEqual(errors,[]);const result={status:'passed',cases:cases.length,allFloorPropTypesPresent:true,terrainUnchanged:true,stairsAndRoutesClear:true,fenceCollisionAndLOS:fence,details:cases};fs.writeFileSync(path.resolve(__dirname,'../preview/city-doors17/validation.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({...result,details:undefined}));
 }finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});






