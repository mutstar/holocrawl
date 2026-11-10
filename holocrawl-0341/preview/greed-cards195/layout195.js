(function(){'use strict';const W=21,H=21,OX=4,OY=4,dirs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
function generate(mode='standalone'){
 const inside=new Set(),shell=new Set(),key=(x,y)=>x+','+y;
 function rect(x,y,w,h){for(let j=y;j<y+h;j++)for(let i=x;i<x+w;i++)inside.add(key(i,j));}
 rect(2,1,9,3);rect(1,4,11,5);rect(2,9,9,3);
 for(const s of inside){const[x,y]=s.split(',').map(Number);for(const[dx,dy]of dirs)if(!inside.has(key(x+dx,y+dy)))shell.add(key(x+dx,y+dy));}
 const cells=Array(W*H).fill(1),building=Array(W*H).fill(false),inner=Array(W*H).fill(false);
 if(mode==='attached')for(let y=0;y<=OY;y++)for(let x=0;x<W;x++)cells[y*W+x]=0;
 for(const s of shell){const[x,y]=s.split(',').map(Number),i=(y+OY)*W+x+OX;cells[i]=0;building[i]=true;}
 for(const s of inside){const[x,y]=s.split(',').map(Number);cells[(y+OY)*W+x+OX]=1;inner[(y+OY)*W+x+OX]=true;}
 const props=[{id:'table',asset:'table',label:'카드 오브 그리드 · 카드 테이블',x:5,y:6,w:3,h:2},{id:'archive-left',asset:'archive',label:'시오리 · 흑백 장서',x:2,y:1,w:2,h:2},{id:'archive-right',asset:'archive',label:'시오리 · 금서 기록대',x:9,y:1,w:2,h:2},{id:'counter',asset:'counter',label:'칩·기록 교환대',x:5,y:2,w:2,h:1}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 const furniture=[{id:'safe',x:8,y:2,w:1,h:1},{id:'chair',x:4,y:6,w:1,h:1},{id:'chair',x:8,y:6,w:1,h:1},{id:'bench',x:2,y:10,w:2,h:1},{id:'bench',x:9,y:10,w:2,h:1}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 const entry={x:6+OX,y:12+OY,w:2,h:1};for(let dx=0;dx<2;dx++)cells[entry.y*W+entry.x+dx]=1;
 const open=cells.slice();for(const p of [...props,...furniture])for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++)open[y*W+x]=0;
 const servicePoints=[{id:'table',x:6,y:5},{id:'table',x:6,y:8},{id:'archive-left',x:3,y:3},{id:'archive-right',x:10,y:3},{id:'counter',x:5,y:3},{id:'safe',x:8,y:3}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 return{w:W,h:H,mode,cells,building,inner,open,props,furniture,entry,servicePoints,start:{x:entry.x,y:entry.y+2},origin:{x:OX,y:OY,w:13,h:13}};
}
function distances(m,start){const d=Array(m.w*m.h).fill(-1),todo=[start];d[start.y*m.w+start.x]=0;for(let i=0;i<todo.length;i++){const p=todo[i];for(const[dx,dy]of [[0,-1],[1,0],[0,1],[-1,0]]){const x=p.x+dx,y=p.y+dy,n=y*m.w+x;if(x<0||y<0||x>=m.w||y>=m.h||!m.open[n]||d[n]>=0)continue;d[n]=d[p.y*m.w+p.x]+1;todo.push({x,y});}}return d;}
window.GreedLayout195={generate,distances,dirs};})();
