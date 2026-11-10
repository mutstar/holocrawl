(function(root){'use strict';const W=29,H=27,OX=4,OY=4,dirs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
function generate(mode='standalone'){
 const inside=new Set(),shell=new Set(),key=(x,y)=>x+','+y;
 function rect(x,y,w,h){for(let j=y;j<y+h;j++)for(let i=x;i<x+w;i++)inside.add(key(i,j));}
 rect(6,1,9,1);rect(3,2,15,2);rect(2,4,17,11);rect(1,6,19,7);rect(3,15,15,2);rect(6,17,9,1);
 for(const p of inside){const[x,y]=p.split(',').map(Number);for(const[dx,dy]of dirs)if(!inside.has(key(x+dx,y+dy)))shell.add(key(x+dx,y+dy));}
 const cells=Array(W*H).fill(1),building=Array(W*H).fill(false),inner=Array(W*H).fill(false);
 if(mode==='attached')for(let y=0;y<=OY;y++)for(let x=0;x<W;x++)cells[y*W+x]=0;
 for(const p of shell){const[x,y]=p.split(',').map(Number),i=(y+OY)*W+x+OX;cells[i]=0;building[i]=true;}
 for(const p of inside){const[x,y]=p.split(',').map(Number),i=(y+OY)*W+x+OX;cells[i]=1;inner[i]=true;}
 const props=[{id:'crane',facility:'robo-crane',label:'로보코 · 로보로보 크레인',x:3,y:2,w:3,h:3},{id:'kong',facility:'capsule-kong',label:'카엘라 · 캡슐 콩',x:9,y:1,w:3,h:3},{id:'onigiri',facility:'onigiri-panic',label:'오카유 · 오니기리 패닉',x:16,y:2,w:2,h:3},{id:'fighting',facility:'korone-fighting',label:'코로네 · 시바키아게 파이팅',x:3,y:12,w:3,h:2},{id:'phoenix',facility:'phoenix-dance',label:'키아라 · 댄스 댄스 피닉스',x:15,y:11,w:3,h:3},{id:'rack',label:'캡슐 보관대',x:13,y:3,w:2,h:1}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 const furniture=[{id:'bench',x:2,y:6,w:2,h:1},{id:'bench',x:17,y:6,w:2,h:1},{id:'bench',x:7,y:15,w:2,h:1},{id:'bench',x:12,y:15,w:2,h:1},{id:'planter',x:2,y:8,w:2,h:1},{id:'planter',x:17,y:8,w:2,h:1}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 const entry={x:OX+10,y:OY+18},entrances=[entry,{x:OX,y:OY+9},{x:OX+20,y:OY+9}],openings=[];
 for(const p of entrances)for(let k=-1;k<=1;k++)openings.push(p===entry?{x:p.x+k,y:p.y}:{x:p.x,y:p.y+k});
 for(const p of openings)cells[p.y*W+p.x]=1;const open=cells.slice();for(const p of [...props,...furniture])for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++)open[y*W+x]=0;
 const servicePoints=[{id:'crane',x:4,y:5},{id:'kong',x:10,y:4},{id:'onigiri',x:17,y:5},{id:'fighting',x:4,y:14},{id:'phoenix',x:16,y:14},{id:'rack',x:14,y:4}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 return{w:W,h:H,mode,cells,building,inner,open,props,furniture,entry,entrances,openings,servicePoints,start:{x:entry.x,y:entry.y+2},origin:{x:OX,y:OY,w:21,h:19}};
}
function distances(m,start){const d=Array(m.w*m.h).fill(-1),q=[start];d[start.y*m.w+start.x]=0;for(let i=0;i<q.length;i++){const p=q[i];for(const[dx,dy]of [[0,-1],[1,0],[0,1],[-1,0]]){const x=p.x+dx,y=p.y+dy,j=y*m.w+x;if(x<0||y<0||x>=m.w||y>=m.h||!m.open[j]||d[j]>=0)continue;d[j]=d[p.y*m.w+p.x]+1;q.push({x,y});}}return d;}
root.ArcadeLayout191={generate,distances,dirs};})(globalThis);
