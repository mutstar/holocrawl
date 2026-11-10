(function(root){'use strict';
const W=23,H=21,OX=4,OY=4,dirs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
function generate(mode='standalone'){
 const inside=new Set(),shell=new Set(),key=(x,y)=>x+','+y;
 function rect(x,y,w,h){for(let j=y;j<y+h;j++)for(let i=x;i<x+w;i++)inside.add(key(i,j));}
 rect(1,1,9,9);rect(10,3,4,7);rect(4,10,7,2);
 for(const p of inside){const[x,y]=p.split(',').map(Number);for(const[dx,dy]of dirs)if(!inside.has(key(x+dx,y+dy)))shell.add(key(x+dx,y+dy));}
 const cells=new Array(W*H).fill(1),building=new Array(W*H).fill(false),inner=new Array(W*H).fill(false);
 if(mode==='attached')for(let y=0;y<=OY;y++)for(let x=0;x<W;x++)cells[y*W+x]=0;
 for(const p of shell){const[x,y]=p.split(',').map(Number),i=(y+OY)*W+x+OX;cells[i]=0;building[i]=true;}
 for(const p of inside){const[x,y]=p.split(',').map(Number),i=(y+OY)*W+x+OX;cells[i]=1;inner[i]=true;}
 const props=[{id:'vehicle',label:'h3ro · 보급 차량',x:3,y:2,w:3,h:3},{id:'zeta',label:'제타 · 정보 단말',x:1,y:7,w:2,h:2},{id:'kaela',label:'카엘라 · 모루와 망치',x:12,y:3,w:2,h:2},{id:'kobo',label:'코보 · 빗물 설비',x:12,y:7,w:2,h:2},{id:'maps',label:'탐험용 지도 상자',x:7,y:3,w:1,h:1}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 const furniture=[{id:'tools',x:1,y:1,w:2,h:1},{id:'candy',x:7,y:1,w:2,h:1},{id:'tires',x:9,y:1,w:1,h:1}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 const entry={x:7+OX,y:12+OY},openings=[-1,0,1].map(dx=>({x:entry.x+dx,y:entry.y}));for(const p of openings)cells[p.y*W+p.x]=1;const open=cells.slice();
 for(const p of [...props,...furniture])for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++)open[y*W+x]=0;
 const servicePoints=[{id:'vehicle',x:4,y:5},{id:'zeta',x:3,y:8},{id:'kaela',x:11,y:4},{id:'kobo',x:11,y:8},{id:'maps',x:7,y:4}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 return{w:W,h:H,mode,cells,building,inner,open,props,furniture,entry,openings,servicePoints,start:{x:entry.x,y:entry.y+2},origin:{x:OX,y:OY,w:15,h:13}};
}
function distances(m,start){const a=new Array(m.w*m.h).fill(-1),todo=[start];a[start.y*m.w+start.x]=0;for(let i=0;i<todo.length;i++){const p=todo[i];for(const[dx,dy]of [[0,-1],[1,0],[0,1],[-1,0]]){const x=p.x+dx,y=p.y+dy,j=y*m.w+x;if(x<0||y<0||x>=m.w||y>=m.h||!m.open[j]||a[j]>=0)continue;a[j]=a[p.y*m.w+p.x]+1;todo.push({x,y});}}return a;}
root.H3roLayout183={generate,distances,dirs};
})(globalThis);
