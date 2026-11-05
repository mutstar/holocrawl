const fs=require('fs'),path=require('path'),assert=require('assert');
const{chromium,executablePath,previewURL}=require('./portable-browser-tools.cjs');
(async()=>{const b=await chromium.launch({headless:true,executablePath});try{const p=await b.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(previewURL+'/city-batch22/?map=0&placement=5110521');await p.waitForFunction(()=>window.ready);const cases=[];
for(let i=0;i<8;i++)for(let n=0;n<2;n++){
 const v=await p.evaluate(({i,n})=>{placementSeed=5110521+n;generate(i);startExploration(true);const start=entry(),stairs=specials().filter(p=>isDown(p.f)),up=specials().filter(p=>isUp(p.f));
 const bfs=start=>{const seen=new Map([[start.x+','+start.y,0]]),queue=[start];for(let j=0;j<queue.length;j++)for(const[dx,dy]of dirs){const p={x:queue[j].x+dx,y:queue[j].y+dy},key=p.x+','+p.y;if(!seen.has(key)&&canWalk(p.x,p.y)){seen.set(key,seen.get(queue[j].x+','+queue[j].y)+1);queue.push(p);}}return seen;};
 const entrance=bfs(start),pairs=[];for(let a=0;a<stairs.length;a++)for(let b=a+1;b<stairs.length;b++)pairs.push({steps:bfs(stairs[a]).get(stairs[b].x+','+stairs[b].y),grid:Math.max(Math.abs(stairs[a].x-stairs[b].x),Math.abs(stairs[a].y-stairs[b].y))});
 return{map:i+1,placement:placementSeed,up:up.length,down:stairs.length,entryMinSteps:Math.min(...stairs.map(p=>entrance.get(p.x+','+p.y))),entryMinGrid:Math.min(...stairs.map(p=>Math.max(Math.abs(start.x-p.x),Math.abs(start.y-p.y)))),pairMinSteps:Math.min(...pairs.map(p=>p.steps)),pairMinGrid:Math.min(...pairs.map(p=>p.grid)),routesConnected:validation.stairsConnected};},{i,n});
 assert(v.up===1&&v.down===3&&v.routesConnected&&v.entryMinSteps>=18&&v.entryMinGrid>=9&&v.pairMinSteps>=14&&v.pairMinGrid>=8,JSON.stringify(v));cases.push(v);
}
const out=path.resolve(__dirname,'../preview/city-batch22'),before=JSON.parse(fs.readFileSync(path.join(out,'before-stairs.json'),'utf8')),after=JSON.parse(fs.readFileSync(path.join(out,'native-d1.json'),'utf8'));let moved=0;
for(let i=0;i<8;i++){const a=before.maps[i],b=after.maps[i];moved+=b.stairPlacement.moved;for(let y=0;y<a.h;y++)for(let x=0;x<a.w;x++){const f=a.palette[a.rows[y][x]],g=b.palette[b.rows[y][x]];if(f!==g)assert((f==='floor'||f.startsWith('stone_stairs_down'))&&(g==='floor'||g.startsWith('stone_stairs_down')));}}
assert.deepStrictEqual(errors,[]);const result={status:'passed',cases:cases.length,movedStairs:moved,wallDoorsEntryUnchanged:true,measure:'eight-direction walk distance after prop placement, plus grid separation',details:cases,errors};fs.writeFileSync(path.join(out,'stairs22-validation.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({...result,details:undefined}));
}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
