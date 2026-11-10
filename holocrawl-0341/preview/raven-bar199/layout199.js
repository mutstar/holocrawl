(function(){'use strict';const W=23,H=21,OX=4,OY=4,dirs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
function generate(mode='standalone'){
 const inside=new Set(),shell=new Set(),key=(x,y)=>x+','+y;const rect=(x,y,w,h)=>{for(let j=y;j<y+h;j++)for(let i=x;i<x+w;i++)inside.add(key(i,j));};rect(1,2,9,6);rect(10,1,3,7);rect(2,8,11,4);
 for(const p of inside){const[x,y]=p.split(',').map(Number);for(const[dx,dy]of dirs)if(!inside.has(key(x+dx,y+dy)))shell.add(key(x+dx,y+dy));}
 const cells=Array(W*H).fill(1),building=Array(W*H).fill(false),inner=Array(W*H).fill(false);if(mode==='attached')for(let y=0;y<=OY;y++)for(let x=0;x<W;x++)cells[y*W+x]=0;
 for(const p of shell){const[x,y]=p.split(',').map(Number),i=(y+OY)*W+x+OX;cells[i]=0;building[i]=true;}for(const p of inside){const[x,y]=p.split(',').map(Number),i=(y+OY)*W+x+OX;cells[i]=1;inner[i]=true;}
 const props=[{id:'counter',asset:'counter',label:'레이븐 · 바 카운터',x:2,y:3,w:4,h:2},{id:'piano',asset:'piano',label:'네리사 · 피아노',x:10,y:2,w:2,h:2},{id:'raven-mic',asset:'raven-mic',label:'까마귀 · 마이크 스탠드',x:12,y:5,w:1,h:2}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 const furniture=[{id:'stool',x:2,y:5,w:1,h:1},{id:'stool',x:4,y:5,w:1,h:1},{id:'stool',x:5,y:5,w:1,h:1},{id:'piano-seat',x:10,y:4,w:1,h:1},{id:'cocktail-left',x:4,y:9,w:1,h:1},{id:'cocktail-right',x:9,y:9,w:1,h:1},{id:'booth',x:2,y:10,w:3,h:1},{id:'booth',x:8,y:10,w:3,h:1}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 const entry={x:6+OX,y:12+OY,w:2,h:1};for(let dx=0;dx<2;dx++)cells[entry.y*W+entry.x+dx]=1;const open=cells.slice();for(const p of [...props,...furniture])for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++)open[y*W+x]=0;
 const servicePoints=[{id:'counter',x:3,y:5},{id:'counter',x:3,y:2},{id:'piano',x:11,y:4},{id:'raven-mic',x:11,y:6},{id:'cocktail-left',x:4,y:8},{id:'cocktail-right',x:9,y:8}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 return{w:W,h:H,mode,cells,building,inner,open,props,furniture,entry,servicePoints,start:{x:entry.x,y:entry.y+2},origin:{x:OX,y:OY,w:15,h:13}};
}
function distances(m,start){const d=Array(W*H).fill(-1),q=[start];d[start.y*W+start.x]=0;for(let i=0;i<q.length;i++)for(const[dx,dy]of [[1,0],[-1,0],[0,1],[0,-1]]){const x=q[i].x+dx,y=q[i].y+dy,j=y*W+x;if(x<0||y<0||x>=W||y>=H||!m.open[j]||d[j]>=0)continue;d[j]=d[q[i].y*W+q[i].x]+1;q.push({x,y});}return d;}
window.RavenLayout199={generate,distances,dirs};})();
