const fs=require('fs'),path=require('path');const P=path.resolve(__dirname,'../preview'),D=path.join(P,'facility-shapes172');fs.mkdirSync(path.join(D,'assets'),{recursive:true});
const prior=JSON.parse(fs.readFileSync(path.join(P,'facility-placement171/catalog.json'),'utf8'));
const plans={
 home:{name:'현관이 돌출된 라운지',rects:[[4,10,8,10],[5,11,7,11]],entry:[6,12],sample:[8,3]},
 holox:{name:'양옆 실험실이 돌출된 십자형',rects:[[-1,3,0,5],[8,2,9,4],[5,8,7,9]],entry:[6,10],sample:[6,6]},
 theater:{name:'뒤가 넓고 앞이 좁은 공연장',rects:[[2,7,5,7],[2,8,4,8]],entry:[3,9],sample:[5,6]},
 dining:{name:'주방 날개와 입구가 꺾인 식당',rects:[[-1,2,0,4],[5,8,7,8]],entry:[6,9],sample:[3,4]},
 gamers:{name:'긴 승강장 날개와 진입 통로',rects:[[-1,2,0,6],[5,8,7,9]],entry:[6,10],sample:[3,5]},
 fantasy:{name:'모서리가 꺾인 팔각 운동장',rects:[[0,2,0,6],[8,2,8,6],[2,0,6,0],[2,8,6,8]],entry:[6,9],sample:[2,1]},
 wheel:{name:'중앙이 넓은 관람차 광장',rects:[[0,3,0,5],[8,3,8,5],[4,8,7,8]],entry:[6,9],sample:[1,1]},
 market:{name:'후면 창고와 옆 하역부가 꺾인 마트',rects:[[-1,1,0,3],[8,5,9,6],[5,8,7,8]],entry:[6,9],sample:[5,7]},
 mountain:{name:'좌우로 엇갈린 암벽 쉼터',rects:[[0,2,0,3],[8,4,8,5],[5,8,7,8]],entry:[6,9],sample:[6,6]},
 dev:{name:'좌우 방송 부스와 앞쪽 무대 로비',rects:[[0,1,0,2],[8,1,8,2],[2,8,7,8],[5,9,7,9]],entry:[6,10],sample:[3,3]}
};
const cards=prior.cards.map(f=>{if(!plans[f.id])return{...f,shapeName:'기존 확정 형태 유지'};const plan=plans[f.id],set=new Set();for(let y=0;y<f.h;y++)for(let x=0;x<f.w;x++)if(f.inside[y*f.w+x])set.add(x+','+y);for(const[a,b,c,d]of plan.rects)for(let y=b;y<=d;y++)for(let x=a;x<=c;x++)set.add(x+','+y);const boundary=new Set();for(const key of set){const[x,y]=key.split(',').map(Number);for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){const k=(x+dx)+','+(y+dy);if(!set.has(k))boundary.add(k);}}
const coords=[...set,...boundary].map(k=>k.split(',').map(Number)),minX=Math.min(...coords.map(p=>p[0])),minY=Math.min(...coords.map(p=>p[1])),maxX=Math.max(...coords.map(p=>p[0])),maxY=Math.max(...coords.map(p=>p[1])),w=maxX-minX+1,h=maxY-minY+1,inside=new Array(w*h).fill(0),open=new Array(w*h).fill(0),rows=Array.from({length:h},()=>new Array(w).fill(' '));for(const key of set){const[x,y]=key.split(',').map(Number),i=(y-minY)*w+x-minX;inside[i]=open[i]=1;rows[y-minY][x-minX]='.';}for(const key of boundary){const[x,y]=key.split(',').map(Number);rows[y-minY][x-minX]=f.id==='fantasy'?'G':'#';}for(let y=0;y<f.h;y++)for(let x=0;x<f.w;x++)if(f.inside[y*f.w+x])open[(y-minY)*w+x-minX]=f.open[y*f.w+x];const entry={x:plan.entry[0]-minX,y:plan.entry[1]-minY};rows[entry.y][entry.x]='.';open[entry.y*w+entry.x]=1;
const doorWidth=f.rows[f.entry.y]?.[f.entry.x]==='+'&&f.rows[f.entry.y]?.[f.entry.x+1]==='+'?2:1;for(let i=1;i<doorWidth;i++){rows[entry.y][entry.x+i]='.';open[entry.y*w+entry.x+i]=1;}return{...f,doorWidth,oldW:f.w,oldH:f.h,sourceInside:f.inside,sourceOpenMap:f.open,oldEntry:f.entry,contentShift:[-minX,-minY],w,h,inside,open,rows:rows.map(r=>r.join('')),entry,shaped:true,fenceField:f.id==='fantasy',shapeName:plan.name,floorSample:plan.sample};});
fs.writeFileSync(path.join(D,'catalog.json'),JSON.stringify({...prior,revision:172,scene:[23,21],scope:'Concept floor plans and field grass boundary review; browser only',cards},null,2)+'\n');
fs.copyFileSync(path.join(P,'facility-placement171/materials171.js'),path.join(D,'materials171.js'));fs.copyFileSync(path.join(P,'facility-placement171/promise-walls171.js'),path.join(D,'promise-walls171.js'));
let html=fs.readFileSync(path.join(P,'facility-placement171/index.html'),'utf8').replaceAll('placements171.js','placements172.js').replace('벽에 붙일 때 / 독립 배치 · 전체12곳','시설별로 꺾인 형태 · 벽붙임 / 독립 배치');html=html.replace('건물의 크기와 내부는 같고, 벽 끝과 모서리는 주변 지형에 맞춰 다시 연결했습니다.','기존 소품과 트랙을 살리고 시설별 측면실·승강장·현관을 돌출시켰습니다. 운동장 잔디와 펜스는 같은 경계를 따릅니다.');fs.writeFileSync(path.join(D,'index.html'),html);
let app=fs.readFileSync(path.join(P,'facility-placement171/placements171.js'),'utf8').replaceAll('FacilityPlacement171','FacilityShapes172').replaceAll('placement171Ready','shapes172Ready').replace('W=19,H=17','W=23,H=21');fs.writeFileSync(path.join(D,'placements172.js'),app);
console.log(JSON.stringify({revision:172,modifiedFloorplans:10,preservedFacilities:['promise','myth'],shapes:cards.map(f=>({id:f.id,w:f.w,h:f.h,name:f.shapeName}))}));

require('child_process').execFileSync('python',[path.join(R,'scripts/patch-facility-shapes172.py')],{stdio:'inherit'});
