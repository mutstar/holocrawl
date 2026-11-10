(function(){'use strict';
function generate(mode){const m=GreedLayout195.generate(mode),o=m.origin;
 const portrait={id:'portrait',asset:'portrait',label:'시오리 · 초상 진열대',x:o.x+1,y:o.y+4,w:2,h:2};
 const lectern={id:'lectern',label:'금서·깃펜 독서대',x:o.x+10,y:o.y+7,w:1,h:1};m.props.push(portrait);m.furniture.push(lectern);
 for(const p of [portrait,lectern])for(let y=p.y;y<p.y+p.h;y++)for(let x=p.x;x<p.x+p.w;x++)m.open[y*m.w+x]=0;
 m.servicePoints.push({id:'portrait',x:o.x+3,y:o.y+5},{id:'lectern',x:o.x+9,y:o.y+7});return m;
}
window.GreedLayout196={generate,distances:GreedLayout195.distances,dirs:GreedLayout195.dirs};})();
