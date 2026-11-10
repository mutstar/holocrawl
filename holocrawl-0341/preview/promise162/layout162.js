(function(root){'use strict';
const w=15,h=15,origin={x:2,y:1,w:11,h:11},entry={x:7,y:11};
function generate(){const cells=new Uint8Array(w*h).fill(1),inside=(x,y)=>{if(y<=0||y>=10)return false;const inset=Math.max(0,3-y,y-7);return x>inset&&x<10-inset;};for(let ly=0;ly<11;ly++)for(let lx=0;lx<11;lx++){if(inside(lx,ly))continue;let border=false;for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++)if(inside(lx+dx,ly+dy))border=true;if(border)cells[(ly+1)*w+lx+2]=0;}cells[entry.y*w+entry.x]=1;
const props=[{id:'clockwork',label:'중앙 시계장치',x:6,y:5,w:3,h:3},{id:'nature',label:'파우나 · 자연 보관함',x:3,y:4,w:1,h:2},{id:'civilization',label:'무메이 · 기록장',x:11,y:4,w:1,h:2},{id:'chaos',label:'벨즈 · 붉은 조율기',x:4,y:9,w:1,h:1},{id:'hope',label:'아이리스 · 수정 장치',x:10,y:9,w:1,h:1}];
const open=Uint8Array.from(cells);for(const p of props)for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++)open[y*w+x]=0;
return{w,h,origin,entry,doors:[{...entry,id:'promise-entry',home:false}],start:{x:7,y:12},cells,open,props,rewardReserve:{x:7,y:3},policy:{footprint:[11,11],clockwork:[3,3],reviewOnly:true,nativeIntegrated:false}};}
function distances(m,start){const d=new Int32Array(m.w*m.h).fill(-1),i=start.y*m.w+start.x,q=[i];d[i]=0;for(let n=0;n<q.length;n++){const v=q[n],x=v%m.w,y=Math.floor(v/m.w);for(const[dx,dy]of [[0,-1],[1,0],[0,1],[-1,0]]){const xx=x+dx,yy=y+dy,j=yy*m.w+xx;if(xx>=0&&yy>=0&&xx<m.w&&yy<m.h&&m.open[j]&&d[j]<0){d[j]=d[v]+1;q.push(j);}}}return d;}
const api={generate,distances};root.PromiseLayout162=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(globalThis);
