(function(root){'use strict';
const W=17,H=15,OX=4,OY=3,dirs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]],catalog=[{id:'candy',facility:'h3ro',name:'h3ro 캔디차',label:'캔디 판매차'},{id:'penlights',facility:'holoro',name:'토코호로로 응원봉 가판대',label:'이동식 응원봉 가판대'},{id:'balloon',facility:'area15',name:'루추추 풍선차',label:'풍선 판매차'}];
function generate(kind='candy',mode='standalone'){
 const item=catalog.find(p=>p.id===kind);if(!item)throw Error('Unknown vendor');const inside=new Set(),shell=new Set(),key=(x,y)=>x+','+y;
 function rect(x,y,w,h){for(let j=y;j<y+h;j++)for(let i=x;i<x+w;i++)inside.add(key(i,j));}
 rect(2,1,5,1);rect(1,2,7,5);rect(2,7,5,1);
 for(const p of inside){const[x,y]=p.split(',').map(Number);for(const[dx,dy]of dirs)if(!inside.has(key(x+dx,y+dy)))shell.add(key(x+dx,y+dy));}
 const cells=new Array(W*H).fill(1),building=new Array(W*H).fill(false),inner=new Array(W*H).fill(false);
 if(mode==='attached')for(let y=0;y<=OY;y++)for(let x=0;x<W;x++)cells[y*W+x]=0;
 for(const p of shell){const[x,y]=p.split(',').map(Number),i=(y+OY)*W+x+OX;cells[i]=0;building[i]=true;}
 for(const p of inside){const[x,y]=p.split(',').map(Number),i=(y+OY)*W+x+OX;cells[i]=1;inner[i]=true;}
 const props=[{id:kind,label:item.label,x:OX+5,y:OY+1,w:2,h:2}],furniture=[{id:'bench',x:OX+2,y:OY+6,w:2,h:1},{id:'planter',x:OX+6,y:OY+5,w:2,h:1}];
 const entry={x:OX+4,y:OY+8},entrances=[entry,{x:OX,y:OY+4},{x:OX+8,y:OY+4}],openings=[{x:entry.x-1,y:entry.y},entry,{x:entry.x+1,y:entry.y},...entrances.slice(1)];
 for(const p of openings)cells[p.y*W+p.x]=1;const open=cells.slice();
 for(const p of [...props,...furniture])for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++)open[y*W+x]=0;
 return{w:W,h:H,kind,mode,item,cells,building,inner,open,props,furniture,entry,entrances,openings,servicePoints:[{id:kind,x:OX+5,y:OY+3}],start:{x:entry.x,y:entry.y+2},origin:{x:OX,y:OY,w:9,h:9}};
}
function distances(m,start){const a=new Array(m.w*m.h).fill(-1),todo=[start];a[start.y*m.w+start.x]=0;for(let i=0;i<todo.length;i++){const p=todo[i];for(const[dx,dy]of [[0,-1],[1,0],[0,1],[-1,0]]){const x=p.x+dx,y=p.y+dy,j=y*m.w+x;if(x<0||y<0||x>=m.w||y>=m.h||!m.open[j]||a[j]>=0)continue;a[j]=a[p.y*m.w+p.x]+1;todo.push({x,y});}}return a;}
root.VendorLayout184={generate,distances,dirs,catalog};
})(globalThis);
