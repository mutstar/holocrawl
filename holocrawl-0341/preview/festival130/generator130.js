(function(root){
 'use strict';
 const native=typeof module!=='undefined'&&module.exports,G=native?require('../city-market124/generator.js'):root.StreetGen,P=native?require('../passage-safe124/passage124.js'):root.Passage124;
 const debris=(native?require('./debris130.js'):root.FestivalDebris130).filter(p=>p.id!=='broken-booth');
 const C=[[1,0],[-1,0],[0,1],[0,-1]];
 const stallTypes=['takoyaki','yakisoba','ringoame','goldfish','shooting','shaved-ice','cotton-candy','grilled-onigiri','ring-toss','omikuji'];
 const index=(m,x,y)=>y*m.w+x,cheb=(a,b)=>Math.max(Math.abs(a.x-b.x),Math.abs(a.y-b.y));
 function shuffle(a,r){for(let i=a.length-1;i>0;i--){const j=Math.floor(r()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
 function rectCells(m,p){const out=[];for(let y=p.y;y<p.y+p.footH;y++)for(let x=p.x;x<p.x+p.footW;x++)out.push(y*m.w+x);return out;}
 function distances(m,open,p){return P.distances(open,m.w,m.h,index(m,p.x,p.y),4);}
 function nearRect(x,y,p,r){return x>=p.x-r&&y>=p.y-r&&x<p.x+p.footW+r&&y<p.y+p.footH+r;}
 function clearance(m,open,x,y,w,h,r=0){for(let yy=y-r;yy<y+h+r;yy++)for(let xx=x-r;xx<x+w+r;xx++)if(xx<1||yy<1||xx>=m.w-1||yy>=m.h-1||!open[index(m,xx,yy)])return false;return true;}
 function create(seed,floor=8){
  if(![8,9,10].includes(floor))throw new RangeError('Festival floors are 8–10');
  const hasStalls=floor<10;
  const placementSeed=floor===8?seed:`${seed}:floor${floor}`;
  const failures=[];
  for(let attempt=0;attempt<16;attempt++){
   const rng=G.random(`${placementSeed}:festival130:${attempt}`),profile={courts:6,wideChance:.72,extraLinks:1.1,avenues:3,minRoomWidth:6,minRoomHeight:5};
   let source;try{source=G.generate(`${seed}:festival${floor}:${attempt}`,80,70,'floor',profile);}catch(e){failures.push(e.message);continue;}
   const m={seed:String(seed),floor,w:80,h:70,attempt,cells:Uint8Array.from(source.cells,c=>c===0?0:1),rooms:source.rooms,structures:[],loose:[],lanterns:[],doors:[],stairs:[],enemies:[],items:[],source:'browser StreetGen, shared festival profile'};
   let open=Uint8Array.from(m.cells,c=>c===1?1:0);
   const stageType=floor===10?'collapsed-yagura':'yagura';
   const plaza=[];for(let y=5;y<m.h-9;y++)for(let x=5;x<m.w-9;x++)if(clearance(m,open,x,y,3,3,2))plaza.push({x,y,footW:3,footH:3,type:stageType,kind:'prop'});
   if(!plaza.length){failures.push('no-plaza');continue;}
   shuffle(plaza,rng);plaza.sort((a,b)=>Math.hypot(a.x-m.w/2,a.y-m.h/2)-Math.hypot(b.x-m.w/2,b.y-m.h/2));
   const stage=plaza[Math.floor(rng()*Math.min(16,plaza.length))];m.stage=stage;m.structures.push(stage);for(const i of rectCells(m,stage))open[i]=0;
   if(hasStalls){
    const booths=[];
    for(let y=3;y<m.h-6;y++)for(let x=3;x<m.w-6;x++){
     let valid=true;
     for(let dy=-1;dy<2;dy++)for(let dx=0;dx<3;dx++)if(m.cells[index(m,x+dx,y+dy)]!==0)valid=false;
     if(!valid||!clearance(m,open,x-1,y+2,5,3))continue;
     booths.push({x,y,footW:3,footH:2,kind:'stall',rank:Math.hypot(x-stage.x,y-stage.y)+rng()*14});
    }
    booths.sort((a,b)=>a.rank-b.rank);
    const order=shuffle([...stallTypes],rng),target=5+Math.floor(rng()*3);
    let placed=0;
    for(const p of booths){
     if(placed>=target)break;
     if(m.structures.some(q=>cheb(p,q)<7))continue;
     const pick={...p,type:order[placed]};
     delete pick.rank;
     m.structures.push(pick);
     for(const i of rectCells(m,pick)){m.cells[i]=1;open[i]=0;}
     placed++;
    }
    if(placed<5){failures.push('not-enough-wall-bays');continue;}
   }
   const apron=m.structures.map(p=>({x:p.x-1,y:p.y-1,w:p.footW+2,h:p.footH+4}));
   const arrivals=[];for(let y=2;y<m.h-2;y++)for(let x=2;x<m.w-2;x++)if(clearance(m,open,x,y,1,1,1)&&!m.structures.some(p=>nearRect(x,y,p,4)))arrivals.push({x,y});
   if(arrivals.length<6){failures.push('not-enough-stair-sites');continue;}
   arrivals.sort((a,b)=>Math.abs(a.x-source.start.x)+Math.abs(a.y-source.start.y)-Math.abs(b.x-source.start.x)-Math.abs(b.y-source.start.y));
   m.stairs.push({...arrivals[0],kind:'up'});let fields=[distances(m,open,m.stairs[0])];
   for(let n=1;n<6;n++){
    let best=null,bestScore=-1;for(const p of arrivals){if(m.stairs.some(q=>cheb(p,q)<9))continue;const i=index(m,p.x,p.y),score=Math.min(...fields.map(f=>f[i]))+rng()*.2;if(score>bestScore){best=p;bestScore=score;}}
    if(!best||bestScore<15)break;m.stairs.push({...best,kind:n%2?'down':'up'});fields.push(distances(m,open,best));
   }
   if(m.stairs.length!==6){failures.push('stair-spacing');continue;}m.start={x:m.stairs[0].x,y:m.stairs[0].y};m.exit={...m.stairs[1]};
   const doorSites=[];for(let y=2;y<m.h-2;y++)for(let x=2;x<m.w-2;x++){
    if(!open[index(m,x,y)]||m.stairs.some(p=>cheb({x,y},p)<4)||m.structures.some(p=>nearRect(x,y,p,3)))continue;
    const isWall=(xx,yy)=>m.cells[index(m,xx,yy)]===0,pass=(xx,yy)=>open[index(m,xx,yy)]===1;
    if((isWall(x-1,y)&&isWall(x+1,y)&&pass(x,y-1)&&pass(x,y+1))||(isWall(x,y-1)&&isWall(x,y+1)&&pass(x-1,y)&&pass(x+1,y)))doorSites.push({x,y});
   }
   shuffle(doorSites,rng);for(const p of doorSites)if(m.doors.length<16&&m.doors.every(q=>cheb(p,q)>=5))m.doors.push({...p,id:m.doors.length});
   const specials=[...m.stairs.map(p=>({...p,radius:3})),...m.doors.map(p=>({...p,radius:2}))];
   const safe=P.create({w:m.w,h:m.h,open,specials,excluded:apron,seed:`${placementSeed}:loose:${attempt}`,mode:4});
   const looseTypes=[['festival-cart',2,2],['mask-rack',2,1],['bench',2,1],['nobori',1,1],['taiko',1,1],['bench',2,1],['mask-rack',2,1],['nobori',1,1],['taiko',1,1],['bench',2,1],['nobori',1,1]];
   const wallSites=[];for(let y=2;y<m.h-2;y++)for(let x=2;x<m.w-2;x++)if(open[index(m,x,y)]&&C.some(([dx,dy])=>m.cells[index(m,x+dx,y+dy)]===0))wallSites.push({x,y,rank:Math.hypot(x-stage.x,y-stage.y)+rng()*35});wallSites.sort((a,b)=>a.rank-b.rank);
   if(!wallSites.length){failures.push('no-loose-bays');continue;}
   let requested;
   if(hasStalls){
    requested=looseTypes.map(([type,footW,footH],n)=>({...wallSites[Math.min(wallSites.length-1,n*9)],type,footW,footH,kind:'prop'}));
   }else{
    // Scatter collapsed stalls and smaller remnants in safe wall-side bays.
    shuffle(wallSites,rng);
    const stallOrder=shuffle([...stallTypes],rng);
    const stallCount=5+Math.floor(rng()*3);
    const debrisOrder=shuffle([...debris],rng);
    const count=14+Math.floor(rng()*5);
    requested=stallOrder.slice(0,stallCount).map((type,n)=>{
     const {x,y}=wallSites[n%wallSites.length];
     return {x,y,type,footW:3,footH:1,kind:'broken-stall'};
    });
    requested.push(...Array.from({length:count},(_,n)=>{
     const {id,footW,footH}=debrisOrder[n%debrisOrder.length];
     const {x,y}=wallSites[(n+stallCount)%wallSites.length];
     return {x,y,type:id,footW,footH,kind:'debris'};
    }));
   }
   for(const p of requested)delete p.rank;
   const plan=safe.place(requested);
   const required=hasStalls?['festival-cart','mask-rack','bench','nobori','taiko']:debris.map(p=>p.id);
   const enoughRubble=hasStalls||(plan.placed.filter(p=>p.kind==='broken-stall').length>=5&&plan.placed.filter(p=>p.kind==='debris').length>=12);
   if(!required.every(type=>plan.placed.some(p=>p.type===type))||!enoughRubble){
    failures.push('missing-safe-props');continue;
   }
   m.loose=plan.placed;m.omitted=plan.omitted;m.placementAudit=plan.audit;m.protectedCells=plan.protectedCells;m.baselineOpen=open.slice();
   m.open=open.slice();for(const i of plan.blocked)m.open[i]=0;
   const usedWall=new Set(),lanternSites=[];for(let y=2;y<m.h-2;y++)for(let x=2;x<m.w-5;x++){
    if(![0,1,2,3].every(dx=>m.cells[index(m,x+dx,y)]===0&&m.cells[index(m,x+dx,y+1)]===1))continue;
    if(m.stairs.some(p=>cheb({x:x+1,y},p)<4)||m.doors.some(p=>cheb({x:x+1,y},p)<4))continue;
    if(m.structures.some(p=>p.kind==='stall'&&y===p.y-1&&x<p.x+p.footW&&x+4>p.x))continue;
    lanternSites.push({x,y,type:'lantern-string',kind:'wall'});
   }
   shuffle(lanternSites,rng);lanternSites.sort((a,b)=>Math.hypot(a.x-stage.x,a.y-stage.y)-Math.hypot(b.x-stage.x,b.y-stage.y));
   const lanternLimit=hasStalls?12:3;
   for(const p of lanternSites){if(m.lanterns.length>=lanternLimit)break;const ids=Array.from({length:4},(_,dx)=>index(m,p.x+dx,p.y));if(ids.some(i=>usedWall.has(i)))continue;ids.forEach(i=>usedWall.add(i));m.lanterns.push(p);}
   if(!m.lanterns.length){failures.push('no-lantern-wall');continue;}
   const origin=distances(m,m.open,m.start),free=m.open.reduce((a,b)=>a+b,0);if(origin.reduce((a,b)=>a+(b>=0),0)!==free){failures.push('final-disconnected');continue;}
   m.floorTiles=free;m.stairDistance=origin[index(m,m.exit.x,m.exit.y)];m.generatorAttempts=attempt+1;m.failures=failures;
   const stageFront={x:stage.x+1,y:stage.y+3};m.plazaFocus=stageFront;
   m.walkStart=m.open[index(m,stageFront.x,stageFront.y)]?stageFront:m.start;
   m.validation={connected:true,border:true,allSevenPropTypes:hasStalls,stairs:6,stage:1,loosePlacement:plan.audit};return m;
  }
  throw Error('Could not create a safe festival map: '+failures.join(', '));
 }
 const api={generate:create,distances,rectCells,shuffle};root.FestivalGen130=api;if(native)module.exports=api;
})(globalThis);
