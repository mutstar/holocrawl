(function(root){'use strict';
const W=23,H=23,OX=4,OY=4,dirs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
function generate(mode='standalone'){
 const inside=new Set(),shell=new Set(),key=(x,y)=>x+','+y;
 function rect(x,y,w,h){for(let j=y;j<y+h;j++)for(let i=x;i<x+w;i++)inside.add(key(i,j));}
 rect(4,1,7,1);rect(2,2,11,2);rect(1,4,13,7);rect(2,11,11,2);rect(4,13,7,1);
 for(const p of inside){const[x,y]=p.split(',').map(Number);for(const[dx,dy]of dirs)if(!inside.has(key(x+dx,y+dy)))shell.add(key(x+dx,y+dy));}
 const cells=new Array(W*H).fill(1),building=new Array(W*H).fill(false),inner=new Array(W*H).fill(false);
 if(mode==='attached')for(let y=0;y<=OY;y++)for(let x=0;x<W;x++)cells[y*W+x]=0;
 for(const p of shell){const[x,y]=p.split(',').map(Number),i=(y+OY)*W+x+OX;cells[i]=0;building[i]=true;}
 for(const p of inside){const[x,y]=p.split(',').map(Number),i=(y+OY)*W+x+OX;cells[i]=1;inner[i]=true;}
 const props=[{id:'candy',label:'캔디 판매차',x:2,y:2,w:2,h:2},{id:'penlights',label:'응원봉 가판대',x:6,y:1,w:2,h:2},{id:'balloon',label:'풍선 판매차',x:11,y:2,w:2,h:2},{id:'fountain',label:'중앙 분수',x:6,y:6,w:3,h:3}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 const furniture=[{id:'bench',x:2,y:7,w:2,h:1},{id:'bench',x:11,y:7,w:2,h:1},{id:'bench',x:4,y:11,w:2,h:1},{id:'bench',x:9,y:11,w:2,h:1},{id:'planter',x:2,y:11,w:2,h:1},{id:'planter',x:11,y:11,w:2,h:1}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 const entry={x:OX+7,y:OY+14},entrances=[entry,{x:OX,y:OY+7},{x:OX+14,y:OY+7}],openings=[];
 for(const p of entrances)for(let k=-1;k<=1;k++)openings.push(p===entry?{x:p.x+k,y:p.y}:{x:p.x,y:p.y+k});
 for(const p of openings)cells[p.y*W+p.x]=1;const open=cells.slice();
 for(const p of [...props,...furniture])for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++)open[y*W+x]=0;
 const servicePoints=[{id:'candy',x:3,y:4},{id:'penlights',x:6,y:3},{id:'balloon',x:11,y:4},{id:'fountain',x:7,y:9}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 return{w:W,h:H,mode,cells,building,inner,open,props,furniture,entry,entrances,openings,servicePoints,start:{x:entry.x,y:entry.y+2},origin:{x:OX,y:OY,w:15,h:15}};
}
function distances(m,start){const a=new Array(m.w*m.h).fill(-1),todo=[start];a[start.y*m.w+start.x]=0;for(let i=0;i<todo.length;i++){const p=todo[i];for(const[dx,dy]of [[0,-1],[1,0],[0,1],[-1,0]]){const x=p.x+dx,y=p.y+dy,j=y*m.w+x;if(x<0||y<0||x>=m.w||y>=m.h||!m.open[j]||a[j]>=0)continue;a[j]=a[p.y*m.w+p.x]+1;todo.push({x,y});}}return a;}
root.FountainLayout185={generate,distances,dirs};
})(globalThis);
