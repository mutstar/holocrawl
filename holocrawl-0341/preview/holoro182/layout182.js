(function(root){'use strict';
const W=23,H=21,OX=5,OY=5,dirs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
function generate(mode='standalone'){
 const inside=new Set(),shell=new Set(),key=(x,y)=>x+','+y;
 function rect(x,y,w,h){for(let j=y;j<y+h;j++)for(let i=x;i<x+w;i++)inside.add(key(i,j));}
 rect(1,1,8,7);rect(9,3,3,6);rect(3,8,6,2);
 for(const p of inside){const[x,y]=p.split(',').map(Number);for(const[dx,dy]of dirs)if(!inside.has(key(x+dx,y+dy)))shell.add(key(x+dx,y+dy));}
 const cells=new Array(W*H).fill(1),building=new Array(W*H).fill(false),inner=new Array(W*H).fill(false);
 if(mode==='attached')for(let y=0;y<=OY;y++)for(let x=0;x<W;x++)cells[y*W+x]=0;
 for(const p of shell){const[x,y]=p.split(',').map(Number),i=(y+OY)*W+x+OX;cells[i]=0;building[i]=true;}
 for(const p of inside){const[x,y]=p.split(',').map(Number),i=(y+OY)*W+x+OX;cells[i]=1;inner[i]=true;}
 const props=[{id:'penlights',label:'중앙 · 응원봉 진열대',x:4,y:1,w:3,h:2},{id:'ollie',label:'올리 · 빨간 패치 곰',x:1,y:4,w:2,h:1,drawW:32,drawH:32,fixture:'ollie-counter',anchorBottom:24},{id:'anya',label:'아냐 · 토스터',x:9,y:4,w:2,h:1,drawW:32,drawH:32,fixture:'anya-counter',anchorBottom:24},{id:'reine',label:'레이네 · 공작 깃털 부채',x:8,y:7,w:3,h:1,drawW:32,drawH:32,fixture:'reine-counter',anchorBottom:24}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 const furniture=[{id:'sales-counter',x:4,y:3,w:3,h:1},{id:'ollie-counter',x:1,y:4,w:2,h:2},{id:'anya-counter',x:9,y:4,w:2,h:2},{id:'reine-counter',x:8,y:7,w:3,h:2},{id:'stock',x:1,y:1,w:2,h:1}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 const entry={x:6+OX,y:10+OY};cells[entry.y*W+entry.x]=1;const open=cells.slice();
 for(const p of [...props.filter(p=>!p.fixture),...furniture])for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++)open[y*W+x]=0;
 const servicePoints=[{id:'penlights',x:5,y:4},{id:'ollie',x:3,y:5},{id:'anya',x:10,y:6},{id:'reine',x:8,y:9}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 return{w:W,h:H,mode,cells,building,inner,open,props,furniture,entry,servicePoints,start:{x:entry.x,y:entry.y+2},origin:{x:OX,y:OY,w:13,h:11}};
}
function distances(m,start){const a=new Array(m.w*m.h).fill(-1),todo=[start];a[start.y*m.w+start.x]=0;for(let i=0;i<todo.length;i++){const p=todo[i];for(const[dx,dy]of [[0,-1],[1,0],[0,1],[-1,0]]){const x=p.x+dx,y=p.y+dy,j=y*m.w+x;if(x<0||y<0||x>=m.w||y>=m.h||!m.open[j]||a[j]>=0)continue;a[j]=a[p.y*m.w+p.x]+1;todo.push({x,y});}}return a;}
root.HoloroLayout182={generate,distances,dirs};
})(globalThis);
