(function(root){
 'use strict';
 const node=typeof module!=='undefined'&&module.exports;
 const base=node?require('./market-generator.js'):root.MarketGen,G=node?require('./generator.js'):root.StreetGen;
 const sizes={'acrylic-rack':[2,1],'shirt-stack':[2,1],'hoodie-rack':[2,1],'plush-basket':[2,1],'poster-rolls':[1,1],'keychain-hooks':[1,1],'badge-trays':[2,1],'shopping-bags':[1,1],'delivery-boxes':[1,1],'open-carton':[2,1],'delivery-cart':[1,1],'folding-crates':[2,1],'trash-bags':[1,1],'paper-rubbish':[2,1],'recycling-bins':[2,1]};
 function generate(seed,floor,exitMode='auto',compact=false){
  const m=base.generate(seed,floor,exitMode);if(compact){m.compact112=true;return m;}
  const old=m.marketProps.map(p=>({...p})),random=G.random(`${seed}:multicell115:${floor}`);
  for(const p of old)m.cells[p.y*m.w+p.x]=G.FLOOR;
  m.marketProps=[];
  const free=(x,y)=>x>0&&y>0&&x<m.w-1&&y<m.h-1&&m.cells[y*m.w+x]===G.FLOOR;
  const limit=Math.max(9,Math.ceil(old.length*.66));
  for(const p of old){
   if(m.marketProps.length>=limit)break;
   const preferred=sizes[p.type],options=[preferred];if(preferred[1]===2)options.push([2,1]);if(preferred[0]===2)options.push([1,1]);
   let placed=false;
   for(const[w,h]of options){
    // Try a nearby legal anchor rather than stretching across a wall or route.
    const anchors=[{x:p.x,y:p.y},{x:p.x-1,y:p.y},{x:p.x,y:p.y+1}];
    if(random()<.5)anchors.reverse();
    for(const a of anchors){const occupied=[];let ok=true;
     for(let dy=0;dy<h;dy++)for(let dx=0;dx<w;dx++){const x=a.x+dx,y=a.y+dy;if(!free(x,y)||[m.start,m.upstairs,m.exit].some(q=>Math.max(Math.abs(x-q.x),Math.abs(y-q.y))<3))ok=false;occupied.push(y*m.w+x);}
     if(!ok)continue;
     if(m.marketProps.some(q=>a.x<=q.x+q.footW&&a.x+w>=q.x&&a.y<=q.y+q.footH&&a.y+h>=q.y))continue;
     for(const i of occupied)m.cells[i]=G.BARRIER;
     if(!G.validate(m).ok){for(const i of occupied)m.cells[i]=G.FLOOR;continue;}
     m.marketProps.push({...p,x:a.x,y:a.y,footW:w,footH:h});placed=true;break;
    }
    if(placed)break;
   }
  }
  m.decoratedCells=m.cells.slice();m.validation=G.validate(m);m.path=G.route(m,m.start,m.exit);m.multicell115=true;
  if(!m.validation.ok)throw Error('Multi-cell furniture disconnected map');return m;
 }
 const api={...base,generate,footprints:sizes};root.MarketGen=api;if(node)module.exports=api;
})(typeof globalThis!=='undefined'?globalThis:this);
