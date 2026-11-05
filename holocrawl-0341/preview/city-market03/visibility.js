(function(root){
'use strict';
const table=root.Crawl0341LOSPaths||(typeof require==='function'?require('./visibility-paths.js'):null);
if(!table)throw new Error('0.34.1 visibility path table is missing');
function compute(w,h,source,opacity,radius=7){
 if(!Number.isInteger(radius)||radius<1||radius>table.maxRadius)throw new Error('Unsupported LOS radius');
 if(source.x<0||source.y<0||source.x>=w||source.y>=h)throw new Error('Invalid viewer position');
 const visible=new Uint8Array(w*h);visible[source.y*w+source.x]=1;
 for(const entry of table.footprints){const[dx,dy]=entry.target;if(Math.max(dx,dy)>radius)continue;
  for(const sx of [1,-1])for(const sy of [1,-1]){const tx=source.x+sx*dx,ty=source.y+sy*dy;if(tx<0||ty<0||tx>=w||ty>=h||visible[ty*w+tx])continue;
   for(const path of entry.paths){let blocked=0;for(let i=0;i<path.length-1;i++){const x=source.x+sx*path[i][0],y=source.y+sy*path[i][1];blocked+=x<0||y<0||x>=w||y>=h?2:opacity(x,y);if(blocked>=2)break;}if(blocked<2){visible[ty*w+tx]=1;break;}}
  }
 }
 return visible;
}
class Memory{
 constructor(w,h){this.w=w;this.h=h;this.visible=new Uint8Array(w*h);this.explored=new Uint8Array(w*h);this.terrain=new Uint8Array(w*h).fill(255);}
 update(cells,source,radius=7){this.visible=compute(this.w,this.h,source,(x,y)=>cells[y*this.w+x]===0?2:0,radius);for(let i=0;i<cells.length;i++)if(this.visible[i]){this.explored[i]=1;this.terrain[i]=cells[i];}return this.visible;}
 renderCells(cells){return Uint8Array.from(cells,(c,i)=>this.visible[i]?c:this.explored[i]?this.terrain[i]:0);}
}
function knownRoute(map,from,to,explored){
 const w=map.w,h=map.h,target=to.y*w+to.x;
 if(to.x<0||to.y<0||to.x>=w||to.y>=h||!explored[target]||map.cells[target]!==1)return[];
 const first=from.y*w+from.x,prev=new Int32Array(w*h).fill(-1),seen=new Uint8Array(w*h),queue=[first];seen[first]=1;
 for(let n=0;n<queue.length&&!seen[target];n++){const i=queue[n],x=i%w,y=Math.floor(i/w);for(const[dx,dy]of [[1,0],[-1,0],[0,1],[0,-1]]){const nx=x+dx,ny=y+dy,j=ny*w+nx;if(nx<0||ny<0||nx>=w||ny>=h||seen[j]||!explored[j]||map.cells[j]!==1)continue;seen[j]=1;prev[j]=i;queue.push(j);}}
 if(!seen[target])return[];const result=[];for(let i=target;i>=0;i=prev[i])result.push({x:i%w,y:Math.floor(i/w)});return result.reverse();
}
const api={compute,Memory,knownRoute,engine:table.engine,defaultRadius:table.defaultRadius};
if(typeof module!=='undefined'&&module.exports)module.exports=api;root.CrawlVisibility=api;
})(typeof globalThis!=='undefined'?globalThis:this);
