(function(root){'use strict';
const W=21,H=19,OX=4,OY=4,dirs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
function generate(mode='standalone'){
 const inside=new Set(),shell=new Set(),key=(x,y)=>x+','+y;
 function rect(x,y,w,h){for(let j=y;j<y+h;j++)for(let i=x;i<x+w;i++)inside.add(key(i,j));}
 rect(2,1,9,7);rect(1,3,11,4);rect(3,8,7,2);
 for(const p of inside){const[x,y]=p.split(',').map(Number);for(const[dx,dy]of dirs)if(!inside.has(key(x+dx,y+dy)))shell.add(key(x+dx,y+dy));}
 const cells=Array(W*H).fill(1),building=Array(W*H).fill(false),inner=Array(W*H).fill(false);
 if(mode==='attached')for(let y=0;y<=OY;y++)for(let x=0;x<W;x++)cells[y*W+x]=0;
 for(const p of shell){const[x,y]=p.split(',').map(Number),i=(y+OY)*W+x+OX;cells[i]=0;building[i]=true;}
 for(const p of inside){const[x,y]=p.split(',').map(Number),i=(y+OY)*W+x+OX;cells[i]=1;inner[i]=true;}
 const props=[{id:'kong',label:'고릴라 캡슐 머신',x:5,y:2,w:3,h:3},{id:'rack',label:'캡슐 보관대 · 왼쪽',x:2,y:2,w:2,h:1},{id:'rack',label:'캡슐 보관대 · 오른쪽',x:9,y:3,w:2,h:1},{id:'kaela',label:'카엘라 · 모루와 망치',x:10,y:5,w:1,h:1}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 const furniture=[{id:'bench',x:2,y:6,w:2,h:1},{id:'bench',x:9,y:6,w:2,h:1},{id:'counter',x:5,y:8,w:3,h:1}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 const entry={x:OX+6,y:OY+10},openings=[-1,0,1].map(dx=>({x:entry.x+dx,y:entry.y}));for(const p of openings)cells[p.y*W+p.x]=1;
 const open=cells.slice();for(const p of [...props,...furniture])for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++)open[y*W+x]=0;
 const servicePoints=[{id:'kong',x:6,y:5},{id:'rack-left',x:4,y:2},{id:'rack-right',x:8,y:3},{id:'kaela',x:9,y:5},{id:'counter',x:6,y:7}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 return{w:W,h:H,mode,cells,building,inner,open,props,furniture,entry,openings,servicePoints,start:{x:entry.x,y:entry.y+2},origin:{x:OX,y:OY,w:13,h:11}};
}
function walk(m,opened=true){const a=m.open.slice();if(!opened)for(const p of m.openings)a[p.y*m.w+p.x]=0;return a;}
function distances(m,start,opened=true){const open=walk(m,opened),a=Array(m.w*m.h).fill(-1),q=[start];a[start.y*m.w+start.x]=0;for(let i=0;i<q.length;i++){const p=q[i];for(const[dx,dy]of [[0,-1],[1,0],[0,1],[-1,0]]){const x=p.x+dx,y=p.y+dy,j=y*m.w+x;if(x<0||y<0||x>=m.w||y>=m.h||!open[j]||a[j]>=0)continue;a[j]=a[p.y*m.w+p.x]+1;q.push({x,y});}}return a;}
root.KongLayout190={generate,walk,distances,dirs};
})(globalThis);
