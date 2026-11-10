(function(root){'use strict';
const W=23,H=21,OX=4,OY=3,dirs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
function generate(mode='standalone'){
 const inside=new Set(),shell=new Set(),key=(x,y)=>x+','+y;
 const rect=(x,y,w,h)=>{for(let j=y;j<y+h;j++)for(let i=x;i<x+w;i++)inside.add(key(i,j));};
 rect(6,1,3,5);rect(1,3,4,3);rect(10,3,4,3);rect(3,6,9,3);rect(1,9,4,3);rect(10,9,4,3);rect(6,9,3,5);
 for(const p of inside){const [x,y]=p.split(',').map(Number);for(const [dx,dy] of dirs)if(!inside.has(key(x+dx,y+dy)))shell.add(key(x+dx,y+dy));}
 const cells=new Array(W*H).fill(1),building=new Array(W*H).fill(false),inner=new Array(W*H).fill(false);
 if(mode==='attached')for(let y=0;y<=OY;y++)for(let x=0;x<W;x++)cells[y*W+x]=0;
 for(const p of shell){const [x,y]=p.split(',').map(Number);cells[(y+OY)*W+x+OX]=0;building[(y+OY)*W+x+OX]=true;}
 for(const p of inside){const [x,y]=p.split(',').map(Number);cells[(y+OY)*W+x+OX]=1;inner[(y+OY)*W+x+OX]=true;}
 const gates=[{x:7,y:5},{x:3,y:5},{x:11,y:5},{x:3,y:9},{x:11,y:9}].map(p=>({x:p.x+OX,y:p.y+OY}));
 const bars=[];for(const [x,y,w]of [[6,5,3],[1,5,4],[10,5,4],[1,9,4],[10,9,4]])for(let i=x;i<x+w;i++)if(!gates.some(g=>g.x===i+OX&&g.y===y+OY))bars.push({x:i+OX,y:y+OY});
 const props=[{id:'shiori',label:'시오리 · 금서 보관실',x:1,y:3,w:2,h:2,drawW:32,drawH:32},{id:'bijou',label:'비쥬 · 보석 수용실',x:7,y:2,w:1,h:2,drawW:20,drawH:40},{id:'nerissa',label:'네리사 · 음향 격리실',x:12,y:3,w:1,h:2,drawW:20,drawH:40},{id:'fuwawa',label:'후와와 · 파란 경비실',x:1,y:10,w:2,h:2,drawW:28,drawH:28},{id:'mococo',label:'모코코 · 분홍 경비실',x:12,y:10,w:2,h:2,drawW:28,drawH:28}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 const furniture=[{id:'cot',x:4,y:3,w:1,h:2},{id:'cot',x:6,y:2,w:1,h:2},{id:'cot',x:13,y:3,w:1,h:2},{id:'cot',x:4,y:10,w:1,h:2},{id:'cot',x:10,y:10,w:1,h:2},{id:'locker',x:6,y:1,w:1,h:1},{id:'locker',x:10,y:3,w:1,h:1},{id:'locker',x:8,y:10,w:1,h:1}].map(p=>({...p,x:p.x+OX,y:p.y+OY}));
 const entry={x:7+OX,y:14+OY};cells[entry.y*W+entry.x]=1;const open=cells.slice();
 for(const p of bars)open[p.y*W+p.x]=0;
 for(const p of [...props,...furniture])for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++)open[y*W+x]=0;
 const counter={x:6+OX,y:11+OY,w:1,h:2};for(let y=counter.y;y<counter.y+2;y++)open[y*W+counter.x]=0;
 return{w:W,h:H,mode,cells,building,inner,open,props,furniture,bars,gates,entry,counter,start:{x:entry.x,y:entry.y+2},origin:{x:OX,y:OY,w:15,h:15}};
}
function distances(m,start){const a=new Array(m.w*m.h).fill(-1),todo=[start];a[start.y*m.w+start.x]=0;for(let i=0;i<todo.length;i++){const p=todo[i];for(const [dx,dy]of [[0,-1],[1,0],[0,1],[-1,0]]){const x=p.x+dx,y=p.y+dy,n=y*m.w+x;if(x<0||y<0||x>=m.w||y>=m.h||!m.open[n]||a[n]>=0)continue;a[n]=a[p.y*m.w+p.x]+1;todo.push({x,y});}}return a;}
root.AdventLayout177={generate,distances,dirs};
})(globalThis);
