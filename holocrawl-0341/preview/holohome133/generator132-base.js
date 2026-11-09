(function(root){'use strict';const native=typeof module!=='undefined'&&module.exports,G=native?require('../city-market124/generator.js'):root.StreetGen;
 const neighbours=[[1,0],[-1,0],[0,1],[0,-1]],idx=(m,x,y)=>y*m.w+x,cheb=(a,b)=>Math.max(Math.abs(a.x-b.x),Math.abs(a.y-b.y));
 function distances(m,from,open=m.open){const d=new Int32Array(m.w*m.h).fill(-1),q=[idx(m,from.x,from.y)];d[q[0]]=0;for(let n=0;n<q.length;n++){const i=q[n],x=i%m.w,y=(i/m.w)|0;for(const[dx,dy]of neighbours){const xx=x+dx,yy=y+dy,j=idx(m,xx,yy);if(xx>=0&&yy>=0&&xx<m.w&&yy<m.h&&open[j]&&d[j]<0){d[j]=d[i]+1;q.push(j);}}}return d;}
 function isHome(m,x,y){const h=m.home;return Boolean(h&&x>=h.x&&y>=h.y&&x<h.x+h.w&&y<h.y+h.h);}
 function generate(seed,floor=1){for(let attempt=0;attempt<24;attempt++){
  const r=G.random(`${seed}:home132:${floor}:${attempt}`),int=(a,b)=>a+Math.floor(r()*(b-a+1)),source=G.generate(`${seed}:street132:${floor}:${attempt}`,80,70,'floor',{courts:3,wideChance:.56,extraLinks:.9});
  const m={seed:String(seed),floor,attempt,w:80,h:70,cells:Uint8Array.from(source.cells,c=>c===0?0:1),home:null,props:[],doors:[],stairs:[],enemies:[],items:[],generation:'browser StreetGen plus guaranteed HoloHome132; not native engine'};
  if(floor===1){const h={id:'holohome',x:int(5,58),y:int(5,51),w:17,h:13};m.home=h;const set=(x,y,c)=>m.cells[idx(m,h.x+x,h.y+y)]=c;
   // A two-cell exterior apron reroutes any old passages around the reserved shell.
   for(let y=-2;y<h.h+2;y++)for(let x=-2;x<h.w+2;x++)set(x,y,1);
   for(let y=0;y<h.h;y++)for(let x=0;x<h.w;x++)set(x,y,x===0||y===0||x===h.w-1||y===h.h-1?0:1);
   for(let y=1;y<=7;y++)set(10,y,0);for(let x=10;x<=15;x++)set(x,7,0);
   for(const p of [{x:10,y:5},{x:12,y:7},{x:8,y:12}]){set(p.x,p.y,1);m.doors.push({id:'home-'+p.x+'-'+p.y,x:h.x+p.x,y:h.y+p.y,home:true,entrance:p.y===12});}
   m.props=[{type:'sofa',x:h.x+2,y:h.y+2,w:2,h:1},{type:'sofa',x:h.x+6,y:h.y+2,w:2,h:1},{type:'table',x:h.x+3,y:h.y+5,w:3,h:2},{type:'table',x:h.x+12,y:h.y+9,w:3,h:2}];
   m.stairs.push({id:'down-0',kind:'down',pair:0,x:h.x+13,y:h.y+3,home:true});m.entrance={x:h.x+8,y:h.y+12};m.homeFocus={x:h.x+8,y:h.y+6};
  }
  m.open=Uint8Array.from(m.cells,c=>c===1?1:0);for(const p of m.props)for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++)m.open[idx(m,x,y)]=0;
  const sites=[];for(let y=3;y<m.h-3;y++)for(let x=3;x<m.w-3;x++){
   if(m.home&&x>=m.home.x-3&&x<m.home.x+m.home.w+3&&y>=m.home.y-3&&y<m.home.y+m.home.h+3)continue;let valid=true;for(let yy=y-1;yy<=y+1;yy++)for(let xx=x-1;xx<=x+1;xx++)if(!m.open[idx(m,xx,yy)])valid=false;if(valid)sites.push({x,y});
  }
  if(!sites.length)continue;
  if(m.home){sites.sort((a,b)=>cheb(a,m.entrance)-cheb(b,m.entrance));m.start={...sites[Math.floor(r()*Math.min(sites.length,12))]};}else m.start={...sites[Math.floor(r()*sites.length)]};
  m.stairs.push({...m.start,id:'up-0',kind:'up',pair:0});const kinds=m.home?['down','up','down','up']:['down','up','down','up','down'];
  for(const kind of kinds){const fields=m.stairs.map(p=>distances(m,p));let best=null,score=-1;for(const p of sites){if(m.stairs.some(q=>cheb(p,q)<9))continue;const j=idx(m,p.x,p.y),s=Math.min(...fields.map(d=>d[j]))+r()*.01;if(s>score){score=s;best=p;}}if(!best||score<15)break;const pair=m.stairs.filter(s=>s.kind===kind).length;m.stairs.push({...best,id:kind+'-'+pair,kind,pair});}
  if(m.stairs.length!==6)continue;const all=distances(m,m.start);if(all.filter(d=>d>=0).length!==m.open.reduce((a,b)=>a+b,0))continue;
  const doorSites=[];for(let y=2;y<m.h-2;y++)for(let x=2;x<m.w-2;x++)if(!isHome(m,x,y)&&m.open[idx(m,x,y)]&&!m.stairs.some(p=>cheb({x,y},p)<3)){const wall=(xx,yy)=>m.cells[idx(m,xx,yy)]===0,pass=(xx,yy)=>m.open[idx(m,xx,yy)];if((wall(x-1,y)&&wall(x+1,y)&&pass(x,y-1)&&pass(x,y+1))||(wall(x,y-1)&&wall(x,y+1)&&pass(x-1,y)&&pass(x+1,y)))doorSites.push({x,y});}
  for(let i=doorSites.length-1;i>0;i--){const j=int(0,i);[doorSites[i],doorSites[j]]=[doorSites[j],doorSites[i]];}for(const p of doorSites)if(m.doors.length<18&&m.doors.every(q=>cheb(p,q)>=5))m.doors.push({...p,id:'street-'+m.doors.length,home:false});
  m.homeStair=m.stairs.find(s=>s.home)||null;m.walkable=all.filter(d=>d>=0).length;m.homeDistance=m.homeStair?all[idx(m,m.homeStair.x,m.homeStair.y)]:null;m.validation={connected:true,guaranteedHome:floor===1,homeDownstairs:floor===1?1:0,ordinaryDownstairs:floor===1?2:3,stairs:6};return m;
 }throw Error('Could not generate connected HoloHome floor');}
 const api={generate,distances,isHome};root.HoloHomeGen132=api;if(native)module.exports=api;
})(globalThis);
