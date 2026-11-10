(function(root){'use strict';
const W=23,H=21,OX=6,OY=5,dirs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
function generate(mode='standalone'){
 const inside=new Set(),shell=new Set(),key=(x,y)=>x+','+y;
 function rect(x,y,w,h){for(let j=y;j<y+h;j++)for(let i=x;i<x+w;i++)inside.add(key(i,j));}
 rect(3,1,5,1);rect(2,2,7,1);rect(1,3,9,5);rect(2,8,7,1);rect(3,9,5,1);
 for(const p of inside){const[x,y]=p.split(',').map(Number);for(const[dx,dy]of dirs)if(!inside.has(key(x+dx,y+dy)))shell.add(key(x+dx,y+dy));}
 const cells=new Array(W*H).fill(1),building=new Array(W*H).fill(false),inner=new Array(W*H).fill(false),high=new Array(W*H).fill(false);
 if(mode==='attached')for(let y=0;y<=OY;y++)for(let x=0;x<W;x++)cells[y*W+x]=0;
 for(const p of shell){const[x,y]=p.split(',').map(Number),i=(y+OY)*W+x+OX;cells[i]=0;building[i]=true;high[i]=mode==='attached'&&y===0;}
 for(const p of inside){const[x,y]=p.split(',').map(Number),i=(y+OY)*W+x+OX;cells[i]=1;inner[i]=true;}
 const props=[{id:'cart',label:'AREA15 · 풍선 판매차',x:6,y:2,w:3,h:3},{id:'risu',label:'리스 · 도토리 풍선',x:3,y:3,w:1,h:1,drawW:28,drawH:28},{id:'moona',label:'무나 · 달 풍선',x:3,y:1,w:1,h:2,drawW:24,drawH:48},{id:'iofi',label:'이오피 · 채색 작업대',x:2,y:4,w:2,h:2,drawW:48,drawH:36}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 const furniture=[{id:'bench',x:4,y:8,w:2,h:1},{id:'bench',x:7,y:8,w:2,h:1},{id:'planter',x:1,y:7,w:2,h:1},{id:'planter',x:8,y:6,w:2,h:1}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 const entry={x:5+OX,y:10+OY},entrances=[entry,{x:OX,y:5+OY},{x:10+OX,y:5+OY}],openings=[];
 for(const p of entrances)for(let k=-1;k<=1;k++)openings.push(p===entry?{x:p.x+k,y:p.y}:{x:p.x,y:p.y+k});
 for(const p of openings)cells[p.y*W+p.x]=1;
 const open=cells.slice();
 for(const p of [...props,...furniture])for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++)open[y*W+x]=0;
 const servicePoints=[{id:'cart',x:7,y:5},{id:'risu',x:4,y:3},{id:'moona',x:4,y:2},{id:'iofi',x:4,y:5}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 return{w:W,h:H,mode,cells,building,inner,high,open,props,furniture,entry,entrances,openings,servicePoints,start:{x:entry.x,y:entry.y+2},origin:{x:OX,y:OY,w:11,h:11}};
}
function distances(m,start){const a=new Array(m.w*m.h).fill(-1),todo=[start];a[start.y*m.w+start.x]=0;for(let i=0;i<todo.length;i++){const p=todo[i];for(const[dx,dy]of [[0,-1],[1,0],[0,1],[-1,0]]){const x=p.x+dx,y=p.y+dy,j=y*m.w+x;if(x<0||y<0||x>=m.w||y>=m.h||!m.open[j]||a[j]>=0)continue;a[j]=a[p.y*m.w+p.x]+1;todo.push({x,y});}}return a;}
root.AreaLayout179={generate,distances,dirs};
})(globalThis);
